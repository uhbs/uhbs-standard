#!/usr/bin/env bash
# Bootstrap Docker + UHBS grader image on Spot instances (cloud-init user-data).
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release git rsync jq python3-pip

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
  >/etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
usermod -aG docker ubuntu || true
systemctl enable --now docker

mkdir -p /opt/uhbs /telemetry
chown -R ubuntu:ubuntu /opt/uhbs /telemetry || true

# Placeholder: sync_repo.sh will rsync the branch; build image when tree present.
if [[ -f /opt/uhbs/uhbs-standard/Dockerfile ]]; then
  cd /opt/uhbs/uhbs-standard
  docker build -t "uhbs:5.0.1" .
fi

touch /var/lib/cloud/instance/uhbs-docker-ready
echo "uhbs userdata complete" >/var/log/uhbs-userdata.log
