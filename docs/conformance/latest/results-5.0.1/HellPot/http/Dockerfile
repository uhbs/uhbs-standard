# UHBS 5.0.1 score Dockerfile — unit `HellPot-http`
# Source: docs/conformance/labs/HellPot/Dockerfile.lab
# Target image: hellpot:uhbs-lab (sha256:844413a1a06a87de1f9d03e0ae550e7074ab7437cf52c1a086e2730d935515ca)
# Rebuild (build context = cloned upstream under .local/labs/HellPot):
#   docker build -f Dockerfile -t hellpot:uhbs-lab .local/labs/HellPot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t hellpot:uhbs-lab .
#
# UHBS lab wrapper. Upstream Dockerfile (golang:1.23 + distroless) exists, but
# lab needs Ubuntu runtime plus a bind/catchall config without a curl UA blacklist.
# go.mod requires Go 1.23, so the binary is built with golang:1.23 then copied
# onto ubuntu:latest.
FROM golang:1.23 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /HellPot ./cmd/HellPot

FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /telemetry
COPY --from=build /HellPot /usr/local/bin/HellPot
COPY docker_config.toml /config.toml
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/HellPot", "-c", "/config.toml"]
