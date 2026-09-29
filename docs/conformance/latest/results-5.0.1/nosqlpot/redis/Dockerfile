# UHBS 5.0.1 score Dockerfile — unit `nosqlpot-redis`
# Source: .local/labs/nosqlpot/Dockerfile.lab
# Target image: nosqlpot:uhbs-lab (sha256:d83006e9ad8465696cbb0a9f9fa2f017eb72e7779be6eda2fbee572a2b1d8209)
# Rebuild (build context = cloned upstream under .local/labs/nosqlpot):
#   docker build -f Dockerfile -t nosqlpot:uhbs-lab .local/labs/nosqlpot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t nosqlpot:uhbs-lab .
#
FROM python:3.11-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir twisted
COPY . .
EXPOSE 6379
CMD ["python3", "nosqlpot.py", "-deploy", "redis", "-port", "6379"]
