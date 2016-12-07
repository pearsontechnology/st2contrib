import requests
import re
import json
import uuid
import boto3
from urlparse import urljoin
from st2actions.runners.pythonrunner import Action

class NfsSpec(Action):

    def run(self, payload):

        customer = payload['labels']['customer']
        pvcname= customer + "-" + payload['name']

        newpayload = {
            'customer': customer,
            'pvcname': pvcname
        }

        #print json.dumps(newpayload, sort_keys=True, indent=2)

        return newpayload

#payload={"resource":"ADDED","uid":"74e019b5-b8cf-11e6-805e-06dd125ad4c4","labels":{"customer":"pulse","name":"bitesize-nfs-prd"},"namespace":"pulse-prd","name":"bitesize-nfs-prd","object_kind":"PersistentVolumeClaim"}
