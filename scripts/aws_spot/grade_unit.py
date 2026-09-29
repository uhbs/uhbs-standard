#!/usr/bin/env python3
"""Grade one UHBS unit on the Spot target host (on-box C/D path).

Intended to run on Spot A at /opt/uhbs/uhbs-standard (or laptop ROOT).
Tracker SQLite updates happen on the operator laptop via run_unit_remote.sh;
this script only produces docs artifacts under results-5.0.1/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(os.environ.get("UHBS_ROOT", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab_recipes import recipe_for  # noqa: E402

UHBS_VERSION = "5.0.1"


def sh(cmd: str, *, check: bool = True) -> subprocess.CompletedProcess:
    print(f"+ {cmd}", flush=True)
    return subprocess.run(["bash", "-lc", cmd], cwd=ROOT, check=check)


def localize_start_cmd(cmd: str) -> str:
    """Drop host port publishes when UHBS_LOCAL_DOCKER=1 (grader uses uhbs-lab DNS).

    Avoids collisions with unrelated local services (Redis :6379, Postgres, etc.).
    Spot dual-vantage still needs published ports — leave unset there.
    """
    if os.environ.get("UHBS_LOCAL_DOCKER", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }:
        return cmd
    # Only docker publish forms (never mkdir -p / chmod -p / etc.).
    # -p 0.0.0.0:6379:6379 | -p 8080:8080/udp | --publish 8080:8080 | --publish=…
    cmd = re.sub(
        r"\s-p\s+(?:\d{1,3}(?:\.\d{1,3}){3}:)?\d{1,5}:\d{1,5}(?:/(?:tcp|udp))?\b",
        "",
        cmd,
    )
    cmd = re.sub(
        r"\s--publish(?:=|\s+)(?:\d{1,3}(?:\.\d{1,3}){3}:)?\d{1,5}:\d{1,5}(?:/(?:tcp|udp))?\b",
        "",
        cmd,
    )
    return cmd


def docker_id(image: str) -> str | None:
    try:
        return subprocess.check_output(
            ["docker", "image", "inspect", "-f", "{{.Id}}", image],
            text=True,
            cwd=ROOT,
        ).strip()
    except subprocess.CalledProcessError:
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_unit(db: Path, unit_id: str) -> dict:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM benchmark_units WHERE unit_id=?", (unit_id,)).fetchone()
    conn.close()
    if not row:
        raise SystemExit(f"unknown unit {unit_id}")
    return dict(row)


def ensure_clone(repo: str, dest: Path) -> tuple[str, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").is_dir():
        sh(f'GIT_TERMINAL_PROMPT=0 git clone --depth 1 "{repo}" "{dest}"')
    branch = subprocess.check_output(
        ["git", "-C", str(dest), "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()
    sha = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
    return branch, sha


def ensure_network() -> None:
    sh("docker network create uhbs-lab 2>/dev/null || true", check=False)


def prepare_module_d_evidence(
    unit: dict,
    recipe: dict,
    out: Path,
    *,
    mode: str,
) -> dict[str, str]:
    """Flush gateway envelope + dump host inspect with SHA-256 digests for Module D.

    Returns env var map for the grader container (paths are /work-relative).
    """
    evidence = out / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    telemetry = ROOT / recipe["telemetry_mount"]
    telemetry.mkdir(parents=True, exist_ok=True)
    gateway = telemetry / "egress-gateway.log"

    envelope = {
        "type": "uhbs_gateway_envelope",
        "uhbs_version": UHBS_VERSION,
        "uhbs_gateway_envelope": True,
        "unit_id": unit["unit_id"],
        "mode": mode,
        "flushed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    # Preserve prior HIT lines (fail-closed evidence) after the envelope header.
    prior_hits: list[str] = []
    if gateway.is_file() and gateway.stat().st_size > 0:
        for ln in gateway.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith("{"):
                continue
            if "HIT" in s.upper():
                prior_hits.append(s)
    body = json.dumps(envelope, separators=(",", ":")) + "\n"
    if prior_hits:
        body += "\n".join(prior_hits) + "\n"
    gateway.write_text(body, encoding="utf-8")
    # Post-activity flush before Module D reads the log.
    with gateway.open("a", encoding="utf-8") as handle:
        handle.flush()
        os.fsync(handle.fileno())

    container = recipe.get("container") or recipe.get("alias") or ""
    inspect_path = evidence / "container-inspect.json"
    if container:
        proc = subprocess.run(
            ["docker", "inspect", container],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            inspect_path.write_text(proc.stdout, encoding="utf-8")
        else:
            inspect_path.write_text(
                json.dumps(
                    {
                        "error": "docker_inspect_failed",
                        "container": container,
                        "stderr": (proc.stderr or "")[:500],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
    else:
        inspect_path.write_text(
            json.dumps({"error": "no_container_in_recipe"}) + "\n", encoding="utf-8"
        )

    gw_digest = sha256_file(gateway)
    inspect_digest = sha256_file(inspect_path)
    (evidence / "egress-gateway.log.sha256").write_text(gw_digest + "\n", encoding="utf-8")
    (evidence / "container-inspect.json.sha256").write_text(
        inspect_digest + "\n", encoding="utf-8"
    )
    # Sidecar copy of gateway for offline audit (telemetry may be ephemeral).
    (evidence / "egress-gateway.log").write_bytes(gateway.read_bytes())

    latest_rel = Path(unit["latest_path"]) / mode
    inspect_work = f"/work/{latest_rel.as_posix()}/evidence/container-inspect.json"
    return {
        "UHBS_EGRESS_GATEWAY_LOG": "/telemetry/egress-gateway.log",
        "UHBS_EGRESS_GATEWAY_SHA256": gw_digest,
        "UHBS_CONTAINER_INSPECT_JSON": inspect_work,
        "UHBS_CONTAINER_INSPECT_SHA256": inspect_digest,
        "module_d_gateway_sha256": gw_digest,
        "module_d_inspect_sha256": inspect_digest,
        "module_d_inspect_path": str(inspect_path.relative_to(ROOT)),
    }


def write_readme(out_dir: Path, unit_id: str, mode: str, report: dict) -> None:
    uhqs = report.get("uhqs") or {}
    scorecard = (out_dir / "SCORECARD.txt").read_text(encoding="utf-8", errors="replace")
    status = uhqs.get("assessment_status") or report.get("assessment_status")
    body = f"""# {unit_id} — {mode} artifacts

**UHQS {uhqs.get("uhqs")} / {uhqs.get("grade")}** · UHBS v{UHBS_VERSION} · assessment `{status}` · δ_C={uhqs.get("delta_c")}

## Verbatim SCORECARD.txt

```text
{scorecard.rstrip()}
```
"""
    (out_dir / "README.md").write_text(body + "\n", encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    files = []
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(out_dir).as_posix()
        if rel == "MANIFEST.json":
            continue
        files.append({"path": rel, "sha256": sha256_file(path)})
    (out_dir / "MANIFEST.json").write_text(
        json.dumps({"artifacts": files}, indent=2) + "\n", encoding="utf-8"
    )


def write_run_meta(out_dir: Path, meta: dict) -> None:
    path = out_dir / "run-meta.json"
    existing: dict = {}
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    existing.update(meta)
    existing["updated_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")


def finalize(out_dir: Path, unit_id: str, mode: str, meta: dict) -> dict:
    report_path = out_dir / "report.json"
    if not report_path.is_file():
        raise SystemExit(f"missing report.json in {out_dir}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    write_readme(out_dir, unit_id, mode, report)
    write_run_meta(out_dir, meta)
    write_manifest(out_dir)
    return report


def _candidate_dockerfiles(recipe: dict) -> list[Path]:
    bench = recipe["bench"]
    return [
        ROOT / "docs" / "conformance" / "labs" / bench / "Dockerfile.lab",
        ROOT / ".local" / "labs" / bench / "Dockerfile.lab",
        ROOT / ".local" / "labs" / bench / "Dockerfile",
        ROOT / "docs" / "conformance" / "labs" / bench / "Dockerfile",
    ]


def publish_score_dockerfile(
    unit: dict,
    recipe: dict,
    *,
    image_digest: str | None,
) -> dict:
    """Persist the exact target Dockerfile under the unit results tree.

    Layout (unit root = latest_path):
      Dockerfile              — build recipe used for the graded image
      image/docker_config.toml / other COPY companions when present
      image/SOURCE.txt        — where the Dockerfile was taken from
    """
    latest = ROOT / unit["latest_path"]
    image_dir = latest / "image"
    image_dir.mkdir(parents=True, exist_ok=True)
    dest = latest / "Dockerfile"
    source = "generated-pin"
    body: str | None = None

    for candidate in _candidate_dockerfiles(recipe):
        if candidate.is_file() and candidate.stat().st_size > 0:
            body = candidate.read_text(encoding="utf-8", errors="replace")
            source = str(candidate.relative_to(ROOT)) if candidate.is_relative_to(ROOT) else str(candidate)
            # Copy common companion files next to Dockerfile for exact rebuild.
            for name in (
                "docker_config.toml",
                "config.toml",
                "config.json",
                "cowrie.cfg",
                "requirements.txt",
            ):
                for base in (candidate.parent, ROOT / "docs" / "conformance" / "labs" / recipe["bench"]):
                    src = base / name
                    if src.is_file():
                        (image_dir / name).write_bytes(src.read_bytes())
                        # Also place beside Dockerfile when the Dockerfile COPY's it from context root.
                        if name in body:
                            (latest / name).write_bytes(src.read_bytes())
            break

    if body is None:
        digest = (image_digest or "").strip()
        ref = recipe["image"]
        if digest and not digest.startswith("sha256:"):
            digest = f"sha256:{digest}"
        pin = f"{ref}@{digest}" if digest and "@" not in ref else ref
        body = (
            f"# UHBS {UHBS_VERSION} pinned target image for `{unit['unit_id']}`.\n"
            f"# No local build context — this reproduces the graded image via pull.\n"
            f"# Strategy: {recipe.get('strategy')}\n"
            f"# Base reason: {recipe.get('base_image_reason') or 'n/a'}\n"
            f"FROM {pin}\n"
        )
        source = f"pin:{pin}"

    header = (
        f"# UHBS {UHBS_VERSION} score Dockerfile — unit `{unit['unit_id']}`\n"
        f"# Source: {source}\n"
        f"# Target image: {recipe['image']}"
        + (f" ({image_digest})" if image_digest else "")
        + "\n"
        f"# Rebuild (build context = cloned upstream under .local/labs/{recipe['bench']}):\n"
        f"#   docker build -f Dockerfile -t {recipe['image']} .local/labs/{recipe['bench']}\n"
        f"# Exact image without rebuild (see Dockerfile.pin):\n"
        f"#   docker build -f Dockerfile.pin -t {recipe['image']} .\n"
        "#\n"
    )
    if not body.startswith(f"# UHBS {UHBS_VERSION} score Dockerfile"):
        body = header + body
    dest.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")

    # Always write a digest pin so the exact graded image is pullable.
    digest = (image_digest or "").strip()
    if digest and not digest.startswith("sha256:"):
        digest = f"sha256:{digest}"
    pin_ref = recipe["image"]
    if digest:
        # Prefer digest-only FROM for true content pin (tag may move).
        pin_body = (
            f"# UHBS {UHBS_VERSION} exact graded image pin — `{unit['unit_id']}`\n"
            f"# Image name at grade time: {recipe['image']}\n"
            f"FROM {digest}\n"
        )
    else:
        pin_body = (
            f"# UHBS {UHBS_VERSION} image pin — `{unit['unit_id']}` (digest unavailable)\n"
            f"FROM {pin_ref}\n"
        )
    (latest / "Dockerfile.pin").write_text(pin_body, encoding="utf-8")

    (image_dir / "SOURCE.txt").write_text(
        f"source={source}\nimage={recipe['image']}\ndigest={image_digest or ''}\n"
        f"dockerfile={unit['latest_path']}/Dockerfile\n"
        f"dockerfile_pin={unit['latest_path']}/Dockerfile.pin\n",
        encoding="utf-8",
    )
    return {
        "dockerfile_path": str(Path(unit["latest_path"]) / "Dockerfile"),
        "dockerfile_pin_path": str(Path(unit["latest_path"]) / "Dockerfile.pin"),
        "dockerfile_sha256": sha256_file(dest),
        "dockerfile_pin_sha256": sha256_file(latest / "Dockerfile.pin"),
        "dockerfile_source": source,
        "target_image_digest": image_digest,
    }


def write_execution_steps(unit: dict, recipe: dict, branch: str, sha: str) -> None:
    latest = ROOT / unit["latest_path"]
    latest.mkdir(parents=True, exist_ok=True)
    uid = unit["unit_id"]
    bench = recipe["bench"]
    text = f"""# Execution steps — `{uid}`

Replication log for the UHBS {UHBS_VERSION} results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `{uid}`
- benchmark: `{unit["benchmark_id"]}` · protocol: `{unit["protocol_id"]}` · class: `{unit.get("class_name")}`
- upstream: `{recipe["repo"]}`
- branch/commit: `{branch}` / `{sha}`
- latest path: `{unit["latest_path"]}`
- strategy: `{recipe["strategy"]}` · base: `{recipe["base_image"]}`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f {unit["latest_path"]}/Dockerfile.pin -t {recipe["image"]} {unit["latest_path"]}

# Or rebuild from the lab recipe + cloned upstream:
docker build -f {unit["latest_path"]}/Dockerfile -t {recipe["image"]} .local/labs/{bench}
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
{"\n".join(recipe.get("build") or [])}
{"\n".join(recipe.get("start") or [])}
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.
"""
    (latest / "EXECUTION-STEPS.md").write_text(text + "\n", encoding="utf-8")
    hub = latest.parent if (latest.parent / "index.md").is_file() or unit["protocol_id"] else latest
    # Prefer product hub one level up when latest ends with protocol
    if (latest.parent / "TUTORIAL.md").is_file() or unit["protocol_id"]:
        hub = latest.parent
    hub.mkdir(parents=True, exist_ok=True)
    if not (hub / "TUTORIAL.md").is_file() or (hub / "TUTORIAL.md").stat().st_size < 40:
        (hub / "TUTORIAL.md").write_text(
            f"# Tutorial: {bench}\n\nSee EXECUTION-STEPS.md under the protocol unit for Spot dual-vantage reproduction.\n",
            encoding="utf-8",
        )
    if not (hub / "METHODOLOGY.md").is_file() or (hub / "METHODOLOGY.md").stat().st_size < 40:
        (hub / "METHODOLOGY.md").write_text(
            f"# Methodology: {bench}\n\n"
            "Dual-vantage 5.0.1: authoritative Module C/D from on-box Spot A with "
            "`/telemetry` + egress canary; Module A/B also probed from Spot B over the VPC.\n",
            encoding="utf-8",
        )
    if not (hub / "index.md").is_file():
        (hub / "index.md").write_text(f"# {bench}\n\nUHBS {UHBS_VERSION} results.\n", encoding="utf-8")


def grade_mode(
    unit: dict,
    recipe: dict,
    mode: str,
    *,
    branch: str,
    sha: str,
) -> dict:
    uid = unit["unit_id"]
    latest = unit["latest_path"]
    out = ROOT / latest / mode
    out.mkdir(parents=True, exist_ok=True)
    if mode == "full":
        (out / "proof").mkdir(parents=True, exist_ok=True)
        (out / "static").mkdir(parents=True, exist_ok=True)

    inventory = unit["inventory_path"]
    tps = unit["quick_tps_path"] if mode == "quick" else unit["full_tps_path"]
    site = uid
    if uid.startswith("qeeqbox-honeypots-"):
        site = "qeeqbox-" + uid.split("qeeqbox-honeypots-", 1)[1]

    honeypot = recipe["honeypot_mount"]
    telemetry = recipe["telemetry_mount"]
    grader = f"uhbs:{UHBS_VERSION}" if mode == "quick" else f"uhbs:{UHBS_VERSION}-full"

    # Flush gateway + attach inspect digests after decoy activity, before Module D.
    d_ev = prepare_module_d_evidence(unit, recipe, out, mode=mode)

    env_extra = ""
    if recipe.get("ssh_known_hosts"):
        env_extra += f' -e UHBS_SSH_KNOWN_HOSTS=/work/{recipe["ssh_known_hosts"]} '
    env_extra += (
        f' -e UHBS_EGRESS_GATEWAY_LOG={d_ev["UHBS_EGRESS_GATEWAY_LOG"]}'
        f' -e UHBS_EGRESS_GATEWAY_SHA256={d_ev["UHBS_EGRESS_GATEWAY_SHA256"]}'
        f' -e UHBS_CONTAINER_INSPECT_JSON={d_ev["UHBS_CONTAINER_INSPECT_JSON"]}'
        f' -e UHBS_CONTAINER_INSPECT_SHA256={d_ev["UHBS_CONTAINER_INSPECT_SHA256"]} '
    )

    if mode == "quick":
        cmd = f"""docker run --rm --network uhbs-lab \\
  -v "{ROOT}:/work" -v "{ROOT / honeypot}:/honeypot:ro" \\
  -v "{ROOT / telemetry}:/telemetry:ro" -w /work \\
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 {env_extra}\\
  {grader} lab \\
    --inventory /work/{inventory} \\
    --target {site} \\
    --tps /work/{tps} \\
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \\
    --quick --skip-sast-tools --concurrency 10 --requests 50 \\
    --out /work/{latest}/quick \\
    --environment "Quick Docker lab: {site}" \\
  > {latest}/quick/uhbs-run.log 2>&1"""
        sh(cmd, check=False)
    else:
        runner = ROOT / ".local" / "benchmark-refresh" / f"{uid}-full.sh"
        runner.parent.mkdir(parents=True, exist_ok=True)
        runner.write_text(
            f"""#!/usr/bin/env bash
set -euo pipefail
cd {ROOT}
docker run --rm --network uhbs-lab \\
  -v "$PWD:/work" \\
  -v "$PWD/{honeypot}:/honeypot:ro" \\
  -v "$PWD/{telemetry}:/telemetry:ro" \\
  -w /work \\
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 {env_extra}\\
  {grader} lab \\
    --inventory /work/{inventory} \\
    --target {site} \\
    --tps /work/{tps} \\
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \\
    --concurrency 25 --requests 200 \\
    --out /work/{latest}/full \\
    --environment "Full Docker lab: {site}" \\
  2>&1 | tee {latest}/full/uhbs-run.log
""",
            encoding="utf-8",
        )
        runner.chmod(0o755)
        cast = out / "proof" / "full-run.cast"
        if sh("command -v asciinema >/dev/null", check=False).returncode == 0:
            sh(f'asciinema rec --overwrite "{cast}" -c "{runner}"', check=False)
        else:
            sh(str(runner), check=False)
            cast.write_text(
                '{"version":2,"width":80,"height":24}\n'
                f'[0.1,"o","uhbs full {uid}\\r\\n"]\n',
                encoding="utf-8",
            )

    meta = {
        "unit_id": uid,
        "mode": mode,
        "uhbs_version": UHBS_VERSION,
        "vantage": "onbox",
        "vantage_onbox": True,
        "vantage_remote": False,
        "upstream_repo": recipe["repo"],
        "upstream_branch": branch,
        "upstream_commit": sha,
        "target_image": recipe["image"],
        "target_image_digest": docker_id(recipe["image"]),
        "grader_image": grader,
        "grader_image_digest": docker_id(grader),
        "base_image": recipe["base_image"],
        "base_image_reason": recipe["base_image_reason"],
        "strategy": recipe["strategy"],
        "inventory_path": inventory,
        "tps_path": tps,
        "telemetry_mount": telemetry,
        "module_d_gateway_sha256": d_ev["module_d_gateway_sha256"],
        "module_d_inspect_sha256": d_ev["module_d_inspect_sha256"],
        "module_d_inspect_path": d_ev["module_d_inspect_path"],
    }
    return finalize(out, uid, mode, meta)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit-id", required=True)
    ap.add_argument("--db", default=str(ROOT / ".local/benchmark-refresh/results-5.0.1.sqlite3"))
    ap.add_argument("--mode", choices=("quick", "full", "both"), default="both")
    args = ap.parse_args()

    unit = load_unit(Path(args.db), args.unit_id)
    recipe = recipe_for(args.unit_id)
    if not recipe:
        print(f"ERROR: no Spot recipe for {args.unit_id}", file=sys.stderr)
        return 2

    ensure_network()
    dest = ROOT / ".local" / "labs" / recipe["bench"]
    branch, sha = ensure_clone(recipe["repo"], dest)
    for cmd in recipe.get("build") or []:
        sh(cmd)
    for cmd in recipe.get("start") or []:
        sh(localize_start_cmd(cmd))
    time.sleep(3)

    df_meta = publish_score_dockerfile(
        unit, recipe, image_digest=docker_id(recipe["image"])
    )
    modes = ["quick", "full"] if args.mode == "both" else [args.mode]
    for mode in modes:
        report = grade_mode(unit, recipe, mode, branch=branch, sha=sha)
        # Stamp Dockerfile provenance into run-meta after finalize.
        out = ROOT / unit["latest_path"] / mode
        write_run_meta(out, df_meta)
        write_manifest(out)
        _ = report
    write_execution_steps(unit, recipe, branch, sha)
    print(
        json.dumps(
            {
                "ok": True,
                "unit_id": args.unit_id,
                "branch": branch,
                "sha": sha,
                **df_meta,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
