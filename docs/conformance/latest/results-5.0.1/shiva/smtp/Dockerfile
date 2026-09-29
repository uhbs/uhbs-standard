# UHBS 5.0.1 score Dockerfile — unit `shiva-smtp`
# Source: pin:shiva-receiver:uhbs-lab@sha256:ba1ef65b29a3a75e9cd30a1f622da91ee5970a17c8f28816b42711b7e5bb4a44
# Target image: shiva-receiver:uhbs-lab (sha256:ba1ef65b29a3a75e9cd30a1f622da91ee5970a17c8f28816b42711b7e5bb4a44)
# Rebuild (build context = cloned upstream under .local/labs/shiva):
#   docker build -f Dockerfile -t shiva-receiver:uhbs-lab .local/labs/shiva
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t shiva-receiver:uhbs-lab .
#
# UHBS 5.0.1 pinned target image for `shiva-smtp`.
# No local build context — this reproduces the graded image via pull.
# Strategy: upstream-dockerfile
# Base reason: Upstream shiva receiver Dockerfile; SMTP on :2525.
FROM shiva-receiver:uhbs-lab@sha256:ba1ef65b29a3a75e9cd30a1f622da91ee5970a17c8f28816b42711b7e5bb4a44
