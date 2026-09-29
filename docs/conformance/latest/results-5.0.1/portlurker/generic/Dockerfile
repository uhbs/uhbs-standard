# UHBS 5.0.1 score Dockerfile — unit `portlurker-generic`
# Source: .local/labs/portlurker/Dockerfile.lab
# Target image: portlurker:uhbs-lab (sha256:0809f50693b51d82ca643b1a96e58707564ffb1e2c8d2b757f5750d01b72a684)
# Rebuild (build context = cloned upstream under .local/labs/portlurker):
#   docker build -f Dockerfile -t portlurker:uhbs-lab .local/labs/portlurker
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t portlurker:uhbs-lab .
#
FROM rust:1.88 AS builder
WORKDIR /src
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
RUN groupadd -r portlurker && useradd -r -g portlurker portlurker
WORKDIR /opt/portlurker
COPY --from=builder /src/target/release/portlurker /opt/portlurker/portlurker
COPY ./config.uhbs.yml /opt/portlurker/config.yml
RUN chown -R portlurker:portlurker /opt/portlurker
USER portlurker
EXPOSE 8080
CMD ["/opt/portlurker/portlurker"]
