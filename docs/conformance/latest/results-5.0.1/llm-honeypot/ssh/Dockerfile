# UHBS 5.0.1 score Dockerfile — unit `llm-honeypot-ssh`
# Source: docs/conformance/labs/llm-honeypot/Dockerfile
# Target image: cowrie/cowrie:latest (sha256:92b9220978bc6095fb72b1a046240604ed03a5be1344abf6a2dd04eadd4cd330)
# Rebuild (build context = cloned upstream under .local/labs/llm-honeypot):
#   docker build -f Dockerfile -t cowrie/cowrie:latest .local/labs/llm-honeypot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t cowrie/cowrie:latest .
#
# Optional: bake overlays into cowrie/cowrie.
# Prefer runtime bind-mounts (see TUTORIAL.md) — distroless VOLUME on /etc
# hides files COPY'd into etc/ unless they are remounted at run time.
FROM cowrie/cowrie:latest
COPY --chown=cowrie:cowrie configs/whoami.py /cowrie/cowrie-git/src/cowrie/commands/whoami.py
COPY --chown=cowrie:cowrie configs/llm_prompts.py /cowrie/cowrie-git/src/cowrie/commands/llm_prompts.py
USER cowrie
EXPOSE 2222
