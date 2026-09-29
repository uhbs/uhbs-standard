# UHBS 5.0.1 score Dockerfile — unit `Log4Pot-http`
# Source: docs/conformance/labs/Log4Pot/Dockerfile.lab
# Target image: log4pot:uhbs-lab (sha256:9bb74bb48640a29a35d8170e05f447befc37f2ab03b1491a1c6d60abdbc4cd71)
# Rebuild (build context = cloned upstream under .local/labs/Log4Pot):
#   docker build -f Dockerfile -t log4pot:uhbs-lab .local/labs/Log4Pot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t log4pot:uhbs-lab .
#
# UHBS lab wrapper. README: python log4pot.py without Azure extras.
# Ubuntu latest + python3 (stdlib http.server; skip payloader/azure).
FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/log4pot
COPY . .
RUN mkdir -p /telemetry
EXPOSE 8080
CMD ["python3", "log4pot-server.py", "--port", "8080", "--log", "/telemetry/log4pot.log", "--response", "responses/default.json"]
