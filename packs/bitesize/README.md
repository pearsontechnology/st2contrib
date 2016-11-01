# Kubernetes sensor integration

Pack which allows integration with [Kubernetes](https://kubernetes.io/) service.

# Current Status & Capabilities
Creates a StackStorm Sensor (watch) on Kubernetes ThirdPartyResource API endpoint
Listens for new events. If 'ADDED', rule can pick up and create and AWS RDS database.

## Configuration

config.yaml includes:
```yaml
user: ""
password: ""
kubernetes_api_url: "https://kube_api_url"
extension_url: "/apis/extensions/v1beta1/watch/thirdpartyresources"
```
Where kube_api_url = The FQDN to your Kubernetes API endpoint.

Note: Currently SSL verification is turned off. This is a WIP.

## To setup the bitesize Pack
```
st2 run packs.setup_virtualenv packs=kubernetes
st2ctl reload
```

Note: The AWS and kubernetes packs must be enabled and running


### Kubernetes Specific Settings

The following must be enabled on Kubernetes API for versions prior to kubernetes 1.4 ```kube-apiserver.yaml```

```yaml
--runtime-config=extensions/v1beta1/thirdpartyresources=true,extensions/v1beta1/deployments=true
```

Simply add the line above. kube-api container will automatically restart to accept the change.



### To Test the RDS create event in the bitesize Pack

Create a yaml file with something like below:

```yaml
apiVersion: prsn.io/v1
kind: Mysql
metadata:
  name: demodb
  namespace: demo
spec:
  version: 5.6
  options:
    param_filename: none
    option_filename: none
```

With kubectl run:

```
kubectl create -f name_of_your_file.yaml
```

### Deploying Mongo Replicaset in the bitesize Pack

First of all, do these 2 manual steps -

1. Add vault token to stackstorm:

  * Get your vault token from the kubernetes master as follows:

    ```
    [root@master-a ~]# echo "$(<vault_keys.txt)" | awk '/Initial/ {print $4}'
    eg22efe3-d7d6-acc1-3ac8-3c803892bc77a
    ```

  * now login to your stackstorm instance and add the vault token to /opt/stackstorm/packs/vault/config.yaml as follows:
    ```
    ---
    url: 'https://vault-prelive.pidah.prsn-dev.io'
    cert: ''
    token: 'eg22efe3-d7d6-acc1-3ac8-3c803892bc77a'
    verify: false
    ```

2. Add the public ip's of the stackstorm and vpc-nat instance to the VPC nat security group:

  * Get the public IP address of your stackstorm instance and the VPC nat instance via the AWS console.
  * Then add these two IP addresses to the vpc-nat security group `nat-sg-<environment name>` Inbound access to port 443 eg:
    ```
    nat-sg-pidah Inbound HTTPS 52.23.12.17/32
    ```

    _Note:_ These manual steps above would no longer be required when we move to dockerized stackstorm running directly on the PAAS ( or possibly Petsets ).

3. Create the mongo thirdparty custom resource:

  * Create a yaml file with something like below:

    ```yaml
    apiVersion: prsn.io/v1
    kind: Mongo
    metadata:
      name: mongo-demodb
      namespace: demo
    spec:
      version: 2.6
      stack_name: demo-stack
    ```

  * With kubectl run:

    ```
    kubectl create -f name_of_your_file.yaml
    ```

### Deploying Cassandra clusters in the bitesize Pack

1. As with the mongo deployment above, add the vault token to stackstorm, and the public ip's of stackstorm and vpc-nat to the VPC nat security group.

2. Create a demo namespace

3. Create a cassandra third party custom resource:

  * Create a yaml file with the below:

    ```yaml
    apiVersion: prsn.io/v1
    kind: Cassandra
    metadata:
      name: cassdb
      namespace: demo
    spec:
      version: 2.2
      stack_name: demo-cass
    ```

  * With kubectl run:

    ```
    kubectl create -f name_of_your_file.yaml
    ```

4. Once the stack is built, the instances will continue to deploy and configure - this takes around 20m. The last thing you'll see in stackstorm is 3 cass_acl and a standalone vault_write action in the stackstorm history tab

5. Upon completion there will be keys in consul under namespace/clustername and vault under the same for the password. The user will be bitesize

6. To see the cluster status, login to any of the cassandra nodes and run:

  ``` /home/cassandra/current/bin/nodetool status ```

7. To delete, remove the third party custom resource within kubernetes

  * With kubectl run:

    ```
    kubectl delete cassandra cassdb --namespace=demo
    ```

  * You should be able to observe the deletion in both stackstorm and the cloudformation console
