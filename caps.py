import os
import yaml
import json
import time

crictl_pods = os.popen('crictl ps -o table -q')
crictl_pods_result = crictl_pods.read()
crictl_pods.close()

data = []
namespaces = []

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


for container_id in crictl_pods_result.splitlines():
    crictl_container_inspect = os.popen('crictl inspect --output json ' + container_id)
    crictl_container_inspect_result = crictl_container_inspect.read()
    crictl_container_inspect.close()
    inspect_result_json = json.loads(crictl_container_inspect_result)
    pod_namespace = inspect_result_json['status']['labels']['io.kubernetes.pod.namespace']
    pod_name = inspect_result_json['status']['labels']['io.kubernetes.pod.name']
    container_name = inspect_result_json['status']['labels']['io.kubernetes.container.name']
    inherited_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['inheritable']
    permitted_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['permitted']
    effective_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['effective']
    bounding_set = inspect_result_json['info']['runtimeSpec']['process']['capabilities']['bounding']
    ns_exists, ns_index = namespace_exists(pod_namespace, data)
    if ns_exists:
        pod_exists, pod_index = pod_exists_in_namespace(pod_name, ns_index, data)
        if pod_exists:
            entry = {'name': container_name, 'capabilities': [{'inherited_set': inherited_set}, {'permitted_set': permitted_set}, {'effective_set': effective_set}, {'bounding_set': bounding_set}]}
            # Append only container to the existing pod
            data[ns_index]['pods'][pod_index]['containers'].append(entry)
        else:
            entry = {'name': pod_name, 'containers': [{'name': container_name, 'capabilities': [{'inherited_set': inherited_set}, {'permitted_set': permitted_set}, {'effective_set': effective_set}, {'bounding_set': bounding_set}]}]}
            # Insert pod and the container into the existing namespace
            data[ns_index]['pods'].append(entry)
    else:
        entry = {'namespace': pod_namespace, 'pods': [{'name': pod_name, 'containers': [{'name': container_name, 'capabilities': [{'inherited_set': inherited_set}, {'permitted_set': permitted_set}, {'effective_set': effective_set}, {'bounding_set': bounding_set}]}]}]}
        # Append namespace, pod and the containers into the output
        data.append(entry)
  
results = {'caps': data}
print(yaml.dump(results, default_flow_style=False, indent=2, width=1000, sort_keys=False).replace("'", ''))

while True:
    time.sleep(500)
