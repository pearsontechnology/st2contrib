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

## To setup the Kubernetes Pack
```
st2 run packs.setup_virtualenv packs=kubernetes
st2ctl reload
```

Note: AWS pack must be enabled and running


### Kubernetes Specific Settings

The following must be enabled on Kubernetes API in ```kube-apiserver.yaml```

```yaml
--runtime-config=extensions/v1beta1/thirdpartyresources=true,extensions/v1beta1/deployments=true
```

Simply add the line above. kube-api container will automatically restart to accept the change.

For more information on using the kubernetes pack with the bitesize pack go here: <https://github.com/pearsontechnology/st2contrib/blob/bite-1061/packs/bitesize/README.md>
