# UHBS 5.0.1 score Dockerfile — unit `mockssh-ssh`
# Source: docs/conformance/labs/mockssh/Dockerfile.lab
# Target image: mockssh:uhbs-lab (sha256:c3eb44567ad5b8b4060dd1222ae788e3b9f2b020cedd35591e39f35c81c316be)
# Rebuild (build context = cloned upstream under .local/labs/mockssh):
#   docker build -f Dockerfile -t mockssh:uhbs-lab .local/labs/mockssh
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t mockssh:uhbs-lab .
#
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip3 install --break-system-packages --no-cache-dir -e .

# Cisco example binds 127.0.0.1:9999; lab entry listens 0.0.0.0:2222 as testadmin/x.
COPY lab_cisco.py /app/lab_cisco.py
EXPOSE 2222
CMD ["python3", "/app/lab_cisco.py"]
