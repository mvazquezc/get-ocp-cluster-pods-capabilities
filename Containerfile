FROM registry.fedoraproject.org/fedora:34
MAINTAINER Dave Baker <dbaker@redhat.com>

RUN set -x && \
    dnf -y update && \
    dnf install -y python3 python3-pyyaml        \
                   cri-tools kubernetes-client        && \
    dnf clean all && \
    rm -rf /var/cache/yum /var/cache/dnf


# Obsolete - if we have need for absolute latest clients, we can install them from upstream:
# If we do this, be sure to verify checksums
#
# RUN cd /usr/bin && \
#    curl -L -o- https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.21.0/crictl-v1.21.0-linux-amd64.tar.gz | tar zxvf - crictl
#
# RUN cd /usr/bin && \
#    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
#    chmod a+x kubectl
#

# All python reqs are handled in RPMs; no need for pip
# COPY requirements.txt .
# RUN pip3 install -r requirements.txt

COPY caps.py /usr/bin/caps.py
RUN chmod 755 /usr/bin/caps.py

USER 1024
ENTRYPOINT ["/usr/bin/python3", "-u", "/usr/bin/caps.py"]

