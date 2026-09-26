# Execution steps — `dionaea-http`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `dionaea-http`
- benchmark: `dionaea` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/dinotools/dionaea.git`
- default branch: `master`
- commit: `4e459f1b672a5b4c1e8335c0bff1b93738019215`
- workspace clone: `.local/labs/dionaea`
- telemetry: `.local/labs/dionaea-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/dionaea/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 \
  https://github.com/dinotools/dionaea.git .local/labs/dionaea
git -C .local/labs/dionaea rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/dionaea rev-parse HEAD                # 4e459f1b672a5b4c1e8335c0bff1b93738019215
```

Docs reviewed: `README.md`, `Dockerfile` (`FROM ubuntu:18.04`), `docker/README.md` (official `dinotools/dionaea` image, `linux/amd64`).

## 2. Runtime decision

`upstream-docker`. Upstream publishes `dinotools/dionaea:latest` and documents `docker run` in `docker/README.md`. Base image is `ubuntu:18.04` from the repo Dockerfile. Image is `linux/amd64`; on Apple Silicon use `--platform linux/amd64`.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/dionaea-telemetry
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/dionaea-telemetry/egress-gateway.log
docker pull --platform linux/amd64 dinotools/dionaea:latest
docker run -d \
  --name uhbs-target-dionaea \
  --network uhbs-lab \
  --network-alias dionaea-lab \
  --platform linux/amd64 \
  -v "$PWD/.local/labs/dionaea-telemetry:/opt/dionaea/var/log/dionaea" \
  -v "$PWD/.local/labs/dionaea-telemetry:/telemetry:rw" \
  dinotools/dionaea:latest
```

Smoke: `dionaea-lab:21`, `:80`, `:445` open.

## 4. Quick (`uhbs:5.0.0`) / 5. Telemetry / 6. Full + asciinema (`uhbs:5.0.0-full`)

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/dionaea:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab --inventory /work/docs/conformance/labs/dionaea/inventory.yaml \
    --target dionaea-http --tps /work/docs/conformance/labs/dionaea/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/dionaea/http/quick \
    --environment "Quick Docker lab: dionaea-http"

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/dionaea/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/run_dionaea_http_full.sh
```

Full grader `uhbs:5.0.0-full`, TPS `docs/conformance/labs/dionaea/web_api_http_full.yaml`, `--concurrency 25 --requests 200`, `UHBS_AIRGAP_ATTESTED=1`, `UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log`.

## 7. Fixture + verifier

```bash
.venv/bin/uhbs validate-scorecard docs/conformance/fixtures/dionaea-http.scorecard.json --strict
python scripts/validate_unit.py --unit-id dionaea-http
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/dionaea/http/quick/`
- full: `docs/conformance/latest/results-5.0.0/dionaea/http/full/`
- cast: `docs/conformance/latest/results-5.0.0/dionaea/http/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/dionaea-http.scorecard.json`

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded**. Do not copy archived 4.x 66.02 / D.
