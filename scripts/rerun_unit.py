#!/usr/bin/env python3
"""Re-run one results-5.0.1 unit with a full, safe target lifecycle.

The Sep-27 wave graded many units against targets that were never started or
not configured for the unit's protocol, producing Module A = 0 scorecards.
This driver makes that impossible by construction:

    1. ensure the uhbs-lab Docker network exists
    2. verify the target image exists (clear error + build hint otherwise)
    3. start the target container: alias, telemetry rw mount, extra mounts/env
    4. capture container-inspect + egress-gateway evidence with sha256 pins
    5. PREFLIGHT (scripts/preflight_unit.py, in-network) until --wait expires
       -> on failure: dump `docker logs`, tear down, exit 1. Nothing is graded.
    6. grade quick (uhbs:5.0.1) and/or full (uhbs:5.0.1-full, + asciinema cast)
    7. tear the target down
    8. run scripts/validate_unit.py and print the resulting UHQS

Unit coordinates (inventory/TPS/paths/alias/port) come from the benchmark
SQLite ledger; the target launcher comes from CLI flags or a runbook YAML:

    python scripts/rerun_unit.py --unit dionaea-sip \
        --image dinotools/dionaea:latest \
        --mount .local/labs/dionaea/sip.yaml:/opt/dionaea/etc/dionaea/dionaea.cfg:ro

    python scripts/rerun_unit.py --unit opencanary-ssh --runbook rerun-runbook.yaml

Preflight-only triage (no grading, no target teardown until after the probe):

    python scripts/rerun_unit.py --unit cowrie-ssh --preflight-only ...
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".local" / "benchmark-refresh" / "results-5.0.1.sqlite3"
PREFLIGHT = ROOT / "scripts" / "preflight_unit.py"
VALIDATE = ROOT / "scripts" / "validate_unit.py"
sys.path.insert(0, str(ROOT / "src"))

QUICK_GRADER = "uhbs:5.0.1"
FULL_GRADER = "uhbs:5.0.1-full"
NETWORK = "uhbs-lab"


def sh(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    printable = " ".join(shlex.quote(c) for c in cmd)
    print(f"+ {printable}", flush=True)
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unit(db: Path, unit_id: str) -> dict:
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM benchmark_units WHERE unit_id=?", (unit_id,)).fetchone()
    con.close()
    if row is None:
        avail = [r[0] for r in sqlite3.connect(str(db)).execute(
            "SELECT unit_id FROM benchmark_units ORDER BY unit_id")]
        raise SystemExit(f"unknown unit {unit_id!r}. Known units: {', '.join(avail)}")
    return dict(row)


def load_runbook(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"runbook not found: {path}")
    try:
        import yaml  # noqa: PLC0415 - optional only for runbook mode
    except ImportError as exc:
        raise SystemExit("PyYAML required for --runbook") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("units") or {}


def site_telemetry_dir(inventory: Path, site: str) -> str:
    """The site's declared telemetry_dir (Module C reads exactly this path).

    Most inventories declare /telemetry; a few declare the product's native
    log dir (kippo /app/log, artillery /var/artillery/logs, pyrdp
    /home/pyrdp/pyrdp_output). The grader must see the sink mounted THERE.
    """
    try:
        from uhbs_core.inventory import load_inventory

        spec = load_inventory(inventory).get(site)
        return str(getattr(spec, "telemetry_dir", None) or "/telemetry")
    except Exception:  # noqa: BLE001 - fall back to the conventional path
        return "/telemetry"


def site_for(unit: dict, inventory_path: Path) -> str:
    """Inventory site id: unit_id, else unique protocol/port match."""
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT), "--inventory", str(inventory_path),
         "--site", unit["unit_id"], "--protocol", unit["protocol_id"],
         "--resolve-site-only", "--json"],
        check=False, capture_output=True, text=True,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {}
    if payload.get("site"):
        return str(payload["site"])
    raise SystemExit(
        f"cannot resolve site for {unit['unit_id']} in {inventory_path}: "
        f"{payload.get('error') or 'unknown error'}"
    )


def preflight(unit: dict, inventory: Path, tps: Path, site: str, *, timeout: float) -> dict:
    cmd = [
        "docker", "run", "--rm", "--network", NETWORK,
        "-v", f"{ROOT}:/work", "-w", "/work",
        "--entrypoint", "python3", QUICK_GRADER,
        str(PREFLIGHT.relative_to(ROOT)),
        "--inventory", f"/work/{inventory.relative_to(ROOT)}",
        "--site", site,
        "--json",
        "--timeout", str(timeout),
    ]
    if tps and Path(tps).is_file():
        cmd += ["--tps", f"/work/{Path(tps).relative_to(ROOT)}"]
    proc = sh(cmd, check=False, capture=True)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "class": "preflight_crashed", "error": proc.stdout[-2000:]}


def seed_evidence(container: str, mode_out: Path, telemetry: Path) -> dict[str, str]:
    """container-inspect + egress-gateway canary, exactly like the wave did."""
    evidence = mode_out / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    inspect_path = evidence / "container-inspect.json"
    inspect_path.write_text(
        subprocess.check_output(["docker", "inspect", container], text=True), encoding="utf-8"
    )
    telemetry.mkdir(parents=True, exist_ok=True)
    egress = telemetry / "egress-gateway.log"
    if not egress.exists():
        egress.write_text(
            "# UHBS egress gateway canary — no HIT lines means clean\n", encoding="utf-8"
        )
    return {
        "UHBS_CONTAINER_INSPECT_JSON": f"/work/{inspect_path.relative_to(ROOT)}",
        "UHBS_CONTAINER_INSPECT_SHA256": sha256_file(inspect_path),
        "UHBS_EGRESS_GATEWAY_LOG": "/telemetry/egress-gateway.log",
        "UHBS_EGRESS_GATEWAY_SHA256": sha256_file(egress),
    }


def _in_container(path: str | Path) -> str:
    """Map a repo path (absolute or repo-relative) to its /work location."""
    p = Path(path)
    if not p.is_absolute():
        return f"/work/{p}"
    return f"/work/{p.relative_to(ROOT)}"


def grade(unit: dict, mode: str, *, site: str, launcher: dict, env_pins: dict[str, str],
          concurrency: int, requests: int, cast: bool) -> None:
    latest = ROOT / unit["latest_path"]
    out = latest / mode
    out.mkdir(parents=True, exist_ok=True)
    (out / "proof").mkdir(exist_ok=True)
    (out / "static").mkdir(exist_ok=True)

    env = ["PYTHONUNBUFFERED=1", "UHBS_AIRGAP_ATTESTED=1", *(f"{k}={v}" for k, v in env_pins.items())]
    tps_key = "quick_tps_path" if mode == "quick" else "full_tps_path"
    tps = unit.get(tps_key) or unit.get("full_tps_path")
    sink = ROOT / launcher["telemetry"]
    # Module C reads the inventory-declared telemetry_dir — mount the sink
    # there too (kippo /app/log, artillery /var/artillery/logs, …), not just
    # at the conventional /telemetry.
    declared = site_telemetry_dir(ROOT / unit["inventory_path"], site)
    sink_mounts = [f"{sink}:/telemetry:ro"]
    if declared != "/telemetry":
        sink_mounts.append(f"{sink}:{declared}:ro")

    cmd = [
        "docker", "run", "--rm", "--network", NETWORK,
        "-v", f"{ROOT}:/work",
        "-v", f"{ROOT / launcher.get('source_root', '.local/labs/' + unit['benchmark_id'])}:/honeypot:ro",
        *itertools.chain.from_iterable(["-v", m] for m in sink_mounts),
        "-w", "/work",
        *itertools.chain.from_iterable(["-e", e] for e in env),
        FULL_GRADER if mode == "full" else QUICK_GRADER,
        "lab",
        "--inventory", _in_container(unit["inventory_path"]),
        "--target", site,
        *(["--tps", _in_container(tps)] if tps else []),
        "--phases", "profile,static,sandbox,dynamic,score",
        "--modules", "A,B,C,D,E,F",
        "--concurrency", str(concurrency),
        "--requests", str(requests),
        "--out", _in_container(out),
        "--environment", f"{mode.capitalize()} Docker lab: {site}",
    ]
    if mode == "quick":
        cmd += ["--quick", "--skip-sast-tools"]

    log_path = out / "uhbs-run.log"
    if cast and mode == "full" and shutil.which("asciinema"):
        cast_path = out / "proof" / "full-run.cast"
        cmd = ["asciinema", "rec", "--overwrite", str(cast_path), "-c",
               " ".join(shlex.quote(c) for c in cmd)]

    print(f"=== grading {unit['unit_id']} [{mode}] -> {out.relative_to(ROOT)}", flush=True)
    with log_path.open("w") as logf:
        proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        print(f"grader exited {proc.returncode}; tail of {log_path.relative_to(ROOT)}:")
        print("".join(log_path.read_text().splitlines(keepends=True)[-25:]))
    else:
        print(f"graded ok; log: {log_path.relative_to(ROOT)}", flush=True)


def track_run(unit: dict, mode: str, image: str | None, grader: str) -> None:
    """Record the run in the benchmark ledger (log-run-start + log-run-finish)."""
    out_dir = ROOT / unit["latest_path"] / mode
    tracker = [sys.executable, str(ROOT / "scripts" / "tracker.py")]
    sh([*tracker, "log-run-start", "--unit-id", unit["unit_id"], "--mode", mode,
        "--uhbs-version", "5.0.1", "--grader-image", grader,
        *(["--target-image", image] if image else []),
        "--telemetry-mode", "mounted", "--airgap-attested"], check=False)
    finish = [*tracker, "log-run-finish", "--unit-id", unit["unit_id"], "--mode", mode,
              "--out-dir", str(out_dir)]
    cast = out_dir / "proof" / "full-run.cast"
    if mode == "full" and cast.is_file():
        finish += ["--cast-path", str(cast)]
    sh(finish, check=False)


def summarize(unit: dict) -> None:
    latest = ROOT / unit["latest_path"]
    for mode in ("quick", "full"):
        rj = latest / mode / "report.json"
        if not rj.is_file():
            continue
        try:
            u = (json.loads(rj.read_text()) or {}).get("uhqs") or {}
        except json.JSONDecodeError:
            print(f"  {mode}: report.json unreadable")
            continue
        print(f"  {mode}: UHQS={u.get('uhqs')} grade={str(u.get('grade', '')).replace('GRADE ', '')}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--unit", required=True, help="unit_id in benchmark_units")
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument("--runbook", type=Path, default=None,
                   help="YAML with per-unit launcher overrides")
    # target launcher
    p.add_argument("--image", help="target image (else runbook['image'])")
    p.add_argument("--alias", help="network alias (else inventory host from DB)")
    p.add_argument("--container-name", help="default uhbs-target-<unit>")
    p.add_argument("--env", action="append", default=[], help="target env K=V (repeatable)")
    p.add_argument("--mount", action="append", default=[],
                   help="extra target mount host:container[:ro] (repeatable)")
    p.add_argument("--publish", type=int, default=None,
                   help="publish container port to localhost for debugging")
    p.add_argument("--cmd", default=None, help="override target CMD (quoted string)")
    p.add_argument("--wire-log", default=None,
                   help="container path of the product's native log dir; the telemetry "
                        "sink is mounted there (rw) so Module C can measure it")
    # lifecycle
    p.add_argument("--wait", type=int, default=60, help="preflight wait seconds (default 60)")
    p.add_argument("--probe-timeout", type=float, default=3.0)
    p.add_argument("--modes", default="both", choices=["quick", "full", "both"])
    p.add_argument("--preflight-only", action="store_true",
                   help="triage: probe the target, never grade")
    p.add_argument("--reuse-target", action="store_true",
                   help="target already running; skip start/teardown (e.g. live dionaea)")
    p.add_argument("--keep-target", action="store_true", help="do not tear down after run")
    p.add_argument("--concurrency", type=int, default=25)
    p.add_argument("--requests", type=int, default=200)
    p.add_argument("--no-cast", action="store_true", help="skip asciinema cast for full")
    p.add_argument("--no-validate", action="store_true")
    p.add_argument("--track", action="store_true",
                   help="record runs in the benchmark SQLite ledger (log-run-start/finish)")
    args = p.parse_args(argv)

    unit = load_unit(args.db, args.unit)
    launcher = {}
    if args.runbook:
        launcher = load_runbook(args.runbook).get(args.unit) or {}
        if not launcher:
            print(f"note: runbook has no entry for {args.unit}; CLI flags only")
    image = args.image or launcher.get("image")
    alias = args.alias or launcher.get("alias") or unit.get("target_host") or f"{unit['benchmark_id']}-lab"
    container = args.container_name or f"uhbs-target-{args.unit}"
    telemetry = ROOT / launcher.get("telemetry", f".local/labs/{unit['benchmark_id']}-telemetry")
    env = [*args.env, *(f"{k}={v}" for k, v in (launcher.get("env") or {}).items())]
    mounts = [*args.mount, *(
        f"{ROOT / m.split(':')[0]}:{':'.join(m.split(':')[1:])}"
        for m in (launcher.get("mounts") or [])
    )]
    inventory = ROOT / unit["inventory_path"]
    # Telemetry wiring: every honeypot logs somewhere — route its native log
    # directory into the graded sink so Module C can measure it (C1 parse /
    # C2 injection markers / C4 ground truth all need records in the sink).
    log_paths: list[str] = [args.wire_log] if args.wire_log else []
    if launcher.get("log_path"):
        log_paths.append(str(launcher["log_path"]))
    if isinstance(launcher.get("log_paths"), list):
        log_paths.extend(str(p) for p in launcher["log_paths"])
    mounts.extend(f"{telemetry}:{p}:rw" for p in dict.fromkeys(log_paths))

    # Site resolution is inventory-only — do it before the container starts so
    # the declared telemetry_dir can be wired into the target as well.
    site = site_for(unit, inventory)
    declared = site_telemetry_dir(inventory, site)
    if declared != "/telemetry" and declared not in log_paths:
        mounts.append(f"{telemetry}:{declared}:rw")
    print(f"site resolved: {site} (alias {alias}, telemetry_dir {declared})", flush=True)

    sh(["docker", "network", "create", NETWORK], check=False)

    if not args.reuse_target:
        if not image:
            raise SystemExit(
                f"no target image for {args.unit}. Pass --image or add it to the runbook "
                f"(see RERUN-TUTORIAL.md §per-product launchers)."
            )
        inspect = subprocess.run(["docker", "image", "inspect", image],
                                 capture_output=True)  # noqa: S603
        if inspect.returncode != 0:
            raise SystemExit(
                f"target image {image} not built/pulled. Build it first "
                f"(RERUN-TUTORIAL.md §step 2), then re-run."
            )
        sh(["docker", "rm", "-f", container], check=False)
        run_cmd = [
            "docker", "run", "-d", "--name", container,
            "--label", f"uhbs.unit={args.unit}",
            "--network", NETWORK, "--network-alias", alias,
            "-v", f"{telemetry}:/telemetry:rw",
            *(["-p", f"{args.publish}:{unit['target_port']}"]
              if args.publish and unit.get("target_port") else []),
            *itertools.chain.from_iterable(["-e", e] for e in env),
            *itertools.chain.from_iterable(["-v", m] for m in mounts),
            image,
        ]
        if args.cmd or launcher.get("cmd"):
            run_cmd += shlex.split(args.cmd or launcher["cmd"])
        sh(run_cmd)

    try:
        # Preflight retry loop (site already resolved before container start)
        deadline = time.time() + args.wait
        pf: dict = {}
        attempt = 0
        while time.time() < deadline:
            attempt += 1
            tps = unit.get("full_tps_path") or ""
            pf = preflight(unit, inventory, ROOT / tps if tps else None, site,
                           timeout=args.probe_timeout)
            if pf.get("ok"):
                break
            detail = pf.get("error") or "; ".join(
                f"{r['protocol']}:{r['class']}" for r in pf.get("results") or [])
            print(f"preflight attempt {attempt}: {detail}", flush=True)
            time.sleep(5)

        if not pf.get("ok"):
            print(f"\nPREFLIGHT FAILED for {args.unit} — nothing graded.", flush=True)
            print(json.dumps(pf, indent=2))
            if not args.reuse_target:
                print(f"\ndocker logs {container} (tail):", flush=True)
                sh(["docker", "logs", "--tail", "80", container], check=False)
            return 1

        print(f"preflight PASS: {json.dumps(pf.get('results'))}", flush=True)
        if args.preflight_only:
            print("preflight-only mode: done.")
            return 0

        for mode in (("quick", "full") if args.modes == "both" else (args.modes,)):
            env_pins = {} if args.reuse_target else seed_evidence(container, ROOT / unit["latest_path"] / mode, telemetry)
            grade(unit, mode, site=site, launcher={
                "source_root": launcher.get("source_root", f".local/labs/{unit['benchmark_id']}"),
                "telemetry": str(telemetry.relative_to(ROOT)),
            }, env_pins=env_pins, concurrency=args.concurrency,
                requests=50 if mode == "quick" else args.requests,
                cast=not args.no_cast)
            if args.track:
                track_run(unit, mode, image, FULL_GRADER if mode == "full" else QUICK_GRADER)
    finally:
        if not args.reuse_target and not args.keep_target:
            sh(["docker", "rm", "-f", container], check=False)

    if not args.no_validate:
        v = subprocess.run([sys.executable, str(VALIDATE), "--unit-id", args.unit,
                            "--db", str(args.db)], capture_output=True, text=True)
        print(f"validate_unit: exit {v.returncode}")
        if v.returncode != 0:
            print((v.stdout or "") + (v.stderr or ""))
    print(f"\n=== {args.unit} summary")
    summarize(unit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
