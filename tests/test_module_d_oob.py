"""Module D Tier-1 host OOB path: gateway + inspect, always-numeric scores."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from uhbs_core import test_safety
from uhbs_core.models import TargetSpec
from uhbs_core.outcomes import CheckOutcome, ContainmentVerdict


def _clean_inspect(**overrides) -> dict:
    data = {
        "Id": "sha256:deadbeef",
        "Config": {"User": "1000:1000"},
        "HostConfig": {
            "Privileged": False,
            "NetworkMode": "bridge",
            "PidMode": "",
            "IpcMode": "",
            "CapAdd": [],
            "CapDrop": ["ALL"],
            "UsernsMode": "",
            "SecurityOpt": [],
            "Binds": [],
            "Devices": [],
            "Memory": 256 * 1024 * 1024,
            "NanoCpus": 1_000_000_000,
            "PidsLimit": 256,
            "ReadonlyRootfs": True,
        },
        "Mounts": [],
        "RepoDigests": ["example@sha256:abc"],
    }
    for key, val in overrides.items():
        if key in ("Config", "HostConfig") and isinstance(val, dict):
            data[key] = {**data[key], **val}
        else:
            data[key] = val
    return data


def _write_gateway(path: Path, *, hit: bool = False, envelope: bool = True) -> str:
    lines: list[str] = []
    if envelope:
        lines.append(
            json.dumps(
                {
                    "type": "uhbs_gateway_envelope",
                    "uhbs_version": "5.0.1",
                    "uhbs_gateway_envelope": True,
                    "run_id": "test",
                }
            )
        )
    if hit:
        lines.append("2026-01-01T00:00:00Z HIT canary exfil")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _attach_oob(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    hit: bool = False,
    inspect: dict | None = None,
    digest_mismatch: bool = False,
    missing_gateway: bool = False,
    missing_inspect: bool = False,
) -> None:
    if missing_gateway:
        monkeypatch.delenv("UHBS_EGRESS_GATEWAY_LOG", raising=False)
        monkeypatch.delenv("UHBS_EGRESS_GATEWAY_SHA256", raising=False)
    else:
        gw = tmp_path / "egress-gateway.log"
        digest = _write_gateway(gw, hit=hit)
        monkeypatch.setenv("UHBS_EGRESS_GATEWAY_LOG", str(gw))
        monkeypatch.setenv(
            "UHBS_EGRESS_GATEWAY_SHA256",
            "0" * 64 if digest_mismatch else digest,
        )

    if missing_inspect:
        monkeypatch.delenv("UHBS_CONTAINER_INSPECT_JSON", raising=False)
        monkeypatch.delenv("UHBS_CONTAINER_INSPECT_SHA256", raising=False)
    else:
        insp = tmp_path / "container-inspect.json"
        payload = inspect if inspect is not None else _clean_inspect()
        text = json.dumps([payload])
        insp.write_text(text, encoding="utf-8")
        dig = hashlib.sha256(insp.read_bytes()).hexdigest()
        monkeypatch.setenv("UHBS_CONTAINER_INSPECT_JSON", str(insp))
        monkeypatch.setenv(
            "UHBS_CONTAINER_INSPECT_SHA256",
            "0" * 64 if digest_mismatch else dig,
        )


def _http_target() -> TargetSpec:
    return TargetSpec(
        name="http-decoy",
        host="127.0.0.1",
        port=8080,
        protocol="http",
        protocols=["http"],
        ports_map={"http": 8080},
    )


def _ssh_target() -> TargetSpec:
    return TargetSpec(
        name="ssh-decoy",
        host="127.0.0.1",
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": 2222},
        ssh_port=2222,
    )


def test_clean_oob_gate_passed_score_gt_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _attach_oob(monkeypatch, tmp_path)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.GATE_PASSED.value
    assert isinstance(result.score, float)
    assert result.score > 0.0
    assert result.score != 0.0


def test_gateway_hit_gate_failed_numeric(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _attach_oob(monkeypatch, tmp_path, hit=True)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.GATE_FAILED.value
    assert isinstance(result.score, float)
    assert result.score >= 1.0


def test_privileged_inspect_gate_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = _clean_inspect(HostConfig={"Privileged": True})
    _attach_oob(monkeypatch, tmp_path, inspect=bad)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.GATE_FAILED.value
    assert result.score >= 1.0
    assert any(
        c.id == "d2.container_privileged" and c.outcome == CheckOutcome.FAIL
        for c in result.checks
    )


def test_unconfined_seccomp_gate_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = _clean_inspect(HostConfig={"SecurityOpt": ["seccomp=unconfined"]})
    _attach_oob(monkeypatch, tmp_path, inspect=bad)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.GATE_FAILED.value


def test_host_network_and_docker_sock_bind_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = _clean_inspect(
        HostConfig={
            "NetworkMode": "host",
            "Binds": ["/var/run/docker.sock:/var/run/docker.sock"],
        }
    )
    _attach_oob(monkeypatch, tmp_path, inspect=bad)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.GATE_FAILED.value
    ids = {c.id: c for c in result.checks if c.outcome == CheckOutcome.FAIL}
    assert "d2.network_mode" in ids
    assert "d2.sensitive_binds" in ids


def test_missing_evidence_incomplete_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _attach_oob(monkeypatch, tmp_path, missing_gateway=True, missing_inspect=True)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.INCOMPLETE.value
    assert result.score == 1.0
    assert isinstance(result.score, float)


def test_digest_mismatch_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _attach_oob(monkeypatch, tmp_path, digest_mismatch=True)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.INCOMPLETE.value
    assert result.score >= 1.0


def test_inspect_digest_matches_raw_file_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Harness pins use sha256(file bytes); verifier must not re-hash decoded text."""
    from uhbs_core.containment_inspect import load_container_inspect
    from uhbs_core.manifest import sha256_file

    insp = tmp_path / "container-inspect.json"
    # Non-ASCII whitespace-safe UTF-8 that still round-trips as JSON.
    insp.write_bytes(b'[{"Id":"x","Config":{},"HostConfig":{},"State":{}}]')
    dig = sha256_file(insp)
    monkeypatch.setenv("UHBS_CONTAINER_INSPECT_JSON", str(insp))
    monkeypatch.setenv("UHBS_CONTAINER_INSPECT_SHA256", dig)
    data, err = load_container_inspect()
    assert err is None
    assert isinstance(data, dict)


def test_ssh_presence_does_not_change_critical_criteria(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class _Fail:
        ok = False
        stdout = ""
        stderr = ""
        error = "ssh down"

    _attach_oob(monkeypatch, tmp_path)
    monkeypatch.setattr(test_safety, "run_ssh_command", lambda *_a, **_k: _Fail())
    monkeypatch.setattr(test_safety, "run_ssh_shell_commands", lambda *_a, **_k: _Fail())
    http = test_safety.run(_http_target())
    ssh = test_safety.run(_ssh_target())
    assert http.critical_control_verdict == ssh.critical_control_verdict == "GATE_PASSED"
    assert http.score > 0 and ssh.score > 0


def test_undeclared_cap_add_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = _clean_inspect(HostConfig={"CapAdd": ["NET_ADMIN"], "CapDrop": []})
    _attach_oob(monkeypatch, tmp_path, inspect=bad)
    result = test_safety.run(_http_target())
    assert result.critical_control_verdict == ContainmentVerdict.GATE_FAILED.value


def test_mixed_protocol_smoke_always_numeric(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Smoke: HTTP + SSH units share the unified OOB path and never stub-zero."""

    class _Down:
        ok = False
        stdout = ""
        stderr = ""
        error = "n/a"

    _attach_oob(monkeypatch, tmp_path)
    for target in (_http_target(), _ssh_target()):
        monkeypatch.setattr(test_safety, "run_ssh_command", lambda *_a, **_k: _Down())
        monkeypatch.setattr(
            test_safety, "run_ssh_shell_commands", lambda *_a, **_k: _Down()
        )
        result = test_safety.run(target)
        assert isinstance(result.score, (int, float))
        assert result.score > 0.0
        assert result.critical_control_verdict == "GATE_PASSED"
        assert any(c.id == "d1.egress_gateway_log" for c in result.checks)
        assert any(c.id == "d2.container_privileged" for c in result.checks)
