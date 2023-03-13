FROM registry.fedoraproject.org/fedora:37
MAINTAINER Mario Vazquez <mavazque@redhat.com>

RUN set -x && \
    dnf -y update && \
    dnf install -y python3 python3-pyyaml        \
                   cri-tools kubernetes-client        && \
    dnf clean all && \
    rm -rf /var/cache/yum /var/cache/dnf


COPY caps.py /usr/bin/caps.py
RUN chmod 755 /usr/bin/caps.py

USER 1024
ENTRYPOINT ["/usr/bin/python3", "-u", "/usr/bin/caps.py"]

