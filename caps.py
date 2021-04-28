#!/usr/bin/python3

import os
import yaml
import json
import time
import argparse

crictl_pods = os.popen('crictl ps -o table -q')
crictl_pods_result = crictl_pods.read()
crictl_pods.close()

data = []
namespaces = []

parser = argparse.ArgumentParser()
parser.add_argument('-n','--namespaces', nargs='+', help='<Optional> Outputs information for a given list of namespaces', required=False)
parser.add_argument('-e','--extended-output', help='<Optional> Adds additional information (container\'s uid/gid, privileged bit, entrypoint)', action='store_true', required=False)
args = parser.parse_args()

output_namespaces = []

if args.namespaces is not None:
    output_namespaces = args.namespaces

def namespace_exists(namespace, data):
    exists = False
    index = 0
    if len(data) <= 0:
       #print("Namespace {0} yet to be found".format(namespace))
       pass
    else:
      for entry in data:
        #print("Entry {0}, searching for {1}".format(entry['namespace'], namespace))
        if str(namespace) == str(entry['namespace']):
            #print("Namespace {0} exist in index {1}".format(namespace, index))
            exists = True
            break
        else:
            #print("Namespace {0} yet to be found".format(namespace))
            index += 1
    return exists, index

def pod_exists_in_namespace(pod, namespace_index, data):
   exists = False
   index = 0
   for entry in data[namespace_index]['pods']:
       if str(entry['name']) == str(pod):
           #print("Pod {0} exists in index {1}".format(pod, index))
           exists = True
           break
       else:
           #print("Pod {0} yet to be found".format(pod))
           index += 1
   return exists, index

# Loop over all containers running on this host
for container_id in crictl_pods_result.splitlines():
    crictl_container_inspect = os.popen('crictl inspect --output json ' + container_id)
    crictl_container_inspect_result = crictl_container_inspect.read()
    crictl_container_inspect.close()
    inspect_result_json = json.loads(crictl_container_inspect_result)
    pod_namespace = inspect_result_json['status']['labels']['io.kubernetes.pod.namespace']
    pod_name = inspect_result_json['status']['labels']['io.kubernetes.pod.name']
    container_name = inspect_result_json['status']['labels']['io.kubernetes.container.name']
    container_uid = inspect_result_json['info']['runtimeSpec']['process']['user']['uid']
    container_gid = inspect_result_json['info']['runtimeSpec']['process']['user']['gid']
    container_process = inspect_result_json['info']['runtimeSpec']['process']['args']
    container_image = inspect_result_json['info']['runtimeSpec']['annotations']['io.kubernetes.cri-o.ImageName']
    container_privileged = inspect_result_json['info']['privileged']
    inherited_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['inheritable']
    permitted_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['permitted']
    effective_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['effective']
    bounding_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['bounding']


    # Skip processing this container if it's in a namespace we are not including (default is we include all)
    if len(output_namespaces) > 0 and pod_namespace not in output_namespaces:
        #print("Namespace {0} is not part of the desired output namespaces {1}".format(pod_namespace, output_namespaces))
        continue


    # If the namespace for this container does not yet exist, we create it before continuing ...
    ns_exists, ns_index = namespace_exists(pod_namespace, data)
    if not ns_exists:

        # Create standard dataset for each namespace
        data_ns = {'namespace': pod_namespace, 'pods': [] }

        if args.extended_output:
            # Extend with additional data fields
            kubectl_get_ns_fh = os.popen('''kubectl get -o=jsonpath='{.metadata.labels.openshift\.io/run-level}' namespace ''' + pod_namespace)
            kubectl_get_ns_txt = kubectl_get_ns_fh.read()
            kubectl_get_ns_fh.close()

            if kubectl_get_ns_txt:
                data_ns["openshift.io/run_level"] = kubectl_get_ns_txt
            else:
                data_ns["openshift.io/run_level"] = "(none set)"

        # Append namespace with empty pod set into output data set.
        data.append(data_ns)



    # If the pod for this container does not yet exist, likewise, we create it before continuing ...
    pod_exists, pod_index = pod_exists_in_namespace(pod_name, ns_index, data)
    if not pod_exists:

        data_pod = {'name': pod_name, 'containers': [] }

        if args.extended_output:

           # Extend with additional data fields
           try:
              pod_annotated_scc = inspect_result_json['info']['runtimeSpec']['annotations']['openshift.io/scc']
           except:
              pod_annotated_scc = "(none)"

           data_pod["openshift.io/scc"] = pod_annotated_scc

        # Insert the pod data with empty container set into the existing namespace
        data[ns_index]['pods'].append(data_pod)




    # Finally, append the containers data set into what is now an existing namespace + pod entry in our dataset
    data_c = {'name': container_name, 'capabilities': [{'inherited_set': inherited_set}, {'permitted_set': permitted_set}, {'effective_set': effective_set}, {'bounding_set': bounding_set}]}

    if args.extended_output:
        # Extend with additional data fields
        data_c["image"] = container_image
        data_c["privileged"] = container_privileged
        data_c["user"] = [{'uid': container_uid}, {'gid': container_gid}]
        data_c["entrypoint"] = container_process

    # Append this container to the existing pod's dataset
    data[ns_index]['pods'][pod_index]['containers'].append(data_c)








results = {'caps': data}
print(yaml.dump(results, default_flow_style=False, indent=2, width=1000, sort_keys=False).replace("'", ''))

while True:
    time.sleep(500)

