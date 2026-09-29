# Execution steps — `mailoney-smtp`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `mailoney-smtp`
- benchmark: `mailoney` · protocol: `smtp` · class: `Low-Interaction`
- upstream: `https://github.com/phin3has/mailoney.git`
- default branch: `main`
- commit: `b8310a7019dd0ba00c666e5185bee3c1dd851e19`
- latest path: `docs/conformance/latest/results-5.0.1/mailoney/smtp`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/phin3has/mailoney.git .local/labs/mailoney
git -C .local/labs/mailoney rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/mailoney rev-parse HEAD                # b8310a7019dd0ba00c666e5185bee3c1dd851e19
```

Docs reviewed: `README.md` (Docker + sqlite/postgres), `Dockerfile` (`FROM python:3.11-slim`).

## 2. Runtime

Strategy `upstream-docker`. Base `python:3.11-slim`. SQLite lab (`MAILONEY_DB_URL=sqlite:////tmp/mailoney.db`) — no Postgres sidecar. Non-root image needs `NET_BIND_SERVICE` to listen on `:25`.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t mailoney:uhbs-lab .local/labs/mailoney
docker run -d --name uhbs-target-mailoney-smtp --network uhbs-lab --network-alias mailoney-lab \
  --cap-add NET_BIND_SERVICE \
  -e MAILONEY_BIND_IP=0.0.0.0 -e MAILONEY_BIND_PORT=25 \
  -e MAILONEY_DB_URL=sqlite:////tmp/mailoney.db \
  mailoney:uhbs-lab
# expect: SMTP Honeypot listening on 0.0.0.0:25
```

## 4. Quick (`uhbs:5.0.1`)

```bash
UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/mailoney:/honeypot:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/mailoney/inventory.yaml \
    --target mailoney-smtp \
    --tps /work/docs/conformance/labs/mailoney/low_interaction_smtp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/mailoney/smtp/quick
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/mailoney/smtp/full/proof/full-run.cast \
  -c .local/benchmark-refresh/mailoney-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/mailoney-smtp.scorecard.json --strict
python scripts/validate_unit.py --unit-id mailoney-smtp
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded**. Module C declared-format + Module D non-SSH gateway/packet evidence. Do not copy archived 4.x 38.69 / F.
