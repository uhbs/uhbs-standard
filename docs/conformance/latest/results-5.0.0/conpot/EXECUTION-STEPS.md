# Execution steps — `conpot-modbus`

- upstream: `https://github.com/mushorg/conpot.git` · `main` · `35e2dfeca70c3b7d961843bd08f35529a75eaed2`
- Docs reviewed: README.md, Dockerfile, docker-compose.yml, docs/

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/mushorg/conpot.git .local/labs/conpot
docker build -t conpot:lab .local/labs/conpot
docker build -f docs/conformance/labs/conpot/Dockerfile.lab -t conpot:lab-fixed .
docker run -d --name uhbs-target-conpot-modbus --network uhbs-lab --network-alias conpot-lab -p 127.0.0.1:502:5020 conpot:lab-fixed
# wait for ModbusServer listening on 0.0.0.0:5020

UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/conpot:/honeypot:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab --inventory /work/docs/conformance/labs/conpot/inventory.yaml \
  --target conpot --tps /work/docs/conformance/labs/conpot/ics_modbus_quick.yaml \
  --quick --skip-sast-tools --out /work/docs/conformance/latest/results-5.0.0/conpot/quick

# seed FC01; docker cp /var/log/conpot; write egress-gateway.log

asciinema rec --overwrite docs/conformance/latest/results-5.0.0/conpot/full/proof/full-run.cast \
  -c .local/benchmark-refresh/conpot-full.sh
# full uses --concurrency 5 --requests 50 (default 25x200 stalls Conpot serial Modbus)

uhbs validate-scorecard docs/conformance/fixtures/conpot-ics-scada.scorecard.json --strict
python scripts/validate_unit.py --unit-id conpot-modbus
```

Runtime: `upstream-docker` + lab wrapper `setuptools<81`. Honest UHBS 5.0.0: **INCOMPLETE / ungraded**.
