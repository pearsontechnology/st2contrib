import json

from st2actions.runners.pythonrunner import Action

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

        if "quotas" in kwargs:
          allquotas = kwargs['quotas']

        myquotas = quotatemplate
        myspec   = spectemplate
        myquotas['metadata']['namespace'] = namespace
        myquotas['spec'] = myspec['spec']

        # individual spec get priority over quota list
        for key in myspec['spec']['hard']:
            if allquotas and key in allquotas and allquotas[key] != None:
                myspec['spec']['hard'][key] = allquotas[key]
            if key in kwargs and kwargs[key] != None:
                myspec['spec']['hard'][key] = kwargs[key]

        return myquotas
