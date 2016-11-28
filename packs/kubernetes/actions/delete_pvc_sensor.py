from lib import k8s
from st2actions.runners.pythonrunner import Action

from jinja2 import Template
from jinja2 import Environment, PackageLoader

import os
import json
import jinja2
import requests

class deletePVCSensor(Action):

    def run(self, payload):

        allvars = {}

        templateLoader = jinja2.FileSystemLoader( searchpath=self.config['template_path'] )
        templateEnv = jinja2.Environment( loader=templateLoader , lstrip_blocks=True, trim_blocks=True)

        pvc = payload['name']
        customer = payload['labels']['customer']

        try:
            allvars['name'], _ =  pvc.split('.', 1)
            if(customer is not None):
                allvars['name'] =  customer + "-" + allvars['name']
        except ValueError:
            if(customer is not None):
                allvars['name'] =  customer + "-" + pvc
            else:
                allvars['name'] = pvc

        sensorpy = self.config['template_path'] +"/sensors/" + allvars['name'] + "_create.py"
        sensoryaml = self.config['template_path'] + "/sensors/" + allvars['name'] + "_create.yaml"
        os.remove(sensorpy)
        os.remove(sensoryaml)
