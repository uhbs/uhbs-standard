# UHBS 5.0.1 score Dockerfile — unit `ssh-auth-logger-ssh`
# Source: .local/labs/ssh-auth-logger/Dockerfile
# Target image: justinazoff/ssh-auth-logger:latest (sha256:5741d6672aaa078810f6d6f1bc6e138029a194b43acc5ca43d2354c314d255e1)
# Rebuild (build context = cloned upstream under .local/labs/ssh-auth-logger):
#   docker build -f Dockerfile -t justinazoff/ssh-auth-logger:latest .local/labs/ssh-auth-logger
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t justinazoff/ssh-auth-logger:latest .
#
FROM golang:latest

LABEL maintainer="Justin Azoff <justin.azoff@gmail.com>" \
      org.opencontainers.image.title="ssh-auth-logger" \
      org.opencontainers.image.description="A low/zero interaction ssh authentication logging honeypot" \
      org.opencontainers.image.source="https://github.com/JustinAzoff/ssh-auth-logger" \
      org.opencontainers.image.url="https://hub.docker.com/r/justinazoff/ssh-auth-logger" \
      org.opencontainers.image.documentation="https://github.com/JustinAzoff/ssh-auth-logger#" \
      org.opencontainers.image.version="0.1.0"

ENV USER=nobody
ENV SSHD_BIND=:2222
ENV TELNET_BIND=:2323

WORKDIR /app

COPY . .

RUN go install . && \
    touch /var/log/ssh-auth-logger.log && \
    chown $USER /var/log/ssh-auth-logger.log && \
    chmod 644 /var/log/ssh-auth-logger.log

USER $USER

EXPOSE 2222 2323

CMD test -f /var/log/ssh-auth-logger.log || { echo 'Creating log file...' && touch /var/log/ssh-auth-logger.log ; }; /go/bin/ssh-auth-logger 2>&1 | tee -a /var/log/ssh-auth-logger.log
