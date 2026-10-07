# Dionaea (UHBS multi-protocol proof)

**Status:** Informative · evaluation proof  
**Upstream:** [https://github.com/dinotools/dionaea](https://github.com/dinotools/dionaea)  
**Scope:** Every Dionaea service that has a UHBS protocol plugin is graded as its own unit (quick + full). Upstream-only surfaces without a UHBS plugin are listed under [protocol-coverage-audit.md](../../protocol-coverage-audit.md).

| Protocol | Class / port | Quick | Full |
| --- | --- | --- | --- |
| [FTP](ftp/index.md) | Low-Interaction · :21 | [quick](ftp/quick/README.md) | [full](ftp/full/README.md) |
| [HTTP](http/index.md) | Web-API · :80 | [quick](http/quick/README.md) | [full](http/full/README.md) |
| [SMB](smb/index.md) | Low-Interaction · :445 | [quick](smb/quick/README.md) | [full](smb/full/README.md) |
| Memcache | Database · :11211 | [latest](../../latest/results-5.0.1/dionaea/index.md) | [latest](../../latest/results-5.0.1/dionaea/index.md) |
| MQTT | Low-Interaction · :1883 | [latest](../../latest/results-5.0.1/dionaea/index.md) | [latest](../../latest/results-5.0.1/dionaea/index.md) |
| MSSQL | Database · :1433 | [latest](../../latest/results-5.0.1/dionaea/index.md) | [latest](../../latest/results-5.0.1/dionaea/index.md) |
| MySQL | Database · :3306 | [latest](../../latest/results-5.0.1/dionaea/index.md) | [latest](../../latest/results-5.0.1/dionaea/index.md) |
| SIP | Low-Interaction · :5060 | [latest](../../latest/results-5.0.1/dionaea/index.md) | [latest](../../latest/results-5.0.1/dionaea/index.md) |
| TFTP | Low-Interaction · :69 | [latest](../../latest/results-5.0.1/dionaea/index.md) | [latest](../../latest/results-5.0.1/dionaea/index.md) |
| PPTP | Low-Interaction · :1723 | [quick](../../latest/results-5.0.1/dionaea/pptp/quick/README.md) | [full](../../latest/results-5.0.1/dionaea/pptp/full/README.md) |
| UPnP | Low-Interaction · :1900/udp | [quick](../../latest/results-5.0.1/dionaea/upnp/quick/README.md) | [full](../../latest/results-5.0.1/dionaea/upnp/full/README.md) |

**Documented upstream, not UHBS-gradable yet:** `blackhole`, `epmap`, `mirror`.

- [Tutorial](TUTORIAL.md) · [Methodology](METHODOLOGY.md) · [Coverage audit](../../protocol-coverage-audit.md)

> Named product is evaluation proof only — not a UHBS endorsement.

## What this decoy is

Malware-capture oriented honeypot. UHBS grades each enabled service with a matching protocol plugin separately.

## Trust & limitations

- Evaluation proof under UHBS 5.0.1 — not a certification or endorsement.
- Prefer **full/** over **quick/** for decisions.
- Reading guide: [READING-UHQS.md](../READING-UHQS.md).
