#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from st2actions.runners.pythonrunner import Action

nstemplate = {
    "kind": "Namespace",
    "apiVersion": "v1",
    "metadata": {
        "name": "",
        "labels": {
            "project": "",
            "environment": ""
        }
    },
}

class CreateNSTemplate(Action):

    def run(self, project, namespace):

        self.project = project
        self.namespace = namespace

        return (True, self._createNSConfig())

    def _createNSConfig(self):
        myconf = nstemplate
        myconf['metadata']['name'] = self.namespace
        myconf['metadata']['labels']['project'] = self.project
        myconf['metadata']['labels']['environment'] = self.config['environment']

        return myconf
