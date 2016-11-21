import json

from st2actions.runners.pythonrunner import Action
from lib import k8s

quotatemplate = {
    "kind": "ResourceQuota",
    "apiVersion": "v1",
    "metadata": {
        "name": "quota",
        "namespace": "default"
    }
}

spectemplate = {
    "spec": {
        "hard" : {
            "persistentvolumeclaims": "60",
            "pods": "100",
            "replicationcontrollers": "20",
            "resourcequotas": "1",
            "secrets": "10",
            "services": "10"
        }
    }
}

class CreateNSQuotaTemplate(Action):

    def run(self, namespace, **kwargs):

        myquotas = quotatemplate
        myspec   = spectemplate
        myquotas['metadata']['namespace'] = namespace
        myquotas['spec'] = myspec['spec']

        for key in myspec['spec']['hard']:
            if key in kwargs and kwargs[key] != None:
                myspec['spec']['hard'][key] = kwargs[key]

        return myquotas
