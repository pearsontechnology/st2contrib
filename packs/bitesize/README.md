# Stackstrom Bitesize Pack

Pack which extends the bitesize [Kubernetes](https://kubernetes.io/) service.

# Current Status & Capabilities
Runs bitesize specific services:
  - request/create namespaces on kubernetes
  - react to kubernetes third party resource object creation to create aws hosted services
  - install the bitesize testapp
  - migrate resources between A/B clusters
  - create consul/vault tokens, and add them as kubernetes secrets
  - install bitesize jenkins
  

Templates for new sensors are installed to the pack root directory by default

## Configuration

config.yaml defines bitesize specific default database settings
This is generated on cluster deployment using ansible roles
( https://github.com/pearsontechnology/ansible-roles/blob/dev/roles/stackstorm/templates/bitesize/config.yaml.j2 )

Installation is via ansible using the stackstorm role

The Bitesize pack requires the aws and kubernetes st2contrib packs

### Testing third party resources

Create a yaml file with the below:

#### Cassandra database

```yaml
metadata:
    name: cass1
    namespace: default
    labels:
        type: cassandra.prsn.io
        version: '2.2'
        stack_name: cass1
apiVersion: prsn.io/v1
kind: Cassandra
description: ""
```

#### mysql (rds)

```yaml
metadata:
    name: mysql1
    namespace: default
    labels:
        type: mysql.prsn.io
        stack_name: mysql1
apiVersion: prsn.io/v1
kind: Mongo
description: ""
```

#### mongo

```yaml
metadata:
    name: mongo1
    labels:
        type: mongo.prsn.io
        version: '2.6'
        stack_name: mongo1
apiVersion: prsn.io/v1
kind: Mongo
description: ""
```

With kubectl run:

```
kubectl create -f name_of_your_file.yaml
```

to view the resources (eg):

```
kubectl get cassandras -o json
```

Upon creation the kubernetes sensor should detect the resource, and send a trigger.
The bitesize pack has rules that match the trigger and call bitesize workflows
For cassandra and mongo you should see their creation in cloudformation
For mysql (rds) you should see the creation in the rds console
