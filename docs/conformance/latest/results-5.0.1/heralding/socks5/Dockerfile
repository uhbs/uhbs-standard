# UHBS 5.0.1 score Dockerfile — unit `heralding-socks5`
# Source: docs/conformance/labs/heralding/Dockerfile.lab
# Target image: heralding:uhbs-lab (sha256:3acb74f08830ef00aefd5c19bc94697f41317827928c14ac14b09d9c018a37f4)
# Rebuild (build context = cloned upstream under .local/labs/heralding):
#   docker build -f Dockerfile -t heralding:uhbs-lab .local/labs/heralding
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t heralding:uhbs-lab .
#
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --user --no-cache-dir -r requirements.txt \
    && python setup.py install --user

WORKDIR /tmp
EXPOSE 21 22 25
CMD ["heralding"]
