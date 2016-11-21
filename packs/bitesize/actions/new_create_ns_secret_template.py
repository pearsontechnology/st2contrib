import json
import base64

from st2actions.runners.pythonrunner import Action

secrettemplate = {
    "kind": "Secret",
    "apiVersion": "v1",
    "metadata": {
        "name": "",
        "namespace": ""
    },
    "data": {
        "" : ""
    }
}

class CreateNSSecretTemplate(Action):

    def run(self, namespace, name, value):

        b64value = base64.encodestring(value)
        secretdata = {name: b64value}

        mysecret = secrettemplate
        mysecret['metadata']['name'] = name
        mysecret['metadata']['namespace'] = namespace
        mysecret['data'] = secretdata

        return mysecret
