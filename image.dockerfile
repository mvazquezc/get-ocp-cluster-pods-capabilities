# Published at: quay.io/mavazque/getcriocaps:latest
FROM fedora:33
RUN dnf install -y python3 python3-pip && dnf clean all
RUN curl -L https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.21.0/crictl-v1.21.0-linux-amd64.tar.gz -o crictl.tar.gz && tar xvfz crictl.tar.gz && mv crictl /usr/bin && rm -f crictl.tar.gz
COPY requirements.txt .
COPY caps.py /usr/bin/caps.py
RUN pip3 install -r requirements.txt
USER 1024
CMD ["python3", "/usr/bin/caps.py"]
