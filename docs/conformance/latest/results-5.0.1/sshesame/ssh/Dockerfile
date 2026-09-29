# UHBS 5.0.1 score Dockerfile — unit `sshesame-ssh`
# Source: .local/labs/sshesame/Dockerfile
# Target image: ghcr.io/jaksi/sshesame:latest (sha256:4061a777a1e5bf393668f109fd8344de5a1708a12ffd891252ed4fec46b571c5)
# Rebuild (build context = cloned upstream under .local/labs/sshesame):
#   docker build -f Dockerfile -t ghcr.io/jaksi/sshesame:latest .local/labs/sshesame
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t ghcr.io/jaksi/sshesame:latest .
#
FROM golang as build-env
WORKDIR /go/src/sshesame
ADD . /go/src/sshesame
RUN go build -o /go/bin/sshesame
RUN sed -i 's/listen_address: .*/listen_address: 0.0.0.0:2022/' sshesame.yaml
FROM gcr.io/distroless/base
COPY --from=build-env /go/bin/sshesame /
COPY --from=build-env /go/src/sshesame/sshesame.yaml /config.yaml
EXPOSE 2022
VOLUME /data
CMD ["/sshesame", "-config", "/config.yaml", "-data_dir", "/data"]
