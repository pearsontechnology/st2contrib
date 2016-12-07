from st2actions.runners.pythonrunner import Action
import sys
import json

class GetStackBuildStatus(Action):
    def run(self, volsize, host, payload):

        customer=payload['labels']['customer']
        name=customer + "-" + payload['labels']['name']

        #Verify volsize (NFS share) exists. Don't create PV if it does not exist (could mean there is no NFS server).
        if volsize is None:
            msg = 'Cannot create PV. No Volume Size in Consul...NFS server may not be deployed/sharing.'
            self.logger.error(msg)
            raise Exception(msg)

        #Verify host exists in consule. Don't create PV if it does not exist (could mean there is no NFS server).
        if host is None:
            msg = 'Cannot create PV. No NFS Host defined in Consul...NFS server may not be deployed/sharing.'
            self.logger.error(msg)
            raise Exception(msg)


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
