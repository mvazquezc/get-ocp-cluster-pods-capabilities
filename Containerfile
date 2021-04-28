# Upstream container is published at: quay.io/mavazque/getcriocaps:latest

# This container is at quay.io/dbaker/getcriocaps:v1
FROM registry.fedoraproject.org/fedora:34
MAINTAINER Dave Baker <dbaker@redhat.com>


RUN set -x && \
    dnf -y update && \
    dnf install -y python3 python3-pip && \
    dnf clean all && \
    rm -rf /var/cache/yum /var/cache/dnf


# install crictl client
# TODO: confirm checksum!!
## RUN curl -L https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.21.0/crictl-v1.21.0-linux-amd64.tar.gz -o crictl.tar.gz && tar xvfz crictl.tar.gz && mv crictl /usr/bin && rm -f crictl.tar.gz

RUN cd /usr/bin && \
    curl -L -o- https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.21.0/crictl-v1.21.0-linux-amd64.tar.gz | tar zxvf - crictl

# install kubectl client - https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
# TODO: confirm checksum!!
RUN cd /usr/bin && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod a+x kubectl

# python reqs are in different container layer than script for faster rebuilds
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY caps.py /usr/bin/caps.py
RUN chmod 755 /usr/bin/caps.py

USER 1024
ENTRYPOINT ["/usr/bin/python3", "-u", "/usr/bin/caps.py"]

