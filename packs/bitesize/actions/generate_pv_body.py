from st2actions.runners.pythonrunner import Action
import sys
import json

class GetStackBuildStatus(Action):
    def run(self, volsize, host, payload):

        name=payload['labels']['name']
        customer=payload['labels']['customer']

        pvbody = {
            "apiVersion": "v1",
            "kind": "PersistentVolume",
            "metadata": {
                "name": name,
                "labels": {
                    "name": name,
                    "customer": customer
                }
            },
            "spec": {
                "capacity": {
                    "storage": volsize
                },
                "accessModes": [ "ReadWriteMany" ],
                "nfs": {
                    "path": "/mnt/nfs/exports",
                    "server": host
                }
            }
        }

        payload = {
            'pvbody':  pvbody,
            'name': name
        }

        print json.dumps(payload, sort_keys=False, indent=2)


        return payload

#payload={"resource":"ADDED","object_kind":"PersistentVolumeClaim","labels":{"customer":"pulse","name":"bitesize-nfs-prd"},"namespace":"pulse-prd","name":"bitesize-nfs-prd","uid":"9918fad3-b8da-11e6-805e-06dd125ad4c4"}
