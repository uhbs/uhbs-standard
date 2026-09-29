# UHBS 5.0.1 score Dockerfile — unit `owa-honeypot-http`
# Source: .local/labs/owa-honeypot/Dockerfile.lab
# Target image: owa-honeypot:uhbs-lab (sha256:d06636c5de94af9eff389ece0d559dbb69e97b8840ddd153803687ea1f4c2e1b)
# Rebuild (build context = cloned upstream under .local/labs/owa-honeypot):
#   docker build -f Dockerfile -t owa-honeypot:uhbs-lab .local/labs/owa-honeypot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t owa-honeypot:uhbs-lab .
#
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Inventory expects :8080; upstream defaults to :80
ENV FLASK_RUN_PORT=8080
EXPOSE 8080
CMD ["python3", "-c", "from owa_pot import create_app; create_app().run(debug=False, port=8080, host='0.0.0.0')"]
