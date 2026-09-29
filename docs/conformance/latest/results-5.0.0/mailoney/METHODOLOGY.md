# mailoney methodology (results-5.0.1)

**UHBS:** 5.0.1 · strategy `upstream-docker` · base `python:3.11-slim`

Upstream Dockerfile is the documented install path. Lab used SQLite instead of the Compose Postgres sidecar. Alembic may warn that `smtp_sessions` already exists; the listener still starts.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/phin3has/mailoney.git |
| Branch / commit | `main` / `b8310a7019dd0ba00c666e5185bee3c1dd851e19` |
| Target image | `mailoney:uhbs-lab` |
| Host / port | `mailoney-lab` : `25` |
| Verdict | INCOMPLETE / INCOMPLETE (ungraded) |

Limitations: `UHBS_AIRGAP_ATTESTED=1` is operator attestation. Product name is evaluation proof only. v5 Safety Gate leaves non-SSH SMTP **ungraded** without gateway/packet evidence.
