# UHBS 5.0.1 score Dockerfile — unit `fortigate-vpn-ssl-http`
# Source: .local/labs/fortigate-vpn-ssl/Dockerfile.lab
# Target image: fortigate-vpn-ssl:uhbs-lab (sha256:0a25874dec879b23806f5444d153100d7658c3f6de93cdfc60824cc33a611f92)
# Rebuild (build context = cloned upstream under .local/labs/fortigate-vpn-ssl):
#   docker build -f Dockerfile -t fortigate-vpn-ssl:uhbs-lab .local/labs/fortigate-vpn-ssl
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t fortigate-vpn-ssl:uhbs-lab .
#
FROM python:3.12-slim-bookworm
WORKDIR /honey
COPY honey/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY honey/ .
ENV FLASK_APP=honey.py
EXPOSE 5000
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
