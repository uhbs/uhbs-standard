# UHBS 5.0.1 score Dockerfile — unit `conpot-modbus`
# Source: docs/conformance/labs/conpot/Dockerfile.lab
# Target image: conpot:uhbs-lab (sha256:af49c2e9b9d8a8f1198375417bcdb809af12d6356810cb8bbd0203df8f3c6a2f)
# Rebuild (build context = cloned upstream under .local/labs/conpot):
#   docker build -f Dockerfile -t conpot:uhbs-lab .local/labs/conpot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t conpot:uhbs-lab .
#
# Lab wrapper: pyfilesystem still imports pkg_resources (removed in setuptools 82+).
FROM conpot:lab
USER root
RUN pip install --no-cache-dir 'setuptools<81'
USER conpot
ENTRYPOINT ["conpot"]
CMD ["--template", "default", "--logfile", "/var/log/conpot/conpot.log", "-f", "--temp_dir", "/tmp"]
