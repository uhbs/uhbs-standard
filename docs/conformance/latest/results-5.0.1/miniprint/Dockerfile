# UHBS 5.0.1 score Dockerfile — unit `miniprint-pjl`
# Source: .local/labs/miniprint/Dockerfile
# Target image: miniprint:uhbs-lab (sha256:98d4cf6be313f434372eb225f773860f130b43d374ed376e9701631d088cb1b9)
# Rebuild (build context = cloned upstream under .local/labs/miniprint):
#   docker build -f Dockerfile -t miniprint:uhbs-lab .local/labs/miniprint
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t miniprint:uhbs-lab .
#
FROM python:3.7-alpine

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "./server.py", "--bind", "0.0.0.0"]
