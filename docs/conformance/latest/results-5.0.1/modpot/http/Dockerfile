# UHBS 5.0.1 score Dockerfile — unit `modpot-http`
# Source: .local/labs/modpot/Dockerfile.lab
# Target image: modpot:uhbs-lab (sha256:7f16d47286f81f8a9a90cb91678014952bea5ef78a036c29daf09e42a1ec9dd5)
# Rebuild (build context = cloned upstream under .local/labs/modpot):
#   docker build -f Dockerfile -t modpot:uhbs-lab .local/labs/modpot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t modpot:uhbs-lab .
#
FROM golang:1.22-bookworm AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /modpot .
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=build /modpot /app/modpot
COPY config.uhbs.yaml /app/config.yaml
COPY templates /app/templates
COPY web /app/web
COPY responders /app/responders
EXPOSE 8080
CMD ["/app/modpot", "-config", "/app/config.yaml"]
