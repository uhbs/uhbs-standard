# Execution steps — `trapster-ftp`

Same clone/image/container as `trapster-ssh` (`main` @ `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`, `trapster:uhbs-lab`, alias `trapster-lab:2121`). See [`../ssh/EXECUTION-STEPS.md`](../ssh/EXECUTION-STEPS.md) for clone/build.

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id trapster-ftp --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image trapster:uhbs-lab \
  --base-image python:3.11-slim --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/trapster:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/trapster/inventory.yaml \
    --target trapster-ftp \
    --tps /work/docs/conformance/labs/trapster/low_interaction_ftp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/trapster/ftp/quick \
    --environment "Quick Docker lab: trapster-ftp" \
  > docs/conformance/latest/results-5.0.0/trapster/ftp/quick/uhbs-run.log 2>&1

docker logs uhbs-target-trapster > .local/labs/trapster-telemetry/trapster.log 2>&1

python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id trapster-ftp --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image trapster:uhbs-lab \
  --base-image python:3.11-slim --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/trapster/ftp/full/proof/full-run.cast \
  -c .local/benchmark-refresh/run_trapster_ftp_full.sh
```

Full grader: `uhbs:5.0.0-full lab --target trapster-ftp --tps .../low_interaction_ftp_full.yaml --out .../trapster/ftp/full` with honeypot + telemetry mounts and `UHBS_AIRGAP_ATTESTED=1`.

```bash
uhbs validate-scorecard docs/conformance/fixtures/trapster-ftp.scorecard.json --strict
python scripts/validate_unit.py --unit-id trapster-ftp
```

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded**. Do not copy archived 4.x UHQS 51.78 / D.
