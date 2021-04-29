# Get capabilities from all containers running on an OpenShift 4 Cluster

## How it works

We have a small script (`caps.py`) that gets the capabilities information directly from CRI-O.

A [container image](./image.dockerfile) is used, it has the caps.py python script and the `crictl` binary.

What we want is connect to the CRI-O runtime from every OpenShift node in order to get information around the containers that are running on the node, we need to do that for every node in the cluster.

A DaemonSet is used to run our container image on every node, we need to mount the CRI-O sock file inside our container as well as grant access to the host network. Once we have the CRI-O sock file and the host network enabled, we can query the CRI-O runtime of the node from our pod.

## Deploy

1. Create the required objects:

    > **NOTE**: Below command must be run as a cluster-admin user.

    ~~~sh
    oc create -f deploy.yaml
    ~~~
2. A pod will be running on every node inside the `getcaps` namespace:

    ~~~sh
    oc -n getcaps get pods
    ~~~

    ~~~
    NAME            READY   STATUS    RESTARTS   AGE   IP               NODE                 NOMINATED NODE   READINESS GATES
    getcaps-425hh   1/1     Running   0          27m   192.168.123.8    openshift-worker-0   <none>           <none>
    getcaps-jg7rg   1/1     Running   0          27m   192.168.123.6    openshift-master-1   <none>           <none>
    getcaps-l6wzx   1/1     Running   0          27m   192.168.123.5    openshift-master-0   <none>           <none>
    getcaps-szb58   1/1     Running   0          27m   192.168.123.10   openshift-worker-2   <none>           <none>
    getcaps-vmtc5   1/1     Running   0          27m   192.168.123.7    openshift-master-2   <none>           <none>
    getcaps-ztr92   1/1     Running   0          27m   192.168.123.9    openshift-worker-1   <none>           <none>
    ~~~
3. You can get the logs of the pods to get information related to capabilities assigned to containers running on the node:

    ~~~sh
    oc -n getcaps logs getcaps-ztr92
    ~~~

    > **NOTE**: Namespaces appended to the output can be specified by using arguments on the DaemonSet, check the comments in the [deploy.yaml file](./deploy.yaml#L54-L56). An extended output is also available, this output will give you information about container uid/gid, image being used, privileged bit, entrypoint and scc used by the pod. Check the comment in the [deploy.yaml file](./deploy.yaml#L58) to get the extended output enabled. The tool can simulate clearing the permitted and effective capability sets when the container does run with a nonroot UID, in order to enable this output check the comment in the [deploy.yaml file](./deploy.yaml#L59).

    ~~~
    caps:
    - namespace: getcaps
      pods:
      - name: getcaps-zxwr8
        containers:
        - name: getcaps
          capabilities:
          - inherited_set:
            - CAP_CHOWN
            - CAP_DAC_OVERRIDE
            - CAP_FSETID
            - CAP_FOWNER
            - CAP_SETGID
            - CAP_SETUID
            - CAP_SETPCAP
            - CAP_NET_BIND_SERVICE
            - CAP_KILL
          - permitted_set:
            - CAP_CHOWN
            - CAP_DAC_OVERRIDE
            - CAP_FSETID
            - CAP_FOWNER
            - CAP_SETGID
            - CAP_SETUID
            - CAP_SETPCAP
            - CAP_NET_BIND_SERVICE
            - CAP_KILL
          - effective_set:
            - CAP_CHOWN
            - CAP_DAC_OVERRIDE
            - CAP_FSETID
            - CAP_FOWNER
            - CAP_SETGID
            - CAP_SETUID
            - CAP_SETPCAP
            - CAP_NET_BIND_SERVICE
            - CAP_KILL
          - bounding_set:
            - CAP_CHOWN
            - CAP_DAC_OVERRIDE
            - CAP_FSETID
            - CAP_FOWNER
            - CAP_SETGID
            - CAP_SETUID
            - CAP_SETPCAP
            - CAP_NET_BIND_SERVICE
            - CAP_KILL
    - namespace: openshift-kube-apiserver
      pods:
      - name: kube-apiserver-openshift-master-2
        containers:
        - name: kube-apiserver-check-endpoints
          capabilities:
    <OMITTED_OUTPUT>
    ~~~
