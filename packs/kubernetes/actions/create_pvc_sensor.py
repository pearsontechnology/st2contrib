from lib import k8s
from st2actions.runners.pythonrunner import Action

from jinja2 import Template
from jinja2 import Environment, PackageLoader

import json
import os
import jinja2
import requests

class createPVCSensor(Action):

    def run(self, payload):

        allvars = {}

        templateLoader = jinja2.FileSystemLoader( searchpath=self.config['template_path'] )
        templateEnv = jinja2.Environment( loader=templateLoader , lstrip_blocks=True, trim_blocks=True)

        #print json.dumps(self.config, sort_keys=True, indent=2)

        myk8s = k8s.K8sClient(self.config)

        user = self.config['user']
        password = self.config['password']
        verify = self.config['verify']

        pvc = payload['name']
        customer = payload['labels']['customer']

        k8s_api_url = self.config['kubernetes_api_url'] + "/api/v1/persistentvolumeclaims"

        r = requests.get(k8s_api_url, auth=(user, password), verify=verify)
        if r.status_code != 200:
            return (False, "Unable to determine remote api endpoint")
        data = json.loads(r.text)

        #print json.dumps(data, sort_keys=True, indent=2)

        pname = None
        for item in data['items']:
          print("Item Name=%s" % item['metadata']['name'])
          if item['metadata']['name'] == pvc:
            pname = item['metadata']['name']
            break

        if pname is None:
            return (False, "Couldn't match PVC with an api endpoint")

        try:
            allvars['name'], _ =  pvc.split('.', 1)
            if(customer is not None):
                allvars['name'] =  customer + "-" + allvars['name']
        except ValueError:
            if(customer is not None):
                allvars['name'] =  customer + "-" + pvc
            else:
                allvars['name'] = pvc

        allvars['watchurl'] = "/apis/prsn.io/v1/watch/" + pname
        allvars['triggername'] = "persistentvolumeclaims"

        print json.dumps(allvars, sort_keys=True, indent=2)

        sensorpy = self.config['template_path'] +"/sensors/" + allvars['name'] + "_create.py"
        sensoryaml = self.config['template_path'] + "/sensors/" + allvars['name'] + "_create.yaml"

        if(os.path.isfile(sensorpy) or os.path.isfile(sensoryaml)):
            return(False, "Sensor Files already Exist.")

        p = open(sensorpy, 'w')
        y = open(sensoryaml, 'w')

        template = templateEnv.get_template('sensor_template.py')
        outputText = template.render( allvars )
        p.write(outputText)
        template = templateEnv.get_template('sensor_template.yaml')
        outputText = template.render( allvars )
        y.write(outputText)

        p.close()
        y.close()
#payload={"resource":"ADDED","uid":"74e019b5-b8cf-11e6-805e-06dd125ad4c4","labels":{"customer":"pulse","name":"bitesize-nfs-prd"},"namespace":"pulse-prd","name":"bitesize-nfs-prd","object_kind":"PersistentVolumeClaim"}
