# Execution steps — `miniprint-pjl`

- unit_id: `miniprint-pjl` · class `Low-Interaction` · protocol `pjl`
- upstream: `https://github.com/sa7mon/miniprint.git` · `master` · `494d2fc75b94c19345c2db55d03b5cf74f75e3c2`

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/sa7mon/miniprint.git .local/labs/miniprint
# Docs reviewed: readme.md, Dockerfile (python:3.7-alpine), server.py
docker build -t miniprint:lab .local/labs/miniprint
docker run -d --name uhbs-target-miniprint-pjl --network uhbs-lab --network-alias miniprint-lab -p 127.0.0.1:9100:9100 miniprint:lab

UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/miniprint:/honeypot:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab --inventory /work/docs/conformance/labs/miniprint/inventory.yaml \
  --target miniprint --tps /work/docs/conformance/labs/miniprint/low_interaction_quick.yaml \
  --quick --skip-sast-tools --out /work/docs/conformance/latest/results-5.0.0/miniprint/quick

# seed PJL INFO ID/STATUS; docker cp /app/miniprint.log; write egress-gateway.log

asciinema rec --overwrite docs/conformance/latest/results-5.0.0/miniprint/full/proof/full-run.cast \
  -c .local/benchmark-refresh/miniprint-full.sh

uhbs validate-scorecard docs/conformance/fixtures/miniprint-low-interaction.scorecard.json --strict
python scripts/validate_unit.py --unit-id miniprint-pjl
```

Runtime: `upstream-docker` / `python:3.7-alpine` (upstream Dockerfile). Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded**.
