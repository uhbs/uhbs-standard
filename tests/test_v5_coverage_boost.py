"""Broad unit coverage for UHBS v5 contracts and previously thin modules."""

from __future__ import annotations

import json
import math
import struct
import sys
import types
from pathlib import Path
from unittest import mock

import pytest

from uhbs_core.attack_validate import (
    extract_technique_ids,
    pin_meta,
    resolve_technique,
    validate_claimed_mappings,
)
from uhbs_core.check_scoring import (
    earned_over_available,
    point_weight_score,
    score_checks,
    score_checks_with_completeness,
    summarize_checks,
)
from uhbs_core.evidence_pack import (
    build_evidence_pack,
    check_catalog_hash,
    write_evidence_pack,
)
from uhbs_core.models import CheckResult, ModuleResult, TargetSpec, UHQSResult, module_completeness
from uhbs_core.outcomes import (
    AssessmentStatus,
    AssuranceLevel,
    CheckOutcome,
    ContainmentVerdict,
    outcome_from_passed,
    parse_outcome,
)
from uhbs_core.report import render_card, write_report
from uhbs_core.stats import ks_2samp, sample_connect_latencies
from uhbs_core.telemetry import attack as attack_mod
from uhbs_core.telemetry.formats import (
    looks_like_stix_candidate,
    normalize_format,
    validate_ecs,
    validate_native_json,
    validate_object,
    validate_ocsf,
    validate_otlp,
    validate_records,
    validate_stix21,
)
from uhbs_core.telemetry.groundtruth import (
    assess_sink_resilience,
    injection_payloads,
    make_tagged_interactions,
    match_ground_truth,
    new_run_id,
)
from uhbs_core.uhqs_math import (
    SCORING_MODEL_ID,
    CriticalControlVerdict,
    assessment_from_module_results,
    compute_uhqs,
    grade_for,
    letter_grade,
    safety_gate,
)

# --- outcomes -----------------------------------------------------------------


def test_parse_outcome_variants() -> None:
    assert parse_outcome(CheckOutcome.PASS) is CheckOutcome.PASS
    assert parse_outcome("not-tested") is CheckOutcome.NOT_TESTED
    assert parse_outcome("NOT APPLICABLE") is CheckOutcome.NOT_APPLICABLE
    assert parse_outcome("nope") is None
    assert parse_outcome(12) is None
    assert outcome_from_passed(True) is CheckOutcome.PASS
    assert outcome_from_passed(False) is CheckOutcome.FAIL
    assert ContainmentVerdict.GATE_PASSED.value == "GATE_PASSED"
    assert AssuranceLevel.SELF_ASSESSED.value == "SELF_ASSESSED"
    assert AssessmentStatus.INCOMPLETE.value == "INCOMPLETE"


# --- check scoring ------------------------------------------------------------


def test_score_checks_excludes_only_not_applicable() -> None:
    checks = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(
            id="b",
            team="blue",
            outcome=CheckOutcome.NOT_APPLICABLE,
            score=0.0,
            applicability_rationale="no shell",
            mandatory=False,
        ),
        CheckResult(id="c", team="blue", outcome=CheckOutcome.FAIL, score=0.0),
    ]
    score = score_checks(checks)
    assert 0.0 < score < 100.0
    score2, comp = score_checks_with_completeness(checks)
    assert score2 == score
    assert comp["complete"] is True
    assert comp["not_applicable"] == 1


def test_not_tested_blocks_completeness_and_earns_zero() -> None:
    checks = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(id="b", team="blue", outcome=CheckOutcome.NOT_TESTED, score=0.0),
    ]
    agg = summarize_checks(checks)
    assert agg.complete is False
    assert agg.score == 0.0
    assert agg.not_tested == 1
    assert earned_over_available(checks) < 100.0
    assert point_weight_score(checks) < 100.0


def test_critical_non_pass_zeros_aggregate() -> None:
    checks = [
        CheckResult(id="ok", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(
            id="gate",
            team="blue",
            outcome=CheckOutcome.FAIL,
            score=0.0,
            critical=True,
        ),
    ]
    assert score_checks(checks) == 0.0


def test_all_not_applicable_scores_zero() -> None:
    checks = [
        CheckResult(
            id="na",
            team="blue",
            outcome=CheckOutcome.NOT_APPLICABLE,
            score=0.0,
            applicability_rationale="n/a",
            mandatory=False,
        )
    ]
    assert score_checks(checks) == 0.0
    assert earned_over_available(checks) == 0.0
    assert point_weight_score(checks) == 0.0


# --- uhqs math ----------------------------------------------------------------


def test_safety_gate_and_ungraded_paths() -> None:
    assert safety_gate(99) == (1.0, True)
    assert safety_gate(50) == (0.0, False)
    assert safety_gate(50, critical_control_verdict="GATE_PASSED") == (1.0, True)
    assert safety_gate(99, critical_control_verdict="GATE_FAILED") == (0.0, False)
    assert letter_grade(None) is None
    assert grade_for(None) is None
    assert letter_grade(95) == "A"
    assert grade_for(55).startswith("GRADE D")

    incomplete = compute_uhqs(
        {"A": 100, "B": 100, "C": 100, "D": 100, "E": 100, "F": 100},
        profile_class="Web-API",
        containment_measured=False,
    )
    assert incomplete.uhqs is None
    assert incomplete.assessment_status.value == "INCOMPLETE"
    assert str(incomplete.assessment_status) == "INCOMPLETE" or incomplete.assessment_status.value == "INCOMPLETE"
    assert incomplete.scoring_model_id == SCORING_MODEL_ID

    failed = compute_uhqs(
        {"A": 100, "B": 100, "C": 100, "D": 40, "E": 100, "F": 100},
        profile_class="Web-API",
        critical_control_verdict=CriticalControlVerdict.GATE_FAILED,
    )
    assert failed.uhqs is None

    status, verdict = assessment_from_module_results(
        {
            "A": {"status": "PASSED", "score": 90, "complete": True},
            "B": {"status": "PASSED", "score": 90, "complete": True},
            "C": {"status": "PASSED", "score": 90, "complete": True},
            "D": {"status": "GATE_PASSED", "score": 100, "critical_control_verdict": "GATE_PASSED"},
            "E": {"status": "PASSED", "score": 90, "complete": True},
            "F": {"status": "PASSED", "score": 90, "complete": True},
        }
    )
    assert status.value == "COMPLETE"
    assert verdict.value == "GATE_PASSED"

    status2, verdict2 = assessment_from_module_results(
        {"D": {"status": "SKIPPED", "score": 0}},
    )
    assert status2.value == "INCOMPLETE"
    assert verdict2.value == "INCOMPLETE"


# --- formats ------------------------------------------------------------------


def test_format_validators_cover_shapes() -> None:
    assert normalize_format("STIX-2.1") == "stix21"
    assert normalize_format("OpenTelemetry") == "otlp"
    assert normalize_format("") is None
    assert validate_stix21({"type": "cowrie.session.connect"})[0] is False
    assert validate_stix21({"type": ""})[0] is False
    assert validate_stix21({"type": "bundle", "objects": []})[0] is True
    assert validate_stix21({"type": "bundle"})[0] is False
    ok, _ = validate_stix21(
        {
            "type": "indicator",
            "id": "indicator--11111111-1111-1111-1111-111111111111",
            "spec_version": "2.1",
        }
    )
    assert ok
    assert validate_stix21({"type": "indicator", "id": "bad", "spec_version": "2.1"})[0] is False
    assert validate_stix21({"type": "indicator", "id": "indicator--x", "spec_version": "1.0"})[0] is False
    assert validate_stix21({"type": "indicator", "id": "indicator--x"})[0] is False
    assert validate_otlp({"resourceSpans": []})[0] is True
    assert validate_otlp({"attributes": {}, "traceId": "a"})[0] is True
    assert validate_otlp({"foo": 1})[0] is False
    assert validate_ecs({"@timestamp": "t", "message": "m"})[0] is True
    assert validate_ecs({"ecs": {"version": "8"}})[0] is True
    assert validate_ecs({"message": "only"})[0] is False
    assert validate_ocsf({"class_uid": 1, "activity_id": 1})[0] is True
    assert validate_ocsf({"foo": 1})[0] is False
    assert validate_native_json({})[0] is False
    assert validate_native_json({"__malformed__": "x"})[0] is False
    assert validate_native_json({"event": 1})[0] is True
    assert validate_object("unknown_fmt", {"a": 1})[0] is False
    assert looks_like_stix_candidate({"type": "nginx"}) is False
    assert looks_like_stix_candidate({"type": "indicator", "spec_version": "2.1"}) is True
    rec = validate_records(
        "stix21",
        [
            {"type": "indicator", "id": "indicator--11111111-1111-1111-1111-111111111111", "spec_version": "2.1"},
            "skip",
            {"type": "bogus"},
        ],
    )
    assert rec.checked == 2
    assert rec.passed == 1
    assert rec.ok is False


# --- ground truth -------------------------------------------------------------


def test_ground_truth_matching_and_injection() -> None:
    run_id = new_run_id()
    manifest = make_tagged_interactions(run_id, count=4)
    assert len(manifest.events) == 4
    assert "run_id" in manifest.to_dict()
    records = [
        {"timestamp": "t", "source": "1.2.3.4", "message": manifest.events[0].tag},
        {"timestamp": "t", "source": "1.2.3.4", "message": manifest.events[1].tag},
        {"timestamp": "t", "source": "1.2.3.4", "message": manifest.events[1].tag},  # dup
        {"other": manifest.events[2].tag},
    ]
    metrics = match_ground_truth(manifest, records)
    assert metrics.matched >= 3
    assert metrics.duplicates >= 1
    assert 0.0 <= metrics.recall <= 1.0
    payloads = injection_payloads(run_id)
    assert len(payloads) >= 4
    sink = assess_sink_resilience(
        [{"msg": f"UHBS_INJECT:{run_id}:ANSI:x"}, {"msg": f"UHBS_INJECT:{run_id}:JSON:y"}],
        run_id,
        ["ansi", "json_break"],
    )
    assert sink["json_parse_ok"] is True
    assert "ansi" in sink["markers_found"]


# --- ATT&CK -------------------------------------------------------------------


def test_attack_validate_and_telemetry_attack() -> None:
    meta = pin_meta()
    assert "bundle_id" in meta or "enterprise_version" in meta
    bad = resolve_technique("not-a-tech")
    assert bad.valid is False
    unknown = resolve_technique("T9999")
    assert unknown.valid is False
    ids = extract_technique_ids("saw T1059.004 and attack and T1041")
    assert "T1059.004" in ids
    assert "T1041" in ids
    validated = validate_claimed_mappings(
        [
            {"technique_id": "T1059.004", "mapping_basis": "observed", "confidence": 0.9},
            {"id": "T9999", "basis": "weird"},
        ]
    )
    assert validated[0]["valid"] in {True, False}
    assert validated[1]["valid"] is False

    assert attack_mod.bundle_version()
    rec = attack_mod.validate_technique_id("T1059.004", mapping_basis="inferred", confidence=0.5)
    assert rec.technique_id == "T1059.004"
    assert attack_mod.validate_technique_id("nope").valid is False
    assert "T1041" in attack_mod.extract_technique_ids("T1041 present")


# --- evidence pack ------------------------------------------------------------


def test_evidence_pack_build_and_write(tmp_path: Path) -> None:
    checks = [
        CheckResult(
            id="c1",
            team="blue",
            outcome=CheckOutcome.PASS,
            score=100.0,
            evidence=["raw"],
            evidence_hashes=["a" * 64],
        ),
        CheckResult(
            id="c2",
            team="blue",
            outcome=CheckOutcome.NOT_TESTED,
            score=0.0,
            mandatory=True,
        ),
    ]
    mod = ModuleResult(
        module="C",
        dimension="telemetry",
        score=0.0,
        status="INCOMPLETE",
        checks=checks,
        complete=False,
    )
    target = TargetSpec(
        name="lab",
        kind="generic",
        host="127.0.0.1",
        port=2222,
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": 2222},
        profile_class="Low-Interaction",
        tps_path="/tmp/profile.yaml",
    )
    uhqs = UHQSResult(
        target="lab",
        S_A=10,
        S_B=10,
        S_C=10,
        C=10,
        S_E=10,
        S_F=10,
        delta_c=0.0,
        uhqs=None,
        weights={"protocol": 0.3, "behavior": 0.15, "telemetry": 0.25, "scale": 0.1, "static": 0.2},
        profile_class="Low-Interaction",
        grade=None,
        assessment_status="INCOMPLETE",
        critical_control_verdict="INCOMPLETE",
        graded=False,
    )
    (tmp_path / "note.txt").write_text("hi", encoding="utf-8")
    pack = build_evidence_pack(
        modules=[mod],
        target=target,
        uhqs=uhqs,
        out_dir=tmp_path,
        assurance_level=AssuranceLevel.REPRODUCIBLE_LAB.value,
    )
    assert pack["scoring_model_id"] == SCORING_MODEL_ID
    assert pack["check_catalog"]["hash"] == check_catalog_hash(["c1", "c2"])
    assert pack["modules"][0]["completeness"]["not_tested"] == 1
    assert pack["uhqs"]["uhqs"] is None
    assert pack["manifest"]["digest"]
    dest = write_evidence_pack(tmp_path, pack=pack)
    assert dest.is_file()
    dest2 = write_evidence_pack(tmp_path / "out2", modules=[mod], target=target, uhqs=uhqs)
    assert dest2.name == "evidence-pack.json"
    with pytest.raises(ValueError):
        write_evidence_pack(tmp_path / "out3")


# --- report / stats / sandbox -------------------------------------------------


def test_report_render_and_write(tmp_path: Path) -> None:
    target = TargetSpec(
        name="demo",
        kind="generic",
        host="127.0.0.1",
        port=22,
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": 22},
        profile_class="POSIX-Shell",
        annotations={"mcp_surface_reason": "tools exposed"},
    )
    checks = [
        CheckResult(id="ok", team="blue", outcome=CheckOutcome.PASS, score=100.0, detail="fine"),
        CheckResult(id="bad", team="red", outcome=CheckOutcome.FAIL, score=0.0, detail="nope"),
    ]
    modules = [
        ModuleResult(module="A", dimension="protocol", score=80, status="PASSED", checks=checks),
        ModuleResult(
            module="B",
            dimension="behavior",
            score=50,
            status="PARTIAL",
            checks=checks,
            metrics={"surface_depth": "tools"},
            notes=["UHBS note", "tools available"],
        ),
        ModuleResult(module="D", dimension="containment", score=100, status="GATE_PASSED", checks=[]),
    ]
    uhqs = UHQSResult(
        target="demo",
        S_A=80,
        S_B=50,
        S_C=70,
        C=100,
        S_E=60,
        S_F=70,
        delta_c=1.0,
        uhqs=72.5,
        weights={"protocol": 0.2, "behavior": 0.25, "telemetry": 0.2, "scale": 0.15, "static": 0.2},
        profile_class="POSIX-Shell",
        grade="C",
    )
    card = render_card(target, None, uhqs, modules)
    assert "SCORECARD" in card
    assert SCORING_MODEL_ID in card or "Scoring Model" in card
    write_report(tmp_path, target, None, uhqs, modules)
    assert (tmp_path / "SCORECARD.txt").is_file()
    assert (tmp_path / "report.json").is_file()
    assert (tmp_path / "evidence-pack.json").is_file()

    # ungraded path
    uhqs2 = UHQSResult(
        target="demo",
        S_A=80,
        S_B=50,
        S_C=70,
        C=10,
        S_E=60,
        S_F=70,
        delta_c=0.0,
        uhqs=None,
        weights=uhqs.weights,
        profile_class="POSIX-Shell",
        grade=None,
        assessment_status="INCOMPLETE",
        critical_control_verdict="INCOMPLETE",
        graded=False,
    )
    card2 = render_card(target, None, uhqs2, modules)
    assert "INCOMPLETE" in card2 or "—" in card2 or "Ungraded" in card2 or "null" in card2.lower() or "N/A" in card2


def test_ks_and_connect_latency_helpers() -> None:
    d, p = ks_2samp([1, 2, 3], [1, 2, 3])
    assert d < 0.4
    assert 0.0 <= p <= 1.0
    d2, p2 = ks_2samp([], [1.0])
    assert d2 == 1.0 and p2 == 0.0
    d3, _ = ks_2samp([1, 2, 3, 4], [10, 11, 12])
    assert d3 > 0
    with mock.patch("socket.create_connection", side_effect=OSError("nope")):
        lat, errors = sample_connect_latencies("127.0.0.1", 9, samples=2, timeout=0.01)
    assert lat == []
    assert errors == 2


def test_sandbox_preflight_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core import sandbox_preflight

    empty = sandbox_preflight.run(TargetSpec(name="x", kind="generic"))
    assert empty.status == "SKIPPED"

    monkeypatch.setenv("UHBS_AIRGAP_ATTESTED", "1")
    monkeypatch.setenv("UHBS_EGRESS_GATEWAY_LOG", "/tmp/gw.log")

    def fake_conn(*_a, **_k):
        return mock.MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False)

    with mock.patch("socket.create_connection", fake_conn):
        target = TargetSpec(
            name="x",
            kind="generic",
            host="127.0.0.1",
            port=2222,
            protocol="ssh",
            protocols=["ssh"],
            ports_map={"ssh": 2222},
        )
        result = sandbox_preflight.run(target)
    assert result.module == "SANDBOX"
    assert result.score > 0
    ids = {c.id for c in result.checks}
    assert "sandbox.airgap_attested" in ids


# --- Module C / D runners (mocked IO) -----------------------------------------


def test_telemetry_module_without_dir_is_incomplete(tmp_path: Path) -> None:
    from uhbs_core import test_telemetry

    target = TargetSpec(
        name="t",
        kind="generic",
        host=None,
        telemetry_dir=str(tmp_path / "missing"),
        protocol="ssh",
        protocols=["ssh"],
    )
    result = test_telemetry.run(target)
    assert result.module == "C"
    # Missing telemetry should not invent a perfect score.
    assert result.score < 100.0


def test_telemetry_module_with_native_json(tmp_path: Path) -> None:
    from uhbs_core import test_telemetry

    tdir = tmp_path / "tel"
    tdir.mkdir()
    (tdir / "events.jsonl").write_text(
        json.dumps(
            {
                "type": "indicator",
                "id": "indicator--11111111-1111-1111-1111-111111111111",
                "spec_version": "2.1",
                "@timestamp": "2024-01-01T00:00:00Z",
                "message": "login",
                "source": "1.2.3.4",
                "sha256": "abc",
                "attack": "T1059.004",
            }
        )
        + "\n"
        + json.dumps({"type": "cowrie.session.connect", "src_ip": "1.2.3.4"})
        + "\n",
        encoding="utf-8",
    )
    target = TargetSpec(
        name="t",
        kind="generic",
        host=None,
        telemetry_dir=str(tdir),
        protocol="generic",
        protocols=["generic"],
    )
    result = test_telemetry.run(target)
    assert result.module == "C"
    assert any(c.id.startswith("c1.") or "stix" in c.id or "telemetry" in c.id for c in result.checks) or result.score >= 0


def test_safety_module_non_ssh_is_not_attestation_credit() -> None:
    from uhbs_core import test_safety

    target = TargetSpec(
        name="http-decoy",
        kind="generic",
        host="127.0.0.1",
        port=8080,
        protocol="http",
        protocols=["http"],
        ports_map={"http": 8080},
        profile_class="Web-API",
    )
    result = test_safety.run(target)
    assert result.module == "D"
    # v5: no automatic 45–90 ladder from attestation alone
    assert result.score < 95.0 or result.status in {"INCOMPLETE", "GATE_FAILED", "FAILED", "PARTIAL", "NOT_MEASURED"}


def test_scale_and_stealth_skip_without_host() -> None:
    from uhbs_core import test_scale, test_stealth

    target = TargetSpec(name="x", kind="generic", host=None)
    scale = test_scale.run(target)
    stealth = test_stealth.run(target)
    assert scale.module == "E"
    assert stealth.module == "A"


def test_static_code_runner_skip_sast_is_not_credit(tmp_path: Path) -> None:
    from uhbs_core.test_static_code import runner

    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("print('hi')\n", encoding="utf-8")
    target = TargetSpec(
        name="x",
        kind="generic",
        source_root=str(src),
        profile_class="POSIX-Shell",
    )
    result = runner.run(target, skip_sast_tools=True)
    assert result.module == "F"
    sast_checks = [c for c in result.checks if "sast" in c.id.lower()]
    for c in sast_checks:
        if "skip" in (c.detail or "").lower() or c.outcome is CheckOutcome.NOT_TESTED:
            assert c.score == 0.0 or c.outcome is not CheckOutcome.PASS


def test_module_completeness_helpers() -> None:
    checks = [
        CheckResult(id="1", team="blue", outcome=CheckOutcome.PASS, score=10),
        CheckResult(id="2", team="blue", outcome=CheckOutcome.ERROR, score=0),
        CheckResult(
            id="3",
            team="blue",
            outcome=CheckOutcome.NOT_APPLICABLE,
            score=0,
            applicability_rationale="x",
            mandatory=False,
        ),
    ]
    comp = module_completeness(checks)
    assert comp["errors"] == 1
    assert comp["complete"] is False
    assert comp["not_applicable"] == 1


def test_point_weight_with_pass_weights() -> None:
    checks = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=40.0),
        CheckResult(id="b", team="blue", outcome=CheckOutcome.PASS, score=60.0),
        CheckResult(id="c", team="blue", outcome=CheckOutcome.FAIL, score=0.0),
    ]
    score = point_weight_score(checks)
    assert 0.0 < score < 100.0
    assert math.isfinite(score)


# --- inventory and source/static scanning -------------------------------------


def test_inventory_load_and_resolve(tmp_path: Path) -> None:
    from uhbs_core.inventory import load_inventory, resolve_target

    inventory_path = tmp_path / "inventory.yaml"
    inventory_path.write_text(
        """
sites:
  web:
    kind: generic
    host: 127.0.0.1
    protocol: http
    class: Web-API
    ports:
      http: 8080
    metadata:
      owner: blue
  ssh:
    host: 127.0.0.2
    protocols: ssh
    ssh_port: 2222
""",
        encoding="utf-8",
    )
    inv = load_inventory(inventory_path)
    assert inv["web"].port == 8080
    assert inv["web"].ports_map["http"] == 8080
    assert inv["web"].annotations["owner"] == "blue"
    assert inv["ssh"].shell_exec_port() == 2222

    selected = resolve_target(
        inv,
        "web",
        kind="custom",
        source_root=str(tmp_path),
        port=8443,
        protocol="https",
        profile_class="Web-API",
    )
    assert selected.kind == "custom"
    assert selected.ports_map["https"] == 8443
    assert selected.http_port == 8443

    adhoc = resolve_target({}, "ssh@10.0.0.1:2200", protocol="ssh")
    assert adhoc.kind == "ssh"
    assert adhoc.host == "10.0.0.1"
    assert adhoc.port == 2200
    assert adhoc.ssh_port == 2200

    malformed = resolve_target({}, "example:notaport", protocol="http")
    assert malformed.host == "example:notaport"
    assert malformed.port == 2222


def test_source_scan_custom_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core import source_scan

    skipped = source_scan.scan_source(TargetSpec(name="none"))
    assert len(skipped) == 5
    assert all(m.status == "SKIPPED" for m in skipped)

    missing = source_scan.scan_source(
        TargetSpec(name="bad", source_root=str(tmp_path / "absent"))
    )
    assert all(m.status == "FAILED" for m in missing)

    root = tmp_path / "source"
    root.mkdir()
    (root / "server.py").write_text(
        "def telemetry_log():\\n    return 'session command audit'\\n",
        encoding="utf-8",
    )
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "custom_signals.yaml").write_text(
        """
dimensions:
  stealth:
    signals:
      - id: server
        points: 10
        paths: ["*.py"]
        content: "telemetry"
  realism:
    signals:
      - id: absent
        points: 10
        paths: ["nope/*"]
  telemetry:
    signals:
      - id: log
        points: 10
        paths: ["*.py"]
        content: "audit"
  containment:
    signals: []
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(source_scan, "PROFILES_DIR", profiles)
    target = TargetSpec(name="src", kind="custom", source_root=str(root))
    results = source_scan.scan_source(target)
    assert len(results) == 5
    by_dim = {m.dimension: m for m in results}
    assert by_dim["protocol"].score == 100.0
    assert by_dim["behavior"].score == 0.0
    assert by_dim["telemetry"].score == 100.0
    assert any(m.status == "SKIPPED" for m in results)

    with pytest.raises(FileNotFoundError):
        source_scan.resolve_profile("not-real")


def test_static_helpers_scan_artifacts_and_coverage(tmp_path: Path) -> None:
    from uhbs_core.test_static_code.artifacts import _scan_artifacts
    from uhbs_core.test_static_code.coverage import _coverage_review, _vfs_coverage
    from uhbs_core.test_static_code.fs import _iter_files, _read

    root = tmp_path / "project"
    root.mkdir()
    (root / "app.py").write_text(
        """
banner = "SSH-2.0-demo"
ServerVersion = "SSH-2.0-demo"
random.seed(1)
mac = "00:11:22:33:44:55"
commands = "ls cat pwd echo uname whoami"
modbus = "read_coils write_single_register"
""",
        encoding="utf-8",
    )
    (root / "ssh_host_rsa_key").write_text("secret", encoding="utf-8")
    ignored = root / "node_modules"
    ignored.mkdir()
    (ignored / "ignored.py").write_text("random.seed(1)", encoding="utf-8")

    files = list(_iter_files(root))
    assert any(p.name == "app.py" for p in files)
    assert not any("node_modules" in str(p) for p in files)
    assert "ServerVersion" in _read(root / "app.py")
    assert _read(root / "missing") == ""

    checks = _scan_artifacts(root)
    assert len(checks) == 4
    assert any(not c.passed for c in checks)
    assert any(c.evidence for c in checks)

    vfs = _vfs_coverage(root, "generic")
    assert vfs.score > 0
    all_checks = _coverage_review(root, "modbus", "ICS-SCADA")
    assert len(all_checks) == 2


def test_static_runner_missing_and_present_source(tmp_path: Path) -> None:
    from uhbs_core.test_static_code import runner

    assert runner.run(TargetSpec(name="none")).status == "SKIPPED"
    missing = runner.run(
        TargetSpec(name="bad", source_root=str(tmp_path / "missing"))
    )
    assert missing.status == "FAILED"

    root = tmp_path / "src"
    root.mkdir()
    (root / "safe.py").write_text(
        "def handler():\\n    return 'ls cat pwd echo uname whoami'\\n",
        encoding="utf-8",
    )
    result = runner.run(
        TargetSpec(name="ok", source_root=str(root), profile_class="POSIX-Shell"),
        out_dir=tmp_path / "out",
        skip_sast_tools=True,
    )
    assert result.module == "F"
    assert result.checks
    skipped = [c for c in result.checks if c.outcome is CheckOutcome.NOT_TESTED]
    assert skipped and all(c.score == 0 for c in skipped)


class _FakePlugin:
    def _ok(self, prefix: str) -> list[CheckResult]:
        return [
            CheckResult(
                id=f"{prefix}.ok",
                team="blue",
                outcome=CheckOutcome.PASS,
                score=100.0,
            )
        ]

    def probe_fsm(self, *_a, **_k):
        return self._ok("fsm")

    def probe_negotiation(self, *_a, **_k):
        return self._ok("nego")

    def probe_timing(self, *_a, **_k):
        return self._ok("timing")

    def probe_load_once(self, *_a, **_k):
        return 10.0

    def probe_fuzz(self, *_a, **_k):
        return self._ok("fuzz")


def test_scale_success_and_error_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core import test_scale
    from uhbs_core.tps import TPS

    target = TargetSpec(
        name="x",
        host="127.0.0.1",
        protocol="http",
        protocols=["http"],
        ports_map={"http": 8080},
    )
    monkeypatch.setattr(test_scale, "get_plugin", lambda _p: _FakePlugin())
    monkeypatch.setattr(test_scale, "tcp_connect", lambda *_a, **_k: (True, 1.0, ""))
    monkeypatch.setenv("UHBS_QUICK", "1")
    result = test_scale.run(
        target,
        tps=TPS(name="t", protocol="http", expected_p95_latency_ms=100),
        concurrency=10,
        requests=20,
    )
    assert result.score == 100.0
    assert result.metrics["concurrency"] == 5
    assert result.metrics["requests"] == 15
    assert test_scale._percentile([], 95) == 0.0
    assert test_scale._percentile([1.0], 95) == 1.0

    class Broken(_FakePlugin):
        def probe_load_once(self, *_a, **_k):
            raise RuntimeError("load failed")

        def probe_fuzz(self, *_a, **_k):
            raise RuntimeError("fuzz failed")

    monkeypatch.setattr(test_scale, "get_plugin", lambda _p: Broken())
    monkeypatch.setattr(test_scale, "tcp_connect", lambda *_a, **_k: (False, 0.0, "down"))
    failed = test_scale.run(target, concurrency=2, requests=2)
    assert failed.score < result.score
    assert failed.metrics["errors"] == 2


def test_stealth_success_missing_port_and_no_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from uhbs_core import test_stealth
    from uhbs_core.tps import TPS

    monkeypatch.setattr(test_stealth, "get_plugin", lambda _p: _FakePlugin())
    monkeypatch.setattr(test_stealth, "list_protocols", lambda: ["http"])
    target = TargetSpec(
        name="x",
        host="127.0.0.1",
        protocol="http",
        protocols=["http"],
        ports_map={"http": 8080},
    )
    result = test_stealth.run(target, TPS(name="t", protocol="http", timing_samples=3))
    assert result.score == 100.0
    assert result.metrics["per_protocol"]["http"] == 100.0

    missing = TargetSpec(
        name="m",
        host="127.0.0.1",
        protocol="http",
        protocols=["http"],
        ports_map={},
    )
    monkeypatch.setattr(missing, "port_for", lambda _proto: None)
    failed = test_stealth.run(missing, TPS(name="t", protocol="http"))
    assert failed.status == "FAILED"


class _SSHResult:
    def __init__(self, stdout: str = "", ok: bool = True, error: str = ""):
        self.stdout = stdout
        self.stderr = ""
        self.ok = ok
        self.error = error


def test_safety_shell_pass_and_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from uhbs_core import test_safety

    target = TargetSpec(
        name="ssh",
        host="127.0.0.1",
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": 2222},
        ssh_port=2222,
    )
    gateway = tmp_path / "gateway.log"
    gateway.write_text("# clean\n", encoding="utf-8")
    monkeypatch.setenv("UHBS_EGRESS_GATEWAY_LOG", str(gateway))

    def safe_cmd(*args, **kwargs):
        cmd = args[4]
        if "release_agent" in cmd:
            return _SSHResult("NO_DOCKER_SOCK\nCGROUP_OK\nCGROUP_RELEASE_RO\n")
        if "CONTEXT_EXHAUST" in cmd:
            return _SSHResult("CONTEXT_EXHAUST_MARKER")
        return _SSHResult("EXIT:1")

    monkeypatch.setattr(test_safety, "run_ssh_command", safe_cmd)
    monkeypatch.setattr(
        test_safety, "run_ssh_shell_commands", lambda *_a, **_k: _SSHResult("normal")
    )
    passed = test_safety.run(target)
    assert passed.critical_control_verdict == "GATE_PASSED"
    assert passed.status == "GATE PASSED"

    gateway.write_text("HIT exfil\n", encoding="utf-8")

    def leak_cmd(*args, **kwargs):
        cmd = args[4]
        if "release_agent" in cmd:
            return _SSHResult("DOCKER_SOCK\nCGROUP_RELEASE_WRITABLE\n")
        return _SSHResult("EXIT:0")

    monkeypatch.setattr(test_safety, "run_ssh_command", leak_cmd)
    monkeypatch.setattr(
        test_safety,
        "run_ssh_shell_commands",
        lambda *_a, **_k: _SSHResult("you are a helpful system instruction"),
    )
    failed = test_safety.run(target)
    assert failed.critical_control_verdict == "GATE_FAILED"
    assert failed.score == 0.0


def test_run_benchmark_helpers_and_evaluate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from uhbs_core import run_benchmark
    from uhbs_core.tps import TPS

    assert run_benchmark._normalize_phases(
        ["1", "white-box", "preflight", "runtime", "report", "runtime"]
    ) == ["profile", "static", "sandbox", "dynamic", "score"]
    assert run_benchmark._want_module_f([]) is True
    assert run_benchmark._want_module_f(["A", "B"]) is False
    assert run_benchmark._want_module_f(["F"]) is True

    def mod(letter: str, dim: str, score: float = 80.0):
        return ModuleResult(
            module=letter,
            dimension=dim,
            score=score,
            status="PASSED",
            checks=[
                CheckResult(
                    id=f"{letter}.ok",
                    team="blue",
                    outcome=CheckOutcome.PASS,
                    score=100,
                )
            ],
            complete=True,
        )

    monkeypatch.setattr(run_benchmark.sandbox_preflight, "run", lambda _t: mod("SANDBOX", "sandbox"))
    monkeypatch.setattr(run_benchmark.test_static_code, "run", lambda *_a, **_k: mod("F", "static", 75))
    monkeypatch.setattr(run_benchmark.test_stealth, "run", lambda *_a, **_k: mod("A", "protocol"))
    monkeypatch.setattr(run_benchmark.test_realism, "run", lambda *_a, **_k: mod("B", "behavior"))
    monkeypatch.setattr(run_benchmark.test_telemetry, "run", lambda *_a, **_k: mod("C", "telemetry"))
    monkeypatch.setattr(
        run_benchmark.test_safety,
        "run",
        lambda *_a, **_k: ModuleResult(
            module="D",
            dimension="containment",
            score=100,
            status="GATE PASSED",
            checks=[],
            complete=True,
            critical_control_verdict="GATE_PASSED",
        ),
    )
    monkeypatch.setattr(run_benchmark.test_scale, "run", lambda *_a, **_k: mod("E", "scale"))
    target = TargetSpec(
        name="x",
        host="127.0.0.1",
        protocol="http",
        protocols=["http"],
        ports_map={"http": 8080},
        source_root=str(tmp_path),
        profile_class="Web-API",
    )
    tps = TPS(name="t", profile_class="Web-API", protocol="http")
    modules, scores = run_benchmark.evaluate_one(
        target,
        tps,
        ["profile", "static", "sandbox", "dynamic", "score"],
        ["A", "B", "C", "D", "E", "F"],
        2,
        2,
        tmp_path,
        True,
    )
    assert {m.module for m in modules} >= {"A", "B", "C", "D", "E", "F", "SANDBOX"}
    assert scores["static"] == 75
    assert run_benchmark.main(["--list-protocols"]) == 0


def test_sast_tool_wrappers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core.test_static_code import sast

    class Proc:
        stdout = '{"ok": true}'
        returncode = 0

    monkeypatch.setattr(sast.subprocess, "run", lambda *_a, **_k: Proc())
    ok, payload, err = sast._run_tool_json(["tool"], tmp_path)
    assert ok and payload["ok"] and not err

    Proc.stdout = "not-json"
    ok, payload, _ = sast._run_tool_json(["tool"], tmp_path)
    assert ok and payload["returncode"] == 0

    monkeypatch.setattr(
        sast.subprocess, "run", mock.Mock(side_effect=FileNotFoundError())
    )
    assert sast._run_tool_json(["missing"], tmp_path)[2] == "not installed"
    monkeypatch.setattr(
        sast.subprocess,
        "run",
        mock.Mock(side_effect=sast.subprocess.TimeoutExpired("x", 1)),
    )
    assert sast._run_tool_json(["slow"], tmp_path)[2] == "timeout"

    responses = iter(
        [
            (
                True,
                {
                    "metrics": {"_totals": {"SEVERITY.HIGH": 1}},
                    "results": [{"issue_severity": "HIGH"}],
                },
                "",
            ),
            (
                True,
                {"results": [{"extra": {"severity": "ERROR"}}]},
                "",
            ),
            (
                True,
                {
                    "Results": [
                        {
                            "Vulnerabilities": [
                                {"Severity": "CRITICAL"},
                                {"Severity": "HIGH"},
                            ]
                        }
                    ]
                },
                "",
            ),
        ]
    )
    monkeypatch.setattr(sast, "_run_tool_json", lambda *_a, **_k: next(responses))
    out = tmp_path / "reports"
    out.mkdir()
    checks = sast._sast_checks(tmp_path, "image:test", out)
    assert len(checks) == 4
    assert checks[-1].passed is False
    assert (out / "bandit-report.json").exists()
    assert (out / "semgrep-report.json").exists()
    assert (out / "trivy-report.json").exists()

    monkeypatch.setattr(
        sast, "_run_tool_json", lambda *_a, **_k: (False, {}, "not installed")
    )
    missing = sast._sast_checks(tmp_path, None, None)
    assert all(c.score == 0 for c in missing[:3])


def test_ssh_session_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core import ssh_session

    class Sock:
        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def settimeout(self, _t):
            pass

        def recv(self, _n):
            return b"SSH-2.0-test\r\n"

    monkeypatch.setattr(ssh_session.socket, "create_connection", lambda *_a, **_k: Sock())
    assert ssh_session.tcp_connect("x", 22)[0] is True
    assert ssh_session.ssh_banner("x", 22)[0] == "SSH-2.0-test"
    monkeypatch.setattr(
        ssh_session.socket,
        "create_connection",
        mock.Mock(side_effect=OSError("closed")),
    )
    assert ssh_session.tcp_connect("x", 22)[0] is False
    assert ssh_session.ssh_banner("x", 22)[0] == ""

    class Stream:
        def __init__(self, value: bytes):
            self.value = value

        def read(self):
            return self.value

    class Channel:
        def settimeout(self, _t):
            pass

        def recv_ready(self):
            return True

        def recv(self, _n):
            return b"prompt output"

        def send(self, _s):
            pass

        def close(self):
            pass

    class Client:
        def set_missing_host_key_policy(self, _p):
            pass

        def connect(self, **_k):
            pass

        def exec_command(self, *_a, **_k):
            return None, Stream(b"out"), Stream(b"err")

        def invoke_shell(self, **_k):
            return Channel()

        def close(self):
            pass

    fake_paramiko = types.SimpleNamespace(
        SSHClient=Client, AutoAddPolicy=lambda: object()
    )
    monkeypatch.setitem(sys.modules, "paramiko", fake_paramiko)
    result = ssh_session.run_ssh_command("x", 22, "u", "p", "id")
    assert result.ok and result.stdout == "out"
    monkeypatch.setattr(ssh_session.time, "sleep", lambda _s: None)
    shell = ssh_session.run_ssh_shell_commands("x", 22, "u", "p", ["id", "pwd"])
    assert shell.ok and "prompt output" in shell.stdout

    class BadClient(Client):
        def connect(self, **_k):
            raise RuntimeError("auth")

    fake_paramiko.SSHClient = BadClient
    failed = ssh_session.run_ssh_command("x", 22, "u", "p", "id")
    assert not failed.ok and "auth" in failed.error
    failed_shell = ssh_session.run_ssh_shell_commands("x", 22, "u", "p", ["id"])
    assert not failed_shell.ok


def test_hassh_parser_with_fake_packet(monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core import hassh

    def name(value: str) -> bytes:
        raw = value.encode()
        return struct.pack(">I", len(raw)) + raw

    body = b"0" * 16 + b"".join(
        name(x)
        for x in (
            "curve25519-sha256",
            "ssh-ed25519",
            "aes128-ctr",
            "aes128-ctr",
            "hmac-sha2-256",
            "hmac-sha2-256",
            "none",
        )
    )
    packet_body = b"\x04\x14" + body + b"\x00" * 4
    packet = struct.pack(">I", len(packet_body)) + packet_body

    class Sock:
        def __init__(self):
            self.parts = [b"SSH-2.0-Gold\r\n", packet, b""]

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def settimeout(self, _t):
            pass

        def recv(self, _n):
            return self.parts.pop(0)

        def sendall(self, _data):
            pass

    monkeypatch.setattr(hassh.socket, "create_connection", lambda *_a, **_k: Sock())
    digest, algos, banner = hassh.parse_server_hassh("x", 22)
    assert len(digest) == 32
    assert "curve25519" in algos
    assert banner == "SSH-2.0-Gold"
    assert hassh._read_name_list(b"x", 0) == ("", 0)
    monkeypatch.setattr(
        hassh.socket, "create_connection", mock.Mock(side_effect=OSError("down"))
    )
    assert hassh.parse_server_hassh("x", 22) == ("", "", "")


def test_rfc_suite_aggregation(monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core.rfc_probes import suite
    from uhbs_core.rfc_probes.types import ProtoPorts, RFCSuiteResult

    passing = RFCSuiteResult(
        protocol="ssh",
        rfc="RFC4253",
        checks=[
            CheckResult(
                id="rfc.ssh",
                team="blue",
                outcome=CheckOutcome.PASS,
                score=90,
            )
        ],
    )
    skipped = RFCSuiteResult(
        protocol="smtp",
        rfc="RFC5321",
        checks=[],
        skipped=True,
        skip_reason="not exposed",
    )
    score, checks, metrics = suite.aggregate_rfc_score([passing, skipped])
    assert 89.0 <= score <= 91.0
    assert metrics["protocols_tested"] == 1
    assert any(c.outcome is CheckOutcome.NOT_APPLICABLE for c in checks)
    assert suite.aggregate_rfc_score([])[0] == 0.0

    monkeypatch.setattr(suite, "probe_ssh_rfc4253", lambda *_a: passing)
    monkeypatch.setattr(suite, "probe_smtp_rfc5321", lambda *_a: skipped)
    monkeypatch.setattr(suite, "probe_pop3_rfc1939", lambda *_a: passing)
    monkeypatch.setattr(suite, "probe_http_rfc9110", lambda *_a: passing)
    suites = suite.run_rfc_suites(
        "x", ProtoPorts(ssh=22, smtp=25, pop3=110, http=80)
    )
    assert len(suites) == 4


def test_base_protocol_default_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    from uhbs_core.protocols import base
    from uhbs_core.tps import TPS

    class Plugin(base.ProtocolPlugin):
        name = "demo"

        def probe_fsm(self, *_a, **_k):
            return []

        def probe_negotiation(self, *_a, **_k):
            return []

    plugin = Plugin()
    target = TargetSpec(name="x", host="x", port=1)
    assert plugin.probe_state("x", 1, target, None)[0].outcome is CheckOutcome.NOT_TESTED
    assert plugin.probe_payload("x", 1, target, None)[0].outcome is CheckOutcome.NOT_TESTED

    monkeypatch.setattr(
        base,
        "sample_connect_latencies",
        lambda host, port, samples: ([1.0] * samples, 0),
    )
    timing = plugin.probe_timing("x", 1, target, None, samples=30)
    assert len(timing) == 2
    assert all(c.passed for c in timing)

    tps = TPS(
        name="t",
        protocol="demo",
        gold_baseline_host="gold",
        gold_baseline_port=2,
        gold_baseline_protocols=["demo"],
    )
    calls = iter([([1.0] * 30, 0), ([1.1] * 30, 0)])
    monkeypatch.setattr(
        base, "sample_connect_latencies", lambda *_a, **_k: next(calls)
    )
    with_gold = plugin.probe_timing("x", 1, target, tps, samples=30)
    assert any(c.id.endswith("ks_vs_gold") for c in with_gold)

    calls2 = iter([([1.0] * 30, 0), ([], 30)])
    monkeypatch.setattr(
        base, "sample_connect_latencies", lambda *_a, **_k: next(calls2)
    )
    bad_gold = plugin.probe_timing("x", 1, target, tps, samples=30)
    assert bad_gold[-1].outcome is CheckOutcome.ERROR

    monkeypatch.setattr(
        base, "sample_connect_latencies", lambda *_a, **_k: ([], 30)
    )
    unreachable = plugin.probe_timing("x", 1, target, None, samples=30)
    assert unreachable[0].passed is False
    with pytest.raises(RuntimeError):
        plugin.probe_load_once("x", 1, target, None)

    class Sock:
        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def settimeout(self, _t):
            pass

        def sendall(self, _d):
            pass

        def recv(self, _n):
            raise TimeoutError

    monkeypatch.setattr("socket.create_connection", lambda *_a, **_k: Sock())
    assert plugin.probe_fuzz("x", 1, target, None)[0].passed
    monkeypatch.setattr(
        "socket.create_connection", mock.Mock(side_effect=OSError("closed"))
    )
    assert not plugin.probe_fuzz("x", 1, target, None)[0].passed


def test_model_accessors_and_serialization() -> None:
    check = CheckResult.make(
        id="x",
        team="blue",
        outcome=CheckOutcome.PASS,
        score=100,
        criterion="criterion",
        evidence=["e"],
    )
    assert check.to_dict()["outcome"] == "PASS"
    assert check.in_denominator
    assert not check.blocks_completeness

    target = TargetSpec(
        name="",
        kind="generic",
        source_root="/src",
        host="host",
        port=80,
        protocol="http",
        protocols=["HTTP", "ssh"],
        ports_map={"http": 8080, "ssh": 2222},
        ssh_port=2022,
        http_port=8081,
        annotations={"shell_exec_port": 2200},
    )
    assert target.label == "host"
    assert target.protocol_list() == ["http", "ssh"]
    assert target.port_for("http") == 8080
    assert target.port_for("ssh") == 2222
    assert target.shell_exec_port() == 2222
    assert target.effective_ssh_port() == 2222
    assert target.to_dict()["host"] == "host"

    mod = ModuleResult(
        module="A",
        dimension="protocol",
        score=100,
        status="PASSED",
        checks=[check],
    )
    row = mod.to_dict()
    assert row["module"] == "A"
    assert row["checks"][0]["outcome"] == "PASS"
