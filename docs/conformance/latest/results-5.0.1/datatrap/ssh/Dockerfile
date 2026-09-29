# UHBS 5.0.1 score Dockerfile — unit `datatrap-ssh`
# Source: .local/labs/datatrap/Dockerfile
# Target image: datatrap:uhbs-lab (sha256:c770fa469eac6850e2795447b47c5cd8f26e3051547eaae2f1819ec9774a48e0)
# Rebuild (build context = cloned upstream under .local/labs/datatrap):
#   docker build -f Dockerfile -t datatrap:uhbs-lab .local/labs/datatrap
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t datatrap:uhbs-lab .
#
FROM python:3.12-alpine
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# verify that the license file is present for paramiko
RUN test -f /usr/local/lib/python3.12/site-packages/paramiko-*.dist-info/LICENSE
WORKDIR /app/
COPY src/. .
ENV PYTHONPATH "/app"
ENTRYPOINT ["python", "-u", "honeypot_main.py"]
