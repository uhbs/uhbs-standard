# UHBS 5.0.1 score Dockerfile — unit `qeeqbox-honeypots-smb`
# Source: .local/labs/qeeqbox-honeypots/Dockerfile.lab
# Target image: qeeqbox-honeypots:uhbs-lab (sha256:92ffc59399766a172f37a7ca57f88c9e9dba10081bebc5245d2ab3d9558afcb4)
# Rebuild (build context = cloned upstream under .local/labs/qeeqbox-honeypots):
#   docker build -f Dockerfile -t qeeqbox-honeypots:uhbs-lab .local/labs/qeeqbox-honeypots
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t qeeqbox-honeypots:uhbs-lab .
#
FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/honeypots
COPY . /opt/honeypots
RUN pip install --no-cache-dir -e .
# UHBS inventory high ports for the 10 graded protocols.
EXPOSE 19021 19022 19023 19025 19080 19110 19306 19432 19637 19900
CMD ["python3", "-m", "honeypots", \
     "--termination-strategy", "signal", \
     "--setup", \
     "ftp:19021,ssh:19022,telnet:19023,smtp:19025,http:19080,pop3:19110,mysql:19306,postgres:19432,redis:19637,vnc:19900"]
