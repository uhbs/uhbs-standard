# Tutorial: grade Dionaea with UHBS (results-5.0.0)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/dinotools/dionaea](https://github.com/dinotools/dionaea) · `master` @ `4e459f1b672a5b4c1e8335c0bff1b93738019215`  
**Refreshed:** FTP `:21`, SMB `:445`, HTTP `:80` (all INCOMPLETE / ungraded under UHBS 5.0.0)

## Clone + start

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/dinotools/dionaea.git .local/labs/dionaea
docker pull --platform linux/amd64 dinotools/dionaea:latest
docker run -d --name uhbs-target-dionaea --network uhbs-lab --network-alias dionaea-lab \
  --platform linux/amd64 \
  -v "$PWD/.local/labs/dionaea-telemetry:/opt/dionaea/var/log/dionaea" \
  -v "$PWD/.local/labs/dionaea-telemetry:/telemetry:rw" \
  dinotools/dionaea:latest
```

Exact per-protocol commands: [`ftp/EXECUTION-STEPS.md`](ftp/EXECUTION-STEPS.md), [`smb/EXECUTION-STEPS.md`](smb/EXECUTION-STEPS.md), [`http/EXECUTION-STEPS.md`](http/EXECUTION-STEPS.md).
