# UHBS 5.0.1 score Dockerfile — unit `beelzebub-mqtt`
# Source: .local/labs/beelzebub/Dockerfile
# Target image: beelzebub:uhbs-lab (sha256:4663259f7336af0895572db5ec697518fc5608846dd54870d0baaec8f70172d3)
# Rebuild (build context = cloned upstream under .local/labs/beelzebub):
#   docker build -f Dockerfile -t beelzebub:uhbs-lab .local/labs/beelzebub
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t beelzebub:uhbs-lab .
#
FROM golang:alpine AS builder

ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux

RUN apk add git

WORKDIR /build

# Download dependency
COPY . .
RUN go mod download

# Install plugins declared in configurations/plugins.yaml (no-op if the file is empty).
# For private plugins, pass a token: docker build --build-arg BEELZEBUB_GITHUB_TOKEN=...
ARG BEELZEBUB_GITHUB_TOKEN=""
RUN BEELZEBUB_GITHUB_TOKEN="$BEELZEBUB_GITHUB_TOKEN" go run . plugin install --no-build

# Build
RUN go build -o main .

WORKDIR /dist

RUN cp /build/main .

# Use scratch image as finally tiny container 
FROM scratch

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /dist/main /

ENTRYPOINT ["/main", "run"]
