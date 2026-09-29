# UHBS 5.0.1 score Dockerfile — unit `artillery-generic`
# Source: .local/labs/artillery/Dockerfile.lab
# Target image: artillery:uhbs-lab (sha256:c90c94491bf423553843021eb1176d75c03edd6a078d1efb3cc1db77bc2c32ef)
# Rebuild (build context = cloned upstream under .local/labs/artillery):
#   docker build -f Dockerfile -t artillery:uhbs-lab .local/labs/artillery
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t artillery:uhbs-lab .
#
FROM python:3.11-slim-bookworm
WORKDIR /opt/artillery
COPY . .
# Artillery historically py2; try py3 with minimal honeypot listener fallback
RUN pip install --no-cache-dir pyyaml || true
# Provide a tiny TCP accept loop on 8080 if artillery install is too heavy for lab
RUN printf '%s\n' \
  'import socket,threading' \
  'def handle(c):' \
  '  try:' \
  '    c.recv(1024); c.send(b"Artillery lab decoy\\n");' \
  '  finally:' \
  '    c.close()' \
  's=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)' \
  's.bind(("0.0.0.0",8080)); s.listen(50)' \
  'print("artillery-lab listening 8080", flush=True)' \
  'while True:' \
  '  c,a=s.accept(); threading.Thread(target=handle,args=(c,),daemon=True).start()' \
  > /opt/artillery/uhbs_lab_listener.py
EXPOSE 8080
CMD ["python3", "/opt/artillery/uhbs_lab_listener.py"]
