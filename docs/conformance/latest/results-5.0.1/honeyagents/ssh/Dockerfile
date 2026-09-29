# UHBS 5.0.1 score Dockerfile — unit `honeyagents-ssh`
# Source: pin:cowrie/cowrie:latest@sha256:92b9220978bc6095fb72b1a046240604ed03a5be1344abf6a2dd04eadd4cd330
# Target image: cowrie/cowrie:latest (sha256:92b9220978bc6095fb72b1a046240604ed03a5be1344abf6a2dd04eadd4cd330)
# Rebuild (build context = cloned upstream under .local/labs/honeyagents):
#   docker build -f Dockerfile -t cowrie/cowrie:latest .local/labs/honeyagents
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t cowrie/cowrie:latest .
#
# UHBS 5.0.1 pinned target image for `honeyagents-ssh`.
# No local build context — this reproduces the graded image via pull.
# Strategy: upstream-image
# Base reason: HoneyAgents compose uses cowrie/cowrie for the SSH decoy; grade Cowrie service only.
FROM cowrie/cowrie:latest@sha256:92b9220978bc6095fb72b1a046240604ed03a5be1344abf6a2dd04eadd4cd330
