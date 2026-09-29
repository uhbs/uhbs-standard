# UHBS 5.0.1 score Dockerfile — unit `endlessh-ssh_tarpit`
# Source: .local/labs/endlessh/Dockerfile
# Target image: endlessh:uhbs-lab (sha256:afb3912dd411adf80907456db7db3058515fe3ca8501f8cc22c3d17c37a70dab)
# Rebuild (build context = cloned upstream under .local/labs/endlessh):
#   docker build -f Dockerfile -t endlessh:uhbs-lab .local/labs/endlessh
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t endlessh:uhbs-lab .
#
FROM alpine:3.9 as builder
RUN apk add --no-cache build-base
ADD endlessh.c Makefile /
RUN make


FROM alpine:3.9

COPY --from=builder /endlessh /

EXPOSE 2222/tcp

ENTRYPOINT ["/endlessh"]

CMD ["-v"]
