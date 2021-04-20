#!/bin/bash

for CONTAINERID in $(crictl ps -o table -q)
do
  POD_NAME=$(crictl inspect --output go-template --template='{{index .status.labels "io.kubernetes.pod.name"}}' $CONTAINERID)
  CONTAINER_NAME=$(crictl inspect --output go-template --template='{{index .status.labels "io.kubernetes.container.name"}}' $CONTAINERID)
  INHERITED_SET=$(crictl inspect --output go-template --template='{{.info.runtimeSpec.process.capabilities.inheritable}}' $CONTAINERID)
  PERMITTED_SET=$(crictl inspect --output go-template --template='{{.info.runtimeSpec.process.capabilities.permitted}}' $CONTAINERID)
  EFFECTIVE_SET=$(crictl inspect --output go-template --template='{{.info.runtimeSpec.process.capabilities.effective}}' $CONTAINERID)
  BOUNDING_SET=$(crictl inspect --output go-template --template='{{.info.runtimeSpec.process.capabilities.bounding}}' $CONTAINERID)
  echo "==== POD NAME: ${POD_NAME} ===="
  echo "==== CONTAINER NAME: ${CONTAINER_NAME} ===="
  echo "==== INHERITED SET: ${INHERITED_SET} ===="
  echo "==== PERMITTED SET: ${PERMITTED_SET} ===="
  echo "==== EFFECTIVE SET: ${EFFECTIVE_SET} ====" 
  echo "==== BOUNDING SET: ${BOUNDING_SET} ===="
  echo "----------------------------------------------------------------"
done
