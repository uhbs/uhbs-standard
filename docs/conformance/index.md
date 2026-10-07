# Published grades (conformance)

**Status:** Normative (fixtures) / Informative (narrative + lab reports)

!!! warning "UHBS v4.6.1 historical scoring model"
    Lab report pages under `docs/conformance/reports/` keep stable URLs and may
    cite DOI-era grades under UHQS 4.x. They are **historical**. New evaluations
    use UHBS **5.0.1** / `scoring_model_id=uhqs-v5.0-critical-gate-diagnostic`
    ([RFC 0003](../rfcs/0003-scoring-assurance.md)). Archived v4 fixtures:
    [`archive/v4.6.1/`](https://github.com/uhbs/uhbs-standard/tree/main/docs/conformance/archive/v4.6.1).

This section is **evaluation proof**: finished scorecards and Docker lab recipes
for named honeypots. It is **not** the “how to install UHBS” guide.

!!! tip "Looking for install / CLI steps?"
    Start here instead: **[Install & use UHBS](../tooling/install-and-use.md)**.

| Page type | Meaning |
| --- | --- |
| **Report hub** | Published quick / full UHQS for one product |
| **Reproduce grade** | Exact Docker commands used to produce that grade |
| **Methodology** | Trust notes / provenance for the run |

Fixtures and **published lab reports** are the only place in the public docs
where specific deception products are named — as evaluation proof (not as UHBS
requirements).

Optional controlled comparative evidence (VoD / FSV / DTDR / EER) lives in the
[Advanced Evidence Profile](../advanced-evidence/index.md) and does **not** alter
these UHQS fixtures.

## Lab reports (reproduce published grades)

Published quick + full Docker grades, reproduce recipes, and provenance:

**→ [reports/index.md](reports/index.md)**

| Honeypot | Quick | Full | Reproduce grade |
| --- | --- | --- | --- |
| [ESPot](latest/results-5.0.1/espot/index.md) | [30.53 / F](latest/results-5.0.1/espot/quick/README.md) | [31.09 / F](latest/results-5.0.1/espot/full/README.md) | [recipe](latest/results-5.0.1/espot/TUTORIAL.md) |
| [miniprint](latest/results-5.0.1/miniprint/index.md) | [12.86 / F](latest/results-5.0.1/miniprint/quick/README.md) | [12.86 / F](latest/results-5.0.1/miniprint/full/README.md) | [recipe](latest/results-5.0.1/miniprint/TUTORIAL.md) |
| [HoneyUp](latest/results-5.0.1/honeyup/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/honeyup/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/honeyup/http/index.md) | [recipe](latest/results-5.0.1/honeyup/TUTORIAL.md) |
| [flux](latest/results-5.0.1/flux/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/flux/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/flux/http/index.md) | [recipe](latest/results-5.0.1/flux/TUTORIAL.md) |
| [Elastichoney](latest/results-5.0.1/elastichoney/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/elastichoney/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/elastichoney/http/index.md) | [recipe](latest/results-5.0.1/elastichoney/TUTORIAL.md) |
| [wordpot](latest/results-5.0.1/wordpot/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/wordpot/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/wordpot/http/index.md) | [recipe](latest/results-5.0.1/wordpot/TUTORIAL.md) |
| [express-honeypot](latest/results-5.0.1/express-honeypot/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/express-honeypot/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/express-honeypot/http/index.md) | [recipe](latest/results-5.0.1/express-honeypot/TUTORIAL.md) |
| [HellPot](latest/results-5.0.1/HellPot/http/index.md) | [40.32 / F](latest/results-5.0.1/HellPot/http/quick/README.md) | [39.59 / F](latest/results-5.0.1/HellPot/http/full/README.md) | [recipe](latest/results-5.0.1/HellPot/TUTORIAL.md) |
| [Beelzebub](latest/results-5.0.1/beelzebub/index.md) | [9.72 / F](latest/results-5.0.1/beelzebub/redis/quick/README.md) | [16.46 / F](latest/results-5.0.1/beelzebub/redis/full/README.md) | [recipe](latest/results-5.0.1/beelzebub/TUTORIAL.md) |
| [HoneyHTTPD](latest/results-5.0.1/honeyhttpd/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/honeyhttpd/http/index.md) | [ungraded](../conformance/latest/results-5.0.1/honeyhttpd/http/index.md) | [recipe](latest/results-5.0.1/honeyhttpd/TUTORIAL.md) |
| [Log4Pot](latest/results-5.0.1/Log4Pot/http/index.md) | [35.54 / F](latest/results-5.0.1/Log4Pot/http/quick/README.md) | [33.94 / F](latest/results-5.0.1/Log4Pot/http/full/README.md) | [recipe](latest/results-5.0.1/Log4Pot/TUTORIAL.md) |
| [Conpot](latest/results-5.0.1/conpot/index.md) | [59.46 / D](latest/results-5.0.1/conpot/quick/README.md) | [61.94 / D](latest/results-5.0.1/conpot/full/README.md) | [recipe](latest/results-5.0.1/conpot/TUTORIAL.md) |
| [Cowrie](reports/cowrie/index.md) | [82.76 / B](reports/cowrie/ssh/quick/README.md) | [61.37 / D](reports/cowrie/ssh/full/README.md) | [recipe](reports/cowrie/TUTORIAL.md) |
| [Endlessh](reports/endlessh/index.md) | [46.55 / F](reports/endlessh/quick/README.md) | [54.07 / D](reports/endlessh/full/README.md) | [recipe](reports/endlessh/TUTORIAL.md) |
| [EchidraOSS](reports/echidra/index.md) | [57.33 / D](reports/echidra/quick/README.md) | [43.45 / F](reports/echidra/full/README.md) | [recipe](reports/echidra/TUTORIAL.md) |
| [OpenCanary](reports/opencanary/index.md) | see hub | see hub | [recipe](reports/opencanary/TUTORIAL.md) |

## Fixtures

| Fixture | Proof target | Expected UHQS | Grade |
| --- | --- | --- | --- |
| [`fixtures/cowrie-low-interaction.scorecard.json`](fixtures/cowrie-low-interaction.scorecard.json) | Cowrie (SSH / Low-Interaction, **full** lab) | 61.37 | D |
| [`fixtures/posix-shell-lab.scorecard.json`](fixtures/posix-shell-lab.scorecard.json) | CyberHalluciNet (POSIX-Shell lab) | 80.33 | B |
| [`fixtures/espot-web-api.scorecard.json`](fixtures/espot-web-api.scorecard.json) | ESPot (Web-API, **full** lab, results-5.0.1) | 31.09 | F |
| [`fixtures/trapster-ssh.scorecard.json`](fixtures/trapster-ssh.scorecard.json) | Trapster Community (SSH, **full** lab, results-5.0.1) | 19.05 | F |
| [`fixtures/trapster-http.scorecard.json`](fixtures/trapster-http.scorecard.json) | Trapster Community (HTTP, **full** lab, results-5.0.1) | 28.95 | F |
| [`fixtures/trapster-ftp.scorecard.json`](fixtures/trapster-ftp.scorecard.json) | Trapster Community (FTP, **full** lab, results-5.0.1) | 27.2 | F |
| [`fixtures/trapster-telnet.scorecard.json`](fixtures/trapster-telnet.scorecard.json) | Trapster Community (Telnet, **full** lab, results-5.0.1) | 41.99 | F |
| [`fixtures/beelzebub-redis.scorecard.json`](fixtures/beelzebub-redis.scorecard.json) | Beelzebub (Redis, **full** lab, results-5.0.1) | 16.46 | F |
| [`fixtures/beelzebub-ssh.scorecard.json`](fixtures/beelzebub-ssh.scorecard.json) | Beelzebub (SSH, **full** lab, results-5.0.1) | 18.89 | F |
| [`fixtures/beelzebub-telnet.scorecard.json`](fixtures/beelzebub-telnet.scorecard.json) | Beelzebub (Telnet, **full** lab, results-5.0.1) | 33.99 | F |
| [`fixtures/beelzebub-http.scorecard.json`](fixtures/beelzebub-http.scorecard.json) | Beelzebub (HTTP, **full** lab, results-5.0.1) | 33.5 | F |
| [`fixtures/beelzebub-mcp.scorecard.json`](fixtures/beelzebub-mcp.scorecard.json) | Beelzebub (MCP, **full** lab, results-5.0.1) | 31.44 | F |
| [`fixtures/miniprint-low-interaction.scorecard.json`](fixtures/miniprint-low-interaction.scorecard.json) | miniprint (PJL / Low-Interaction, **full**, results-5.0.1) | 12.86 | F |
| [`fixtures/honeyup-web-api.scorecard.json`](fixtures/honeyup-web-api.scorecard.json) | HoneyUp (Web-API, **full**, results-5.0.1) | 79.83 | C |
| [`fixtures/flux-web-api.scorecard.json`](fixtures/flux-web-api.scorecard.json) | flux (Web-API, **full**, results-5.0.1) | 83.28 | B |
| [`fixtures/elastichoney-web-api.scorecard.json`](fixtures/elastichoney-web-api.scorecard.json) | Elastichoney (Web-API, **full**, results-5.0.1) | 82.22 | B |
| [`fixtures/wordpot-web-api.scorecard.json`](fixtures/wordpot-web-api.scorecard.json) | wordpot (Web-API, **full**, results-5.0.1) | 70.56 | C |
| [`fixtures/express-honeypot-web-api.scorecard.json`](fixtures/express-honeypot-web-api.scorecard.json) | express-honeypot (Web-API, **full**, results-5.0.1) | 79.46 | C |
| [`fixtures/honeyhttpd-web-api.scorecard.json`](fixtures/honeyhttpd-web-api.scorecard.json) | HoneyHTTPD (Web-API, **full**, results-5.0.1) | 70.96 | C |
| [`fixtures/log4pot-web-api.scorecard.json`](fixtures/log4pot-web-api.scorecard.json) | Log4Pot (Web-API, **full**, results-5.0.1) | 33.94 | F |
| [`fixtures/conpot-ics-scada.scorecard.json`](fixtures/conpot-ics-scada.scorecard.json) | Conpot (ICS-SCADA / Modbus, **full**, results-5.0.1) | 61.94 | D |
| [`fixtures/hellpot-web-api.scorecard.json`](fixtures/hellpot-web-api.scorecard.json) | HellPot (Web-API / HTTP, **full**, results-5.0.1) | 39.59 | F |
| [`fixtures/opencanary-web-api.scorecard.json`](fixtures/opencanary-web-api.scorecard.json) | OpenCanary (Web-API / HTTP, **full**) | 32.07 | F |
| [`fixtures/opencanary-ftp.scorecard.json`](fixtures/opencanary-ftp.scorecard.json) | OpenCanary (FTP, **full**) | 28.38 | F |
| [`fixtures/opencanary-ssh.scorecard.json`](fixtures/opencanary-ssh.scorecard.json) | OpenCanary (SSH, **full**) | 10.82 | F |
| [`fixtures/opencanary-telnet.scorecard.json`](fixtures/opencanary-telnet.scorecard.json) | OpenCanary (Telnet, **full**) | 41.65 | F |
| [`fixtures/opencanary-redis.scorecard.json`](fixtures/opencanary-redis.scorecard.json) | OpenCanary (Redis, **full**) | 16.12 | F |
| [`fixtures/endlessh-low-interaction.scorecard.json`](fixtures/endlessh-low-interaction.scorecard.json) | Endlessh (SSH tarpit / `ssh_tarpit`, **full**) | 33.95 | F |
| [`fixtures/echidra-low-interaction.scorecard.json`](fixtures/echidra-low-interaction.scorecard.json) | EchidraOSS (SSH / Low-Interaction, **full**) | 38.09 | F |
| [`fixtures/safety-gate-fail.scorecard.json`](fixtures/safety-gate-fail.scorecard.json) | Synthetic GATE_FAILED (ungraded) | 23.49 | F |
| [`fixtures/v5/gate-passed-graded.scorecard.json`](fixtures/v5/gate-passed-graded.scorecard.json) | Synthetic GATE_PASSED graded | 90 | A |
| [`fixtures/v5/gate-failed-ungraded.scorecard.json`](fixtures/v5/gate-failed-ungraded.scorecard.json) | Synthetic GATE_FAILED | 50 | D |
| [`fixtures/v5/incomplete-ungraded.scorecard.json`](fixtures/v5/incomplete-ungraded.scorecard.json) | Synthetic INCOMPLETE | 76 | C |

## How to run

```bash
pip install -e ".[dev]"
pytest tests/test_conformance.py -q
uhbs validate-scorecard docs/conformance/fixtures/cowrie-low-interaction.scorecard.json --strict
uhbs validate-scorecard docs/conformance/fixtures/espot-web-api.scorecard.json --strict
uhbs validate-scorecard docs/conformance/fixtures/miniprint-low-interaction.scorecard.json --strict
uhbs validate-scorecard docs/conformance/fixtures/conpot-ics-scada.scorecard.json --strict
uhbs validate-scorecard docs/conformance/fixtures/opencanary-web-api.scorecard.json --strict
```

## Relationship to the lab harness

Fixtures and reports were produced by `uhbs_core.run_benchmark` (Modules A–F)
and verified with `compute_uhqs`. See [reference-implementation.md](../reference-implementation.md)
and the per-honeypot [reports](reports/index.md).

**Naming policy:** Outside this conformance tree, docs and templates MUST use
decoy **classes** and **protocols** only (see repository `GOVERNANCE.md`).
