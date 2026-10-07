# Official Benchmark Scorecards

Auditors must publish results using the standard scorecard layout validated by [`schemas/scorecard.schema.json`](https://github.com/uhbs/uhbs-standard/blob/main/schemas/scorecard.schema.json).

UHBS is **vendor-neutral**: decoy **classes** and **protocols** are the normative vocabulary. Named products appear only as **evaluation proof** (not requirements or endorsements).

**Current wave (results-5.0.1):** every graded unit — quick/full UHQS, module breakdowns, verbatim `SCORECARD.txt`, and provenance — is published under [Conformance → Lab reports](../conformance/index.md). Machine-readable golden fixtures live under [`docs/conformance/fixtures/`](https://github.com/uhbs/uhbs-standard/tree/main/docs/conformance/fixtures).

**CTI & blue team:** start with [How to read UHBS lab proof](../conformance/reports/READING-UHQS.md). Each scorecard page includes a module interpretation table (what A–F mean for sensors vs tarpits vs credential sinks).

## Published scorecards (results-5.0.1)

Full runs are authoritative. All values under `scoring_model_id=uhqs-v5.2-measured-renorm` (always-grade; the Safety Gate acts through δ_C).

| Scorecard | Class / protocol | Full UHQS | Grade |
| --- | --- | ---: | --- |
| [Beelzebub — HTTP :8080](beelzebub-http.scorecard.md) | Web-API · HTTP | **33.5** | F |
| [Beelzebub — MCP :8000](beelzebub-mcp.scorecard.md) | Web-API (MCP v1) · MCP | **31.44** | F |
| [Beelzebub — Redis :6379](beelzebub-redis.scorecard.md) | Low-Interaction · Redis | **16.46** | F |
| [Beelzebub — SSH :2222](beelzebub-ssh.scorecard.md) | Low-Interaction · SSH | **18.89** | F |
| [Beelzebub — Telnet :23](beelzebub-telnet.scorecard.md) | Low-Interaction · Telnet | **33.99** | F |
| [Dionaea — FTP :21](dionaea-ftp.scorecard.md) | Low-Interaction · FTP | **22.4** | F |
| [Dionaea — HTTP :80](dionaea-http.scorecard.md) | Web-API · HTTP | **23.11** | F |
| [Dionaea — SMB :445](dionaea-smb.scorecard.md) | Low-Interaction · SMB | **33.1** | F |

## Archived 4.x scorecards

The historical 4.2.2-era narrative scorecard pages (including the illustrative POSIX-Shell / GenAI layout sample) are **archived in the repository only** and are no longer rendered on this site. Browse them at [`docs/scorecards/` on GitHub](https://github.com/uhbs/uhbs-standard/tree/main/docs/scorecards) if you need the original 4.x-era presentation. Their numbers predate the UHQS v5 always-grade model and must not be cited as current results.

## Badge Snippets

After an official evaluation, maintainers can embed:

```markdown
![UHBS v5.0.1 Grade A](https://img.shields.io/badge/UHBS%20v5.0.1-Grade%20A-brightgreen)
![UHBS v5.0.1 Grade B](https://img.shields.io/badge/UHBS%20v5.0.1-Grade%20B-yellowgreen)
![UHBS v5.0.1 Grade C](https://img.shields.io/badge/UHBS%20v5.0.1-Grade%20C-yellow)
![UHBS v5.0.1 Grade D](https://img.shields.io/badge/UHBS%20v5.0.1-Grade%20D-orange)
![UHBS v5.0.1 Grade F](https://img.shields.io/badge/UHBS%20v5.0.1-Grade%20F-red)
```

## Submitting a Scorecard

1. Complete a TPS `profile.yaml`
2. Run the five-phase audit
3. Emit a scorecard conforming to the schema
4. Open a PR or issue using the **Profile / Scorecard Submission** template

Validate a published fixture locally:

```bash
uhbs validate-scorecard docs/conformance/fixtures/espot-web-api.scorecard.json --strict
```
