# UHBS 5.0.1 score Dockerfile — unit `pghoney-postgres`
# Source: docs/conformance/labs/pghoney/Dockerfile.lab
# Target image: pghoney:uhbs-lab (sha256:09367f266cf3fde5bd31d367e5d3b26d6637329d587bcde9b935490c5ee7bc4e)
# Rebuild (build context = cloned upstream under .local/labs/pghoney):
#   docker build -f Dockerfile -t pghoney:uhbs-lab .local/labs/pghoney
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t pghoney:uhbs-lab .
#
FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV GOPROXY=https://proxy.golang.org,direct
ENV GO111MODULE=on

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
COPY pghoney.lab.conf /app/pghoney.conf

RUN go mod init github.com/betheroot/pghoney \
    && go get github.com/Sirupsen/logrus@v1.0.6 \
    && go get github.com/fw42/go-hpfeeds@master \
    && go get github.com/lib/pq \
    && go build -o /usr/local/bin/pghoney .

EXPOSE 5432
CMD ["pghoney", "-config", "/app/pghoney.conf"]
