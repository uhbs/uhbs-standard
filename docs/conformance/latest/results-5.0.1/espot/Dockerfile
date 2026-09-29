# UHBS 5.0.1 score Dockerfile — unit `espot-http`
# Source: .local/labs/espot/Dockerfile
# Target image: espot:uhbs-lab (sha256:353e164df44fef98a94ebd3da59b01bc0b576e757c1b425d954b871f9422b955)
# Rebuild (build context = cloned upstream under .local/labs/espot):
#   docker build -f Dockerfile -t espot:uhbs-lab .local/labs/espot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t espot:uhbs-lab .
#
# Lab wrapper: upstream README requires NodeJS v0.10.x / Express 3.
# ubuntu:latest cannot install Node 0.10; sqlite3@2 also fails on modern Node.
FROM node:10-buster-slim
WORKDIR /opt/espot
RUN npm install --production express@3.16.5 ejs@2.7.4 request@2.88.2 \
 && npm cache clean --force
COPY . .
EXPOSE 9200
CMD ["node", "app.js"]
