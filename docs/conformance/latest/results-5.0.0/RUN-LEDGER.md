# RUN-LEDGER — `docs/conformance/latest/results-5.0.0`

Updated: 2026-09-26T21:07:53Z

**Gate D:** OPEN — workers may claim refreshable units with `python scripts/tracker.py claim-next --agent <id>`.

## Counts

- Hubs: **69**
- Units: **111**
- Refreshable: **0**
- Legacy / not refreshed: **19**
- Blocked: **0**
- Assigned: **71**

SQLite: `.local/benchmark-refresh/results-5.0.0.sqlite3`
Manifest: `docs/conformance/latest/results-5.0.0/benchmark-manifest.yaml`

## Units

| unit_id | benchmark | protocol | status | agent | latest | archive |
| --- | --- | --- | --- | --- | --- | --- |
| `HellPot-http` | `HellPot` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/HellPot/http` | `docs/conformance/archive/v5.0.0/HellPot/http` |
| `HoneyPy-legacy` | `HoneyPy` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/HoneyPy` | `docs/conformance/archive/v5.0.0/HoneyPy` |
| `HoneyWire-http` | `HoneyWire` | `http` | `done` |  | `docs/conformance/latest/results-5.0.0/HoneyWire/http` | `docs/conformance/archive/v5.0.0/HoneyWire/http` |
| `Krawl-http` | `Krawl` | `http` | `done` |  | `docs/conformance/latest/results-5.0.0/Krawl/http` | `docs/conformance/archive/v5.0.0/Krawl/http` |
| `Log4Pot-http` | `Log4Pot` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/Log4Pot/http` | `docs/conformance/archive/v5.0.0/Log4Pot/http` |
| `Malbait-legacy` | `Malbait` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/Malbait` | `docs/conformance/archive/v5.0.0/Malbait` |
| `SMTPLLMPot-legacy` | `SMTPLLMPot` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/SMTPLLMPot` | `docs/conformance/archive/v5.0.0/SMTPLLMPot` |
| `acra-legacy` | `acra` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/acra` | `docs/conformance/archive/v5.0.0/acra` |
| `artillery-generic` | `artillery` | `generic` | `done` |  | `docs/conformance/latest/results-5.0.0/artillery/generic` | `docs/conformance/archive/v5.0.0/artillery/generic` |
| `beelzebub-http` | `beelzebub` | `http` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/beelzebub/http` | `docs/conformance/archive/v5.0.0/beelzebub/http` |
| `beelzebub-mcp` | `beelzebub` | `mcp` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/beelzebub/mcp` | `docs/conformance/archive/v5.0.0/beelzebub/mcp` |
| `beelzebub-redis` | `beelzebub` | `redis` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/beelzebub/redis` | `docs/conformance/archive/v5.0.0/beelzebub/redis` |
| `beelzebub-ssh` | `beelzebub` | `ssh` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/beelzebub/ssh` | `docs/conformance/archive/v5.0.0/beelzebub/ssh` |
| `beelzebub-telnet` | `beelzebub` | `telnet` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/beelzebub/telnet` | `docs/conformance/archive/v5.0.0/beelzebub/telnet` |
| `blacknet-legacy` | `blacknet` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/blacknet` | `docs/conformance/archive/v5.0.0/blacknet` |
| `conpot-modbus` | `conpot` | `modbus` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/conpot` | `docs/conformance/archive/v5.0.0/conpot` |
| `cowrie-ssh` | `cowrie` | `ssh` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/cowrie/ssh` | `docs/conformance/archive/v5.0.0/cowrie/ssh` |
| `cowrie-telnet` | `cowrie` | `telnet` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/cowrie/telnet` | `docs/conformance/archive/v5.0.0/cowrie/telnet` |
| `datatrap-http` | `datatrap` | `http` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/datatrap/http` | `docs/conformance/archive/v5.0.0/datatrap/http` |
| `datatrap-mysql` | `datatrap` | `mysql` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/datatrap/mysql` | `docs/conformance/archive/v5.0.0/datatrap/mysql` |
| `datatrap-postgres` | `datatrap` | `postgres` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/datatrap/postgres` | `docs/conformance/archive/v5.0.0/datatrap/postgres` |
| `datatrap-redis` | `datatrap` | `redis` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/datatrap/redis` | `docs/conformance/archive/v5.0.0/datatrap/redis` |
| `datatrap-ssh` | `datatrap` | `ssh` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/datatrap/ssh` | `docs/conformance/archive/v5.0.0/datatrap/ssh` |
| `datatrap-telnet` | `datatrap` | `telnet` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/datatrap/telnet` | `docs/conformance/archive/v5.0.0/datatrap/telnet` |
| `dionaea-ftp` | `dionaea` | `ftp` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/dionaea/ftp` | `docs/conformance/archive/v5.0.0/dionaea/ftp` |
| `dionaea-http` | `dionaea` | `http` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/dionaea/http` | `docs/conformance/archive/v5.0.0/dionaea/http` |
| `dionaea-smb` | `dionaea` | `smb` | `done` | worker-wave3b | `docs/conformance/latest/results-5.0.0/dionaea/smb` | `docs/conformance/archive/v5.0.0/dionaea/smb` |
| `echidra-ssh` | `echidra` | `ssh` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/echidra` | `docs/conformance/archive/v5.0.0/echidra` |
| `elastichoney-http` | `elastichoney` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/elastichoney/http` | `docs/conformance/archive/v5.0.0/elastichoney/http` |
| `endlessh-ssh_tarpit` | `endlessh` | `ssh_tarpit` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/endlessh` | `docs/conformance/archive/v5.0.0/endlessh` |
| `ensnare-legacy` | `ensnare` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/ensnare` | `docs/conformance/archive/v5.0.0/ensnare` |
| `espot-http` | `espot` | `http` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/espot` | `docs/conformance/archive/v5.0.0/espot` |
| `express-honeypot-http` | `express-honeypot` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/express-honeypot/http` | `docs/conformance/archive/v5.0.0/express-honeypot/http` |
| `fapro-legacy` | `fapro` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/fapro` | `docs/conformance/archive/v5.0.0/fapro` |
| `flux-http` | `flux` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/flux/http` | `docs/conformance/archive/v5.0.0/flux/http` |
| `fortigate-vpn-ssl-http` | `fortigate-vpn-ssl` | `http` | `done` |  | `docs/conformance/latest/results-5.0.0/fortigate-vpn-ssl/http` | `docs/conformance/archive/v5.0.0/fortigate-vpn-ssl/http` |
| `galah-legacy` | `galah` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/galah` | `docs/conformance/archive/v5.0.0/galah` |
| `genaipot-pop3` | `genaipot` | `pop3` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/genaipot/pop3` | `docs/conformance/archive/v5.0.0/genaipot/pop3` |
| `genaipot-smtp` | `genaipot` | `smtp` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/genaipot/smtp` | `docs/conformance/archive/v5.0.0/genaipot/smtp` |
| `glastopf-legacy` | `glastopf` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/glastopf` | `docs/conformance/archive/v5.0.0/glastopf` |
| `glutton-legacy` | `glutton` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/glutton` | `docs/conformance/archive/v5.0.0/glutton` |
| `heralding-ftp` | `heralding` | `ftp` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/heralding/ftp` | `docs/conformance/archive/v5.0.0/heralding/ftp` |
| `heralding-smtp` | `heralding` | `smtp` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/heralding/smtp` | `docs/conformance/archive/v5.0.0/heralding/smtp` |
| `heralding-ssh` | `heralding` | `ssh` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/heralding/ssh` | `docs/conformance/archive/v5.0.0/heralding/ssh` |
| `honeyagents-ssh` | `honeyagents` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/honeyagents/ssh` | `docs/conformance/archive/v5.0.0/honeyagents/ssh` |
| `honeyhttpd-http` | `honeyhttpd` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/honeyhttpd/http` | `docs/conformance/archive/v5.0.0/honeyhttpd/http` |
| `honeymcp-mcp` | `honeymcp` | `mcp` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/honeymcp/mcp` | `docs/conformance/archive/v5.0.0/honeymcp/mcp` |
| `honeyplc-legacy` | `honeyplc` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/honeyplc` | `docs/conformance/archive/v5.0.0/honeyplc` |
| `honeypot-ftp-ftp` | `honeypot-ftp` | `ftp` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp` | `docs/conformance/archive/v5.0.0/honeypot-ftp/ftp` |
| `honeytrap-ssh` | `honeytrap` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/honeytrap/ssh` | `docs/conformance/archive/v5.0.0/honeytrap/ssh` |
| `honeyup-http` | `honeyup` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/honeyup/http` | `docs/conformance/archive/v5.0.0/honeyup/http` |
| `kippo-ssh` | `kippo` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/kippo/ssh` | `docs/conformance/archive/v5.0.0/kippo/ssh` |
| `llm-honeypot-ssh` | `llm-honeypot` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/llm-honeypot/ssh` | `docs/conformance/archive/v5.0.0/llm-honeypot/ssh` |
| `llmpot-http` | `llmpot` | `http` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/llmpot/http` | `docs/conformance/archive/v5.0.0/llmpot/http` |
| `llmpot-modbus` | `llmpot` | `modbus` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/llmpot/modbus` | `docs/conformance/archive/v5.0.0/llmpot/modbus` |
| `llmpot-s7comm` | `llmpot` | `s7comm` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/llmpot/s7comm` | `docs/conformance/archive/v5.0.0/llmpot/s7comm` |
| `lophiid-legacy` | `lophiid` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/lophiid` | `docs/conformance/archive/v5.0.0/lophiid` |
| `mailoney-smtp` | `mailoney` | `smtp` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/mailoney/smtp` | `docs/conformance/archive/v5.0.0/mailoney/smtp` |
| `masscanned-legacy` | `masscanned` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/masscanned` | `docs/conformance/archive/v5.0.0/masscanned` |
| `miniprint-pjl` | `miniprint` | `pjl` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/miniprint` | `docs/conformance/archive/v5.0.0/miniprint` |
| `mockssh-ssh` | `mockssh` | `ssh` | `done` | worker-wave1 | `docs/conformance/latest/results-5.0.0/mockssh/ssh` | `docs/conformance/archive/v5.0.0/mockssh/ssh` |
| `modpot-http` | `modpot` | `http` | `done` |  | `docs/conformance/latest/results-5.0.0/modpot/http` | `docs/conformance/archive/v5.0.0/modpot/http` |
| `mqtt-decoy-a-mqtt` | `mqtt-decoy-a` | `mqtt` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/mqtt-decoy-a/mqtt` | `docs/conformance/archive/v5.0.0/mqtt-decoy-a/mqtt` |
| `mqtt-decoy-b-mqtt` | `mqtt-decoy-b` | `mqtt` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/mqtt-decoy-b/mqtt` | `docs/conformance/archive/v5.0.0/mqtt-decoy-b/mqtt` |
| `mysql-honeypotd-mysql` | `mysql-honeypotd` | `mysql` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/mysql-honeypotd/mysql` | `docs/conformance/archive/v5.0.0/mysql-honeypotd/mysql` |
| `node-ftp-honeypot-ftp` | `node-ftp-honeypot` | `ftp` | `done` |  | `docs/conformance/latest/results-5.0.0/node-ftp-honeypot/ftp` | `docs/conformance/archive/v5.0.0/node-ftp-honeypot/ftp` |
| `nosqlpot-redis` | `nosqlpot` | `redis` | `done` |  | `docs/conformance/latest/results-5.0.0/nosqlpot/redis` | `docs/conformance/archive/v5.0.0/nosqlpot/redis` |
| `opencanary-ftp` | `opencanary` | `ftp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/ftp` | `docs/conformance/archive/v5.0.0/opencanary/ftp` |
| `opencanary-git` | `opencanary` | `git` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/git` | `docs/conformance/archive/v5.0.0/opencanary/git` |
| `opencanary-http` | `opencanary` | `http` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/http` | `docs/conformance/archive/v5.0.0/opencanary/http` |
| `opencanary-mysql` | `opencanary` | `mysql` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/mysql` | `docs/conformance/archive/v5.0.0/opencanary/mysql` |
| `opencanary-ntp` | `opencanary` | `ntp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/ntp` | `docs/conformance/archive/v5.0.0/opencanary/ntp` |
| `opencanary-rdp` | `opencanary` | `rdp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/rdp` | `docs/conformance/archive/v5.0.0/opencanary/rdp` |
| `opencanary-redis` | `opencanary` | `redis` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/redis` | `docs/conformance/archive/v5.0.0/opencanary/redis` |
| `opencanary-sip` | `opencanary` | `sip` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/sip` | `docs/conformance/archive/v5.0.0/opencanary/sip` |
| `opencanary-smb` | `opencanary` | `smb` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/smb` | `docs/conformance/archive/v5.0.0/opencanary/smb` |
| `opencanary-snmp` | `opencanary` | `snmp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/snmp` | `docs/conformance/archive/v5.0.0/opencanary/snmp` |
| `opencanary-ssh` | `opencanary` | `ssh` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/ssh` | `docs/conformance/archive/v5.0.0/opencanary/ssh` |
| `opencanary-telnet` | `opencanary` | `telnet` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/telnet` | `docs/conformance/archive/v5.0.0/opencanary/telnet` |
| `opencanary-tftp` | `opencanary` | `tftp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/tftp` | `docs/conformance/archive/v5.0.0/opencanary/tftp` |
| `opencanary-vnc` | `opencanary` | `vnc` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/opencanary/vnc` | `docs/conformance/archive/v5.0.0/opencanary/vnc` |
| `owa-honeypot-http` | `owa-honeypot` | `http` | `done` |  | `docs/conformance/latest/results-5.0.0/owa-honeypot/http` | `docs/conformance/archive/v5.0.0/owa-honeypot/http` |
| `owasp-python-honeypot-http` | `owasp-python-honeypot` | `http` | `done` |  | `docs/conformance/latest/results-5.0.0/owasp-python-honeypot/http` | `docs/conformance/archive/v5.0.0/owasp-python-honeypot/http` |
| `pghoney-postgres` | `pghoney` | `postgres` | `done` | worker-wave2 | `docs/conformance/latest/results-5.0.0/pghoney/postgres` | `docs/conformance/archive/v5.0.0/pghoney/postgres` |
| `portlurker-generic` | `portlurker` | `generic` | `done` |  | `docs/conformance/latest/results-5.0.0/portlurker/generic` | `docs/conformance/archive/v5.0.0/portlurker/generic` |
| `pyrdp-rdp` | `pyrdp` | `rdp` | `done` |  | `docs/conformance/latest/results-5.0.0/pyrdp/rdp` | `docs/conformance/archive/v5.0.0/pyrdp/rdp` |
| `qeeqbox-honeypots-ftp` | `qeeqbox-honeypots` | `ftp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/ftp` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/ftp` |
| `qeeqbox-honeypots-http` | `qeeqbox-honeypots` | `http` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/http` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/http` |
| `qeeqbox-honeypots-mysql` | `qeeqbox-honeypots` | `mysql` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/mysql` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/mysql` |
| `qeeqbox-honeypots-pop3` | `qeeqbox-honeypots` | `pop3` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/pop3` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/pop3` |
| `qeeqbox-honeypots-postgres` | `qeeqbox-honeypots` | `postgres` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/postgres` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/postgres` |
| `qeeqbox-honeypots-redis` | `qeeqbox-honeypots` | `redis` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/redis` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/redis` |
| `qeeqbox-honeypots-smtp` | `qeeqbox-honeypots` | `smtp` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/smtp` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/smtp` |
| `qeeqbox-honeypots-ssh` | `qeeqbox-honeypots` | `ssh` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/ssh` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/ssh` |
| `qeeqbox-honeypots-telnet` | `qeeqbox-honeypots` | `telnet` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/telnet` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/telnet` |
| `qeeqbox-honeypots-vnc` | `qeeqbox-honeypots` | `vnc` | `done` | worker-main | `docs/conformance/latest/results-5.0.0/qeeqbox-honeypots/vnc` | `docs/conformance/archive/v5.0.0/qeeqbox-honeypots/vnc` |
| `sentrypeer-sip` | `sentrypeer` | `sip` | `done` |  | `docs/conformance/latest/results-5.0.0/sentrypeer/sip` | `docs/conformance/archive/v5.0.0/sentrypeer/sip` |
| `shiva-smtp` | `shiva` | `smtp` | `done` |  | `docs/conformance/latest/results-5.0.0/shiva/smtp` | `docs/conformance/archive/v5.0.0/shiva/smtp` |
| `snare-legacy` | `snare` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/snare` | `docs/conformance/archive/v5.0.0/snare` |
| `ssh-auth-logger-ssh` | `ssh-auth-logger` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/ssh-auth-logger/ssh` | `docs/conformance/archive/v5.0.0/ssh-auth-logger/ssh` |
| `ssh-honeypot-legacy` | `ssh-honeypot` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/ssh-honeypot` | `docs/conformance/archive/v5.0.0/ssh-honeypot` |
| `ssh-honeypotd-ssh` | `ssh-honeypotd` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/ssh-honeypotd/ssh` | `docs/conformance/archive/v5.0.0/ssh-honeypotd/ssh` |
| `sshesame-ssh` | `sshesame` | `ssh` | `done` |  | `docs/conformance/latest/results-5.0.0/sshesame/ssh` | `docs/conformance/archive/v5.0.0/sshesame/ssh` |
| `sticky_elephant-postgres` | `sticky_elephant` | `postgres` | `done` |  | `docs/conformance/latest/results-5.0.0/sticky_elephant/postgres` | `docs/conformance/archive/v5.0.0/sticky_elephant/postgres` |
| `tanner-legacy` | `tanner` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/tanner` | `docs/conformance/archive/v5.0.0/tanner` |
| `telnet-iot-honeypot-legacy` | `telnet-iot-honeypot` | `legacy` | `legacy-not-refreshed` |  | `docs/conformance/latest/results-5.0.0/telnet-iot-honeypot` | `docs/conformance/archive/v5.0.0/telnet-iot-honeypot` |
| `trapster-ftp` | `trapster` | `ftp` | `done` | worker-wave3 | `docs/conformance/latest/results-5.0.0/trapster/ftp` | `docs/conformance/archive/v5.0.0/trapster/ftp` |
| `trapster-http` | `trapster` | `http` | `done` | worker-wave3 | `docs/conformance/latest/results-5.0.0/trapster/http` | `docs/conformance/archive/v5.0.0/trapster/http` |
| `trapster-ssh` | `trapster` | `ssh` | `done` | worker-wave3 | `docs/conformance/latest/results-5.0.0/trapster/ssh` | `docs/conformance/archive/v5.0.0/trapster/ssh` |
| `trapster-telnet` | `trapster` | `telnet` | `done` | worker-wave3 | `docs/conformance/latest/results-5.0.0/trapster/telnet` | `docs/conformance/archive/v5.0.0/trapster/telnet` |
| `wordpot-http` | `wordpot` | `http` | `done` | worker-remainder | `docs/conformance/latest/results-5.0.0/wordpot/http` | `docs/conformance/archive/v5.0.0/wordpot/http` |

## Open blockers

_None._

## Notes

Legacy hubs are explicitly closed as `legacy-not-refreshed` (no executable lab). No UHQS scores were invented. Historical proof remains under `docs/conformance/archive/v5.0.0/`.

| unit_id | benchmark | note |
| --- | --- | --- |
| `HoneyPy-legacy` | `HoneyPy` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `Malbait-legacy` | `Malbait` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `SMTPLLMPot-legacy` | `SMTPLLMPot` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `acra-legacy` | `acra` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `blacknet-legacy` | `blacknet` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `ensnare-legacy` | `ensnare` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `fapro-legacy` | `fapro` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `galah-legacy` | `galah` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `glastopf-legacy` | `glastopf` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `glutton-legacy` | `glutton` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `honeyplc-legacy` | `honeyplc` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `lophiid-legacy` | `lophiid` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `masscanned-legacy` | `masscanned` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `mqtt-decoy-a-mqtt` | `mqtt-decoy-a` | legacy-not-refreshed: operator-provided MQTT endpoint; no cloneable lab inventory matching the hub name. Closed without new UHQS scores. |
| `mqtt-decoy-b-mqtt` | `mqtt-decoy-b` | legacy-not-refreshed: operator-provided MQTT endpoint; no cloneable lab inventory matching the hub name. Closed without new UHQS scores. |
| `snare-legacy` | `snare` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `ssh-honeypot-legacy` | `ssh-honeypot` | legacy-not-refreshed: lab dir exists but no inventory/TPS (upstream Docker base image missing). Closed without new UHQS scores. |
| `tanner-legacy` | `tanner` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
| `telnet-iot-honeypot-legacy` | `telnet-iot-honeypot` | legacy-not-refreshed: no usable inventory + quick/full TPS. Closed without new UHQS scores. |
