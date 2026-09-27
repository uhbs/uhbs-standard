# Execution steps — `espot-http`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `espot-http`
- benchmark: `espot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/mycert/ESPot.git`
- default branch: `master`
- commit: `0b126a7783da69d543239606df59211c5d21f1db`
- workspace clone: `.local/labs/espot`
- telemetry: `.local/labs/espot-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/espot`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/mycert/ESPot.git .local/labs/espot
git -C .local/labs/espot rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/espot rev-parse HEAD                # 0b126a7783da69d543239606df59211c5d21f1db
```

Docs reviewed: `README.md` (requires NodeJS v0.10.x / npm 1.4.x), `package.json`, `config.js-sample`. No upstream Dockerfile.

## 2. Runtime decision

`custom-base` / `node:10-buster-slim`. Ubuntu latest cannot install Node 0.10; `sqlite3@2` fails on modern Node. Lab `config.js` disables SQLite logging. Wrapper Dockerfile next to the clone:

```dockerfile
FROM node:10-buster-slim
WORKDIR /opt/espot
RUN npm install --production express@3.16.5 ejs@2.7.4 request@2.88.2 \
 && npm cache clean --force
COPY . .
EXPOSE 9200
CMD ["node", "app.js"]
```

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
docker rm -f uhbs-target-espot-http 2>/dev/null || true
docker build -t espot:lab .local/labs/espot
docker run -d --name uhbs-target-espot-http --network uhbs-lab \
  --network-alias espot-lab -p 127.0.0.1:9200:9200 espot:lab
curl -sS -m 5 http://127.0.0.1:9200/
# expect JSON with "tagline": "You Know, for Search"
```

## 4. Quick run (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id espot-http --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image espot:lab \
  --base-image node:10-buster-slim --strategy custom-base --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/espot:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/espot/inventory.yaml \
    --target espot \
    --tps /work/docs/conformance/labs/espot/web_api_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.0/espot/quick \
    --environment "Quick Docker lab: ESPot HTTP :9200, UHBS_QUICK=1, SAST skipped" \
  > docs/conformance/latest/results-5.0.0/espot/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
mkdir -p .local/labs/espot-telemetry
for i in $(seq 1 30); do
  curl -sS -o /dev/null "http://127.0.0.1:9200/"
  curl -sS -o /dev/null "http://127.0.0.1:9200/_search?q=uhbs$i"
  curl -sS -o /dev/null -X PUT "http://127.0.0.1:9200/idx/doc/$i" \
    -H 'Content-Type: application/json' -d "{\"probe\":$i}"
done
docker cp uhbs-target-espot-http:/opt/espot/logs/. .local/labs/espot-telemetry/
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/espot-telemetry/egress-gateway.log
```

## 6. Full run + asciinema (`uhbs:5.0.0-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id espot-http --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image espot:lab \
  --base-image node:10-buster-slim --strategy custom-base --airgap-attested

asciinema rec --overwrite docs/conformance/latest/results-5.0.0/espot/full/proof/full-run.cast \
  -c .local/benchmark-refresh/espot-full.sh
```

`espot-full.sh` runs:

```bash
UHBS_AIRGAP_ATTESTED=1 UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/espot:/honeypot:ro" \
  -v "$PWD/.local/labs/espot-telemetry:/telemetry:ro" \
  -w /work -e PYTHONUNBUFFERED=1 \
  -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.0-full lab \
    --inventory /work/docs/conformance/labs/espot/inventory.yaml \
    --target espot \
    --tps /work/docs/conformance/labs/espot/web_api_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.0/espot/full \
    --environment "Full Docker lab: ESPot HTTP :9200 + 1000-sample A3 + SAST + telemetry"
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/espot-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id espot-http
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/espot/quick/`
- full: `docs/conformance/latest/results-5.0.0/espot/full/`
- cast: `docs/conformance/latest/results-5.0.0/espot/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/espot-web-api.scorecard.json`

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded** (Module C declared-format + Module D non-SSH gateway/packet evidence not fully measured). Do not copy archived 4.x UHQS 63.33 / D.
