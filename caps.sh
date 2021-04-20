#!/bin/bash

GO_TEMPLATE='
==== NAMESPACE: {{index .status.labels "io.kubernetes.pod.namespace"}} ====
==== POD NAME: {{index .status.labels "io.kubernetes.pod.name"}} ====
==== CONTAINER NAME: {{index .status.labels "io.kubernetes.container.name"}} ====
==== INHERITED SET: {{.info.runtimeSpec.process.capabilities.inheritable}} ====
==== PERMITTED SET: {{.info.runtimeSpec.process.capabilities.permitted}} ====
==== EFFECTIVE SET: {{.info.runtimeSpec.process.capabilities.effective}} ====
==== BOUNDING SET: {{.info.runtimeSpec.process.capabilities.bounding}} ====
'

for CONTAINERID in $(crictl ps -o table -q)
do
  crictl inspect --output go-template --template="${GO_TEMPLATE}" $CONTAINERID
  echo "----------------------------------------------------------------"
done

sleep infinity
