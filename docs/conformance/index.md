# Published grades (conformance)

**Status:** Normative (fixtures) / Informative (narrative + lab reports)

!!! warning "UHBS v4.6.1 historical scoring model"
    Lab report pages under `docs/conformance/reports/` keep stable URLs and may
    cite DOI-era grades under UHQS 4.x. They are **historical**. New evaluations
    use UHBS **5.0.1** / `scoring_model_id=uhqs-v5.0-critical-gate-diagnostic`
    ([RFC 0003](../rfcs/0003-scoring-assurance.md)). Archived v4 fixtures:
    [`archive/v4.6.1/`](archive/v4.6.1/).

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
| [ESPot](latest/results-5.0.1/espot/index.md) | [ungraded](latest/results-5.0.1/espot/quick/) | [ungraded](latest/results-5.0.1/espot/full/) | [recipe](latest/results-5.0.1/espot/TUTORIAL.md) |
| [miniprint](latest/results-5.0.1/miniprint/index.md) | [ungraded](latest/results-5.0.1/miniprint/quick/) | [ungraded](latest/results-5.0.1/miniprint/full/) | [recipe](latest/results-5.0.1/miniprint/TUTORIAL.md) |
| [HoneyUp](latest/results-5.0.1/honeyup/http/index.md) | [ungraded](latest/results-5.0.1/honeyup/http/quick/) | [ungraded](latest/results-5.0.1/honeyup/http/full/) | [recipe](latest/results-5.0.1/honeyup/TUTORIAL.md) |
| [flux](latest/results-5.0.1/flux/http/index.md) | [ungraded](latest/results-5.0.1/flux/http/quick/) | [ungraded](latest/results-5.0.1/flux/http/full/) | [recipe](latest/results-5.0.1/flux/TUTORIAL.md) |
| [Elastichoney](latest/results-5.0.1/elastichoney/http/index.md) | [ungraded](latest/results-5.0.1/elastichoney/http/quick/) | [ungraded](latest/results-5.0.1/elastichoney/http/full/) | [recipe](latest/results-5.0.1/elastichoney/TUTORIAL.md) |
| [wordpot](latest/results-5.0.1/wordpot/http/index.md) | [ungraded](latest/results-5.0.1/wordpot/http/quick/) | [ungraded](latest/results-5.0.1/wordpot/http/full/) | [recipe](latest/results-5.0.1/wordpot/TUTORIAL.md) |
| [express-honeypot](latest/results-5.0.1/express-honeypot/http/index.md) | [ungraded](latest/results-5.0.1/express-honeypot/http/quick/) | [ungraded](latest/results-5.0.1/express-honeypot/http/full/) | [recipe](latest/results-5.0.1/express-honeypot/TUTORIAL.md) |
| [HellPot](latest/results-5.0.1/HellPot/http/index.md) | [ungraded](latest/results-5.0.1/HellPot/http/quick/) | [ungraded](latest/results-5.0.1/HellPot/http/full/) | [recipe](latest/results-5.0.1/HellPot/TUTORIAL.md) |
| [Beelzebub](latest/results-5.0.1/beelzebub/index.md) | [ungraded](latest/results-5.0.1/beelzebub/redis/quick/) | [ungraded](latest/results-5.0.1/beelzebub/redis/full/) | [recipe](latest/results-5.0.1/beelzebub/TUTORIAL.md) |
| [HoneyHTTPD](latest/results-5.0.1/honeyhttpd/http/index.md) | [ungraded](latest/results-5.0.1/honeyhttpd/http/quick/) | [ungraded](latest/results-5.0.1/honeyhttpd/http/full/) | [recipe](latest/results-5.0.1/honeyhttpd/TUTORIAL.md) |
| [Log4Pot](latest/results-5.0.1/Log4Pot/http/index.md) | [ungraded](latest/results-5.0.1/Log4Pot/http/quick/) | [ungraded](latest/results-5.0.1/Log4Pot/http/full/) | [recipe](latest/results-5.0.1/Log4Pot/TUTORIAL.md) |
| [Conpot](latest/results-5.0.1/conpot/index.md) | [ungraded](latest/results-5.0.1/conpot/quick/) | [ungraded](latest/results-5.0.1/conpot/full/) | [recipe](latest/results-5.0.1/conpot/TUTORIAL.md) |
| [Cowrie](reports/cowrie/index.md) | [82.76 / B](reports/cowrie/ssh/quick/) | [61.37 / D](reports/cowrie/ssh/full/) | [recipe](reports/cowrie/TUTORIAL.md) |
| [Endlessh](reports/endlessh/index.md) | [46.55 / F](reports/endlessh/quick/) | [54.07 / D](reports/endlessh/full/) | [recipe](reports/endlessh/TUTORIAL.md) |
| [EchidraOSS](reports/echidra/index.md) | [57.33 / D](reports/echidra/quick/) | [43.45 / F](reports/echidra/full/) | [recipe](reports/echidra/TUTORIAL.md) |
| [OpenCanary](reports/opencanary/index.md) | see hub | see hub | [recipe](reports/opencanary/TUTORIAL.md) |

## Fixtures

| Fixture | Proof target | Expected UHQS | Grade |
| --- | --- | --- | --- |
| [`fixtures/cowrie-low-interaction.scorecard.json`](fixtures/cowrie-low-interaction.scorecard.json) | Cowrie (SSH / Low-Interaction, **full** lab) | 61.37 | D |
| [`fixtures/posix-shell-lab.scorecard.json`](fixtures/posix-shell-lab.scorecard.json) | CyberHalluciNet (POSIX-Shell lab) | 80.33 | B |
| [`fixtures/espot-web-api.scorecard.json`](fixtures/espot-web-api.scorecard.json) | ESPot (Web-API, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/trapster-ssh.scorecard.json`](fixtures/trapster-ssh.scorecard.json) | Trapster Community (SSH, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/trapster-http.scorecard.json`](fixtures/trapster-http.scorecard.json) | Trapster Community (HTTP, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/trapster-ftp.scorecard.json`](fixtures/trapster-ftp.scorecard.json) | Trapster Community (FTP, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/trapster-telnet.scorecard.json`](fixtures/trapster-telnet.scorecard.json) | Trapster Community (Telnet, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/beelzebub-redis.scorecard.json`](fixtures/beelzebub-redis.scorecard.json) | Beelzebub (Redis, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/beelzebub-ssh.scorecard.json`](fixtures/beelzebub-ssh.scorecard.json) | Beelzebub (SSH, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/beelzebub-telnet.scorecard.json`](fixtures/beelzebub-telnet.scorecard.json) | Beelzebub (Telnet, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/beelzebub-http.scorecard.json`](fixtures/beelzebub-http.scorecard.json) | Beelzebub (HTTP, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/beelzebub-mcp.scorecard.json`](fixtures/beelzebub-mcp.scorecard.json) | Beelzebub (MCP, **full** lab, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/miniprint-low-interaction.scorecard.json`](fixtures/miniprint-low-interaction.scorecard.json) | miniprint (PJL / Low-Interaction, **full**, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/honeyup-web-api.scorecard.json`](fixtures/honeyup-web-api.scorecard.json) | HoneyUp (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/flux-web-api.scorecard.json`](fixtures/flux-web-api.scorecard.json) | flux (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/elastichoney-web-api.scorecard.json`](fixtures/elastichoney-web-api.scorecard.json) | Elastichoney (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/wordpot-web-api.scorecard.json`](fixtures/wordpot-web-api.scorecard.json) | wordpot (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/express-honeypot-web-api.scorecard.json`](fixtures/express-honeypot-web-api.scorecard.json) | express-honeypot (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/honeyhttpd-web-api.scorecard.json`](fixtures/honeyhttpd-web-api.scorecard.json) | HoneyHTTPD (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/log4pot-web-api.scorecard.json`](fixtures/log4pot-web-api.scorecard.json) | Log4Pot (Web-API, **full**, results-5.0.1) | null | ungraded |
| [`fixtures/conpot-ics-scada.scorecard.json`](fixtures/conpot-ics-scada.scorecard.json) | Conpot (ICS-SCADA / Modbus, **full**, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/hellpot-web-api.scorecard.json`](fixtures/hellpot-web-api.scorecard.json) | HellPot (Web-API / HTTP, **full**, results-5.0.1) | null | ungraded (INCOMPLETE) |
| [`fixtures/opencanary-web-api.scorecard.json`](fixtures/opencanary-web-api.scorecard.json) | OpenCanary (Web-API / HTTP, **full**) | 66.02 | D |
| [`fixtures/opencanary-ftp.scorecard.json`](fixtures/opencanary-ftp.scorecard.json) | OpenCanary (FTP, **full**) | 61.5 | D |
| [`fixtures/opencanary-ssh.scorecard.json`](fixtures/opencanary-ssh.scorecard.json) | OpenCanary (SSH, **full**) | 35.64 | F |
| [`fixtures/opencanary-telnet.scorecard.json`](fixtures/opencanary-telnet.scorecard.json) | OpenCanary (Telnet, **full**) | 64.9 | D |
| [`fixtures/opencanary-redis.scorecard.json`](fixtures/opencanary-redis.scorecard.json) | OpenCanary (Redis, **full**) | 53.72 | D |
| [`fixtures/endlessh-low-interaction.scorecard.json`](fixtures/endlessh-low-interaction.scorecard.json) | Endlessh (SSH tarpit / `ssh_tarpit`, **full**) | 54.07 | D |
| [`fixtures/echidra-low-interaction.scorecard.json`](fixtures/echidra-low-interaction.scorecard.json) | EchidraOSS (SSH / Low-Interaction, **full**) | 43.45 | F |
| [`fixtures/safety-gate-fail.scorecard.json`](fixtures/safety-gate-fail.scorecard.json) | Synthetic GATE_FAILED (ungraded) | null | null |
| [`fixtures/v5/gate-passed-graded.scorecard.json`](fixtures/v5/gate-passed-graded.scorecard.json) | Synthetic GATE_PASSED graded | 90.0 | A |
| [`fixtures/v5/gate-failed-ungraded.scorecard.json`](fixtures/v5/gate-failed-ungraded.scorecard.json) | Synthetic GATE_FAILED | null | null |
| [`fixtures/v5/incomplete-ungraded.scorecard.json`](fixtures/v5/incomplete-ungraded.scorecard.json) | Synthetic INCOMPLETE | null | null |

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
