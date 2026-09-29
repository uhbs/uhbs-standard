# UHBS 5.0.1 score Dockerfile — unit `honeypot-ftp-ftp`
# Source: docs/conformance/labs/honeypot-ftp/Dockerfile.lab
# Target image: honeypot-ftp:uhbs-lab (sha256:7ef087855d43efbabddee32c56b5ff87db7f29702a33c58af123758571e1a7ff)
# Rebuild (build context = cloned upstream under .local/labs/honeypot-ftp):
#   docker build -f Dockerfile -t honeypot-ftp:uhbs-lab .local/labs/honeypot-ftp
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t honeypot-ftp:uhbs-lab .
#
FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-twisted \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN mkdir -p /app/pub

EXPOSE 21
CMD ["python3", "/app/ftp_lab.py"]
