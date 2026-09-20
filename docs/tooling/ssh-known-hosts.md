# Pinning SSH host keys for UHBS labs

UHBS rejects unknown SSH host keys (`RejectPolicy`). Before Modules B–D can
authenticate to a lab decoy, pin the target key:

```bash
mkdir -p .local
# Replace host/port with your lab listen address.
ssh-keyscan -p 2222 127.0.0.1 > .local/uhbs_known_hosts
ssh-keygen -lf .local/uhbs_known_hosts   # verify against the container console
chmod 600 .local/uhbs_known_hosts
export UHBS_SSH_KNOWN_HOSTS="$PWD/.local/uhbs_known_hosts"
```

Inventory alternative (same effect as the env var):

```yaml
sites:
  my-ssh:
    host: 127.0.0.1
    ports: { ssh: 2222 }
    protocol: ssh
    ssh_known_hosts: .local/uhbs_known_hosts
```

If the host key is missing or mismatched, Module D records mandatory
`ERROR` checks and the containment verdict is **INCOMPLETE** — never an
inferred `GATE_PASSED`.
