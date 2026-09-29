# UHBS 5.0.1 score Dockerfile — unit `mailoney-smtp`
# Source: .local/labs/mailoney/Dockerfile
# Target image: mailoney:uhbs-lab (sha256:f6939f6ea1d449d4a839a7ba9ed42070656369389516ce647422e8801c89833a)
# Rebuild (build context = cloned upstream under .local/labs/mailoney):
#   docker build -f Dockerfile -t mailoney:uhbs-lab .local/labs/mailoney
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t mailoney:uhbs-lab .
#
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MAILONEY_DB_URL=sqlite:///mailoney.db

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run as non-root user for better security
RUN groupadd -r mailoney && \
    useradd -r -g mailoney mailoney && \
    chown -R mailoney:mailoney /app

USER mailoney

# Expose port
EXPOSE 25

# Run the application
ENTRYPOINT ["python", "main.py"]
