# UHBS 5.0.1 score Dockerfile — unit `honeytrap-ssh`
# Source: .local/labs/honeytrap/Dockerfile.lab
# Target image: honeytrap:uhbs-lab (sha256:bf9df058337b7be44768d527f10483e653f771e3a54e97c47c56a563219f20a0)
# Rebuild (build context = cloned upstream under .local/labs/honeytrap):
#   docker build -f Dockerfile -t honeytrap:uhbs-lab .local/labs/honeytrap
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t honeytrap:uhbs-lab .
#
FROM golang:latest AS go

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

ADD . /src/honeytrap

ARG LDFLAGS=""

WORKDIR /src/honeytrap
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -tags="" -ldflags="$(go run scripts/gen-ldflags.go)" -o /go/bin/app .

FROM alpine
MAINTAINER  Remco Verhoef <remco.verhoef@dutchsec.com>

RUN apk --update upgrade && apk add curl ca-certificates && rm -rf /var/cache/apk/*
RUN apk add ca-certificates && update-ca-certificates

RUN mkdir /config /data

RUN curl -s -o /config/config.toml https://raw.githubusercontent.com/honeytrap/honeytrap-configs/master/server-standalone/config-server-standalone.toml
COPY --from=go /go/bin/app /honeytrap/honeytrap

ENTRYPOINT ["/honeytrap/honeytrap", "--config", "/config/config.toml", "--data", "/data/"]

EXPOSE 8022 5900
