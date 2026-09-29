# UHBS 5.0.1 score Dockerfile — unit `echidra-ssh`
# Source: .local/labs/echidra/Dockerfile
# Target image: echidra:uhbs-lab (sha256:b77be4a5a0b0defbfb6a540ddf9957521f6da93070a75dd3c7a7a770f4bd48c3)
# Rebuild (build context = cloned upstream under .local/labs/echidra):
#   docker build -f Dockerfile -t echidra:uhbs-lab .local/labs/echidra
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t echidra:uhbs-lab .
#
FROM python:3.11-slim

# tzdata provides the /usr/share/zoneinfo database that /etc/localtime
# (bind-mounted from the host in docker-compose.yml) resolves against --
# without it, glibc silently stays on UTC regardless of what's mounted.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir .
RUN useradd --create-home --shell /bin/false echidra \
    && mkdir -p /app/logs \
    && chown -R echidra:echidra /app
USER echidra

# docker-compose.yml overrides this per-service (honeypot vs. API); running
# it standalone starts both together via the echidra CLI, same as
# `echidra start` outside a container.
CMD ["python", "-m", "echidra", "start"]
