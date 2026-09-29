# UHBS 5.0.1 score Dockerfile — unit `trapster-dns`
# Source: .local/labs/trapster/Dockerfile
# Target image: trapster:uhbs-lab (sha256:fe8aa1c13246549e6c024a4cb3f558e0dfb6ca75e17d845917ef2fbafce90314)
# Rebuild (build context = cloned upstream under .local/labs/trapster):
#   docker build -f Dockerfile -t trapster:uhbs-lab .local/labs/trapster
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t trapster:uhbs-lab .
#
FROM python:3.11-slim

WORKDIR /app

# Copy setup files first to leverage cache for dependency installation
COPY requirements.txt setup.py MANIFEST.in README.md /app/
COPY trapster/__init__.py /app/trapster/__init__.py

# Install the package with AI features enabled
# This will install both base requirements and AI extras
RUN pip install --no-cache-dir .[ai]

# Create configuration directory
RUN mkdir -p /etc/trapster

# Copy application code - these are likely to change more frequently
# so we place them after the dependency installation
COPY trapster/data/trapster.conf /etc/trapster/trapster.conf
COPY main.py /app/
COPY trapster /app/trapster/

# Run main.py when the container launches
ENTRYPOINT ["python3", "main.py", "-c", "/etc/trapster/trapster.conf"]
