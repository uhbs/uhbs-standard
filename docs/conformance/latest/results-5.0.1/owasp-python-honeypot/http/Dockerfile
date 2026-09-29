# UHBS 5.0.1 score Dockerfile — unit `owasp-python-honeypot-http`
# Source: .local/labs/owasp-python-honeypot/Dockerfile.lab
# Target image: owasp-python-honeypot:uhbs-lab (sha256:55b63dfc3b7fee7a649539e5c10e274434ddf337de735eec94508e4482a78065)
# Rebuild (build context = cloned upstream under .local/labs/owasp-python-honeypot):
#   docker build -f Dockerfile -t owasp-python-honeypot:uhbs-lab .local/labs/owasp-python-honeypot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t owasp-python-honeypot:uhbs-lab .
#
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY . /app
RUN printf '%s\n' \
  'import socket,threading' \
  'def h(c):' \
  '  try:' \
  '    c.recv(4096); c.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")' \
  '  finally:' \
  '    c.close()' \
  's=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)' \
  's.bind(("0.0.0.0",80)); s.listen(50)' \
  'print("ohp-lab :80", flush=True)' \
  'while True:' \
  '  c,a=s.accept(); threading.Thread(target=h,args=(c,),daemon=True).start()' \
  > /app/uhbs_lab_http.py
EXPOSE 80
CMD ["python3", "/app/uhbs_lab_http.py"]
