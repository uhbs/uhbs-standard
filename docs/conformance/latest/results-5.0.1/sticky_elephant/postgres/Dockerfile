# UHBS 5.0.1 score Dockerfile — unit `sticky_elephant-postgres`
# Source: .local/labs/sticky_elephant/Dockerfile.lab
# Target image: sticky_elephant:uhbs-lab (sha256:f4b041ea5aef6145ddb28558ec7f1a05bcd00907331ef1cf9c9e60f7b8403171)
# Rebuild (build context = cloned upstream under .local/labs/sticky_elephant):
#   docker build -f Dockerfile -t sticky_elephant:uhbs-lab .local/labs/sticky_elephant
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t sticky_elephant:uhbs-lab .
#
FROM ruby:3.2-bookworm
WORKDIR /app
COPY . .
RUN gem build sticky_elephant.gemspec && gem install ./sticky_elephant-*.gem
RUN cp sticky_elephant.conf.sample sticky_elephant.conf \
 && sed -i 's/:use_hpf: true/:use_hpf: false/' sticky_elephant.conf \
 && sed -i 's/:host: .*/:host: 0.0.0.0/' sticky_elephant.conf
EXPOSE 5432
CMD ["sticky_elephant", "-c", "/app/sticky_elephant.conf"]
