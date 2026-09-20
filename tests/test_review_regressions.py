"""Regression tests for review findings fixed on the v5 assurance branch."""

from __future__ import annotations

from pathlib import Path

import pytest

from uhbs_cli.scoring import assert_scorecard_integrity
from uhbs_core.attack_validate import resolve_technique
from uhbs_core.check_scoring import score_checks
from uhbs_core.evidence_pack import _redact_evidence_text, build_evidence_pack
from uhbs_core.models import CheckOutcome, CheckResult, ModuleResult
from uhbs_core.outcomes import ContainmentVerdict
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.telemetry.formats import validate_stix21
from uhbs_core.telemetry.groundtruth import assess_sink_resilience
from uhbs_core.test_safety import _CANARY_HIT_RE, _gateway_canary_hits, _verdict_from_critical
from uhbs_core.uhqs_math import (
    AssessmentStatus,
    CriticalControlVerdict,
    assessment_from_module_results,
    compute_uhqs,
)


def test_d3_breakout_does_not_override_critical_gate_passed() -> None:
    """Non-critical DiD failures must not flip GATE_PASSED → GATE_FAILED."""
    checks = [
        CheckResult.make(
            id="d1.egress_tcp",
            team="blue",
            outcome=CheckOutcome.PASS,
            score=100.0,
            critical=True,
            catalog_id="D1.critical",
        ),
        CheckResult.make(
            id="d2.runtime_escape_surface",
            team="blue",
            outcome=CheckOutcome.PASS,
            score=100.0,
            critical=True,
            catalog_id="D2.critical",
        ),
        CheckResult.make(
            id="d3.prompt_injection",
            team="red",
            outcome=CheckOutcome.FAIL,
            score=0.0,
            critical=False,
            catalog_id="D3.did",
        ),
    ]
    assert _verdict_from_critical(checks) == ContainmentVerdict.GATE_PASSED


def test_gateway_canary_ignores_hit_substrings(tmp_path: Path, monkeypatch) -> None:
    log = tmp_path / "gw.log"
    log.write_text("WHITE list allowed\nARCHITECT note\n# HIT ignored\n", encoding="utf-8")
    monkeypatch.setenv("UHBS_EGRESS_GATEWAY_LOG", str(log))
    result = _gateway_canary_hits()
    assert result.outcome == CheckOutcome.PASS
    assert _CANARY_HIT_RE.search("CANARY HIT detected") is not None
    assert _CANARY_HIT_RE.search("WHITE list") is None


def test_log_floor_does_not_leak_credit_for_not_tested() -> None:
    checks = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(id="b", team="blue", outcome=CheckOutcome.NOT_TESTED, score=0.0),
    ]
    assert score_checks(checks) < 0.1


def test_stix_id_requires_uuid_shape() -> None:
    ok, detail = validate_stix21(
        {
            "type": "indicator",
            "id": "indicator--not-a-uuid-but-has--dash",
            "spec_version": "2.1",
        }
    )
    assert ok is False
    assert "STIX-shaped" in detail


def test_assessment_from_module_not_tested_status() -> None:
    status, _ = assessment_from_module_results(
        {
            "A": {"score": 80, "status": "NOT_TESTED"},
            "B": {"score": 80, "status": "PASSED"},
            "C": {"score": 80, "status": "PASSED"},
            "D": {"score": 95, "status": "GATE PASSED", "critical_control_verdict": "GATE_PASSED"},
            "E": {"score": 80, "status": "PASSED"},
            "F": {"score": 80, "status": "PASSED"},
        }
    )
    assert status is AssessmentStatus.INCOMPLETE


def test_assessment_skipped_module_with_complete_true_ok() -> None:
    status, verdict = assessment_from_module_results(
        {
            "A": {"score": 80, "status": "PASSED", "complete": True},
            "B": {"score": 80, "status": "PASSED", "complete": True},
            "C": {"score": 80, "status": "PASSED", "complete": True},
            "D": {
                "score": 55,
                "status": "GATE_FAILED",
                "complete": True,
                "critical_control_verdict": "GATE_FAILED",
            },
            "E": {"score": 80, "status": "PASSED", "complete": True},
            "F": {"score": 0, "status": "SKIPPED", "complete": True},
        }
    )
    assert status is AssessmentStatus.COMPLETE
    assert verdict is CriticalControlVerdict.GATE_FAILED


def test_integrity_omitted_uhqs_ok_when_ungraded() -> None:
    from uhbs_core.uhqs_math import SCORING_MODEL_ID

    card = {
        "scoring_model_id": SCORING_MODEL_ID,
        "target": {"class": "POSIX-Shell"},
        "assessment_status": "INCOMPLETE",
        "modules": {
            "A": {"score": 80.0, "status": "INCOMPLETE", "complete": False},
            "B": {"score": 80.0, "status": "PASSED", "complete": True},
            "C": {"score": 80.0, "status": "PASSED", "complete": True},
            "D": {
                "score": 0.0,
                "status": "INCOMPLETE",
                "complete": False,
                "critical_control_verdict": "INCOMPLETE",
            },
            "E": {"score": 80.0, "status": "PASSED", "complete": True},
            "F": {"score": 80.0, "status": "PASSED", "complete": True},
        },
        "containment_measured": False,
        "safety_gate": {
            "delta_c": 0.0,
            "passed": False,
            "critical_control_verdict": "INCOMPLETE",
        },
    }
    # uhqs key intentionally omitted
    errors = assert_scorecard_integrity(card)
    assert errors == []


def test_integrity_rejects_complete_when_modules_incomplete() -> None:
    from uhbs_core.uhqs_math import SCORING_MODEL_ID

    card = {
        "scoring_model_id": SCORING_MODEL_ID,
        "target": {"class": "POSIX-Shell"},
        "assessment_status": "COMPLETE",
        "uhqs": None,
        "modules": {
            "A": {"score": 80.0, "status": "INCOMPLETE", "complete": False},
            "B": {"score": 80.0, "status": "PASSED", "complete": True},
            "C": {"score": 80.0, "status": "PASSED", "complete": True},
            "D": {
                "score": 0.0,
                "status": "INCOMPLETE",
                "complete": False,
                "critical_control_verdict": "INCOMPLETE",
            },
            "E": {"score": 80.0, "status": "PASSED", "complete": True},
            "F": {"score": 80.0, "status": "PASSED", "complete": True},
        },
        "containment_measured": False,
        "safety_gate": {
            "delta_c": 0.0,
            "passed": False,
            "critical_control_verdict": "INCOMPLETE",
        },
    }
    errors = assert_scorecard_integrity(card)
    assert any("COMPLETE" in e and "INCOMPLETE" in e for e in errors)


def test_invalid_verdict_string_fails_closed() -> None:
    result = compute_uhqs(
        {"A": 80, "B": 80, "C": 80, "D": 99, "E": 80, "F": 80},
        profile_class="POSIX-Shell",
        critical_control_verdict="BOGUS",
    )
    assert result.graded is False
    assert result.uhqs is None
    assert result.critical_control_verdict is CriticalControlVerdict.INCOMPLETE


def test_base_stubs_are_optional_not_tested() -> None:
    class _P(ProtocolPlugin):
        name = "stub"

        def probe_fsm(self, host, port, target, tps):
            return []

        def probe_negotiation(self, host, port, target, tps):
            return []

    p = _P()
    state = p.probe_state("h", 1, None, None)  # type: ignore[arg-type]
    payload = p.probe_payload("h", 1, None, None)  # type: ignore[arg-type]
    assert state[0].outcome is CheckOutcome.NOT_TESTED
    assert state[0].mandatory is False
    assert state[0].score == 0.0
    assert payload[0].mandatory is False


def test_c2_requires_current_run_id_markers() -> None:
    # Stale markers from another run must not satisfy resilience.
    records = [{"msg": "UHBS_INJECT:oldrun:ANSI:x"}, {"msg": "UHBS_INJECT:oldrun:JSON:y"}]
    assessment = assess_sink_resilience(records, "newrun", ["ansi", "json_break"])
    assert assessment["ok"] is False


def test_attack_pins_share_primary_techniques() -> None:
    # Primary pin IDs resolve via attack_validate after merge.
    assert resolve_technique("T1071").valid is True
    assert resolve_technique("T0867").valid is True  # legacy-only ID still merged


def test_evidence_redaction_scrubs_secrets() -> None:
    text = _redact_evidence_text("password=hunter2 and token: abcdef")
    assert "hunter2" not in text
    assert "[REDACTED]" in text
    pack = build_evidence_pack(
        modules=[
            ModuleResult(
                module="D",
                dimension="containment",
                score=0.0,
                status="INCOMPLETE",
                checks=[
                    CheckResult(
                        id="d1",
                        team="blue",
                        outcome=CheckOutcome.FAIL,
                        score=0.0,
                        evidence=["Authorization: Bearer supersecret"],
                    )
                ],
            )
        ]
    )
    evidence = pack["modules"][0]["checks"][0]["evidence"][0]
    assert "supersecret" not in evidence


def test_module_d_ssh_failure_is_incomplete_not_gate_passed(
    tmp_path: Path, monkeypatch
) -> None:
    """Unpinned/failed SSH must never be inferred as egress-blocked PASS."""
    from uhbs_core import test_safety
    from uhbs_core.models import TargetSpec

    class _Fail:
        ok = False
        stdout = ""
        stderr = ""
        error = "Server '127.0.0.1' not found in known_hosts"

    target = TargetSpec(
        name="ssh",
        host="127.0.0.1",
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": 2222},
        ssh_port=2222,
    )
    monkeypatch.delenv("UHBS_EGRESS_GATEWAY_LOG", raising=False)
    monkeypatch.setattr(test_safety, "run_ssh_command", lambda *_a, **_k: _Fail())
    monkeypatch.setattr(test_safety, "run_ssh_shell_commands", lambda *_a, **_k: _Fail())
    result = test_safety.run(target)
    assert result.critical_control_verdict == ContainmentVerdict.INCOMPLETE.value
    assert result.complete is False
    assert any(c.outcome == CheckOutcome.ERROR and c.mandatory for c in result.checks)


def test_classify_ssh_algorithms_flags_legacy_offers() -> None:
    from uhbs_core.hassh import classify_ssh_algorithms

    weak = classify_ssh_algorithms(
        "diffie-hellman-group1-sha1,curve25519-sha256;"
        "3des-cbc,aes128-ctr;"
        "hmac-md5,hmac-sha2-256;"
        "none"
    )
    assert "diffie-hellman-group1-sha1" in weak["weak"]
    assert "3des-cbc" in weak["weak"]
    assert "hmac-md5" in weak["weak"]
    # AES-CBC remains widely advertised alongside CTR/GCM — not scored as weak.
    clean_modernish = classify_ssh_algorithms(
        "curve25519-sha256;aes128-cbc,aes128-ctr;hmac-sha2-256;none"
    )
    assert clean_modernish["weak"] == []
    clean = classify_ssh_algorithms(
        "curve25519-sha256;aes128-ctr;hmac-sha2-256;none"
    )
    assert clean["weak"] == []


def test_ssh_nego_weak_algorithms_check_penalizes_legacy_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from uhbs_core.models import TargetSpec
    from uhbs_core.protocols.ssh import SSHPlugin
    from uhbs_core.rfc_probes.types import RFCSuiteResult

    monkeypatch.setattr(
        "uhbs_core.protocols.ssh.probe_ssh_rfc4253",
        lambda *_a, **_k: RFCSuiteResult(protocol="ssh", rfc="RFC 4253"),
    )
    monkeypatch.setattr(
        "uhbs_core.protocols.ssh.parse_server_hassh",
        lambda *_a, **_k: (
            "deadbeef",
            "diffie-hellman-group1-sha1;3des-cbc;hmac-md5;none",
            "SSH-2.0-test",
        ),
    )
    checks = SSHPlugin().probe_negotiation(
        "127.0.0.1", 22, TargetSpec(name="t", host="127.0.0.1"), None
    )
    by_id = {c.id: c for c in checks}
    assert by_id["ssh.nego.hassh"].passed is True
    assert by_id["ssh.nego.hassh"].score == 100.0
    weak = by_id["ssh.nego.weak_algorithms"]
    assert weak.passed is False
    assert weak.score < 100.0


def test_module_d_keeps_gateway_mandatory_when_ssh_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from uhbs_core import test_safety
    from uhbs_core.models import TargetSpec

    class _Fail:
        ok = False
        stdout = ""
        stderr = ""
        error = "Server not found in known_hosts"

    target = TargetSpec(
        name="ssh",
        host="127.0.0.1",
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": 2222},
        ssh_port=2222,
    )
    monkeypatch.delenv("UHBS_EGRESS_GATEWAY_LOG", raising=False)
    monkeypatch.setattr(test_safety, "run_ssh_command", lambda *_a, **_k: _Fail())
    monkeypatch.setattr(test_safety, "run_ssh_shell_commands", lambda *_a, **_k: _Fail())
    result = test_safety.run(target)
    gw = next(c for c in result.checks if c.id == "d1.egress_gateway_log")
    assert gw.outcome == CheckOutcome.NOT_TESTED
    assert gw.mandatory is True


def test_inventory_loads_ssh_known_hosts(tmp_path: Path) -> None:
    from uhbs_core.inventory import load_inventory

    inv = tmp_path / "inv.yaml"
    kh = tmp_path / "known_hosts"
    kh.write_text("host key line\n", encoding="utf-8")
    inv.write_text(
        f"""
sites:
  lab:
    host: 127.0.0.1
    protocol: ssh
    ports: {{ssh: 2222}}
    ssh_known_hosts: {kh}
""",
        encoding="utf-8",
    )
    sites = load_inventory(inv)
    assert sites["lab"].ssh_known_hosts == str(kh)
    assert sites["lab"].known_hosts_path() == str(kh)
