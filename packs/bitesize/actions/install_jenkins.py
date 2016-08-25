#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from st2actions.runners.pythonrunner import Action
from st2client.client import Client
from st2client.models import KeyValuePair

class K8sClient:

    def __init__(self, master_url, username, password):

        self.k8s = (
            self._get_k8s_client('k8sv1','ApivApi', master_url, username, password),
            self._get_k8s_client('k8sv1beta1','ApisextensionsvbetaApi', master_url, username, password)
        )

    def _get_k8s_client(self, api_version, api_library, master_url, username, password):

        api_version = importlib.import_module(api_version)
        api_library = getattr(api_version, api_library)
        api_version.Configuration().verify_ssl = False
        api_version.Configuration().username = username
        api_version.Configuration().password = password

        apiclient = api_version.ApiClient(
            master_url,
            header_name="Authorization",
            header_value=api_version.configuration.get_basic_auth_token())
        apiclient.default_headers['Content-Type'] = 'application/json'

        client = api_library(apiclient)
        return client

    def _lookup_func(self, func):
        funcmap = {
                   "service": "create_namespaced_service",
                   "ingress": "create_namespaced_ingress",
                   "deployments": "create_namespaced_deployment"
                  }

        return funcmap[func]

    def k8s_action(self, action_type, ns, data):

        myfunc = self._lookup_func(action_type)

        if(myfunc in dir(self.k8s[0])):
            myapi = self.k8s[0]
        if(myfunc in dir(self.k8s[1])):
            myapi = self.k8s[1]

        data = getattr(myapi, myfunc)(data, ns).to_dict()

        print json.dumps(data, sort_keys=True, indent=2, default=self.json_serial)

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")

class UpdateJenkins(Action):

    def run(self, source, ns):
        """
        Entry into the action script

        """

        env      = self.config.get('environment')
        region   = self.config.get('region')
        k8suser  = self.config.get('user')
        k8spass  = self.config.get('password')
        k8surl   = self.config.get('kubernetes_api_url')

        self.project, suffix = ns.split("-")

        # only install jenkins if dev, otherwise carry on
        if suffix != "dev":
            return 0

        self.k8s = K8sClient(k8surl, k8suser, k8spass)
        client = Client(base_url='http://localhost')

        self.source = source
        self.ns = ns
        key = ns + ".gitrepo"

        self.gitrepo = client.keys.get_by_name(key).value

        self.createSvc()
        self.createDep()
        self.createIng()

    def createIng(self):

        template = "jenkins-ingress.json.tmpl"
        data = self.openFile(template)

        data['metadata']['namespace'] = self.ns

        jenkins_url = self.project + ".prsn.io"

        data['spec']['rules'][0]['host'] = jenkins_url

        self.k8s.k8s_action("ingress", self.ns, data)

    def createDep(self):

        template = "jenkins-deployment.json.tmpl"
        data = self.openFile(template)

        data['metadata']['namespace'] = self.ns
        repo = { "name": "SEED_JOBS_REPO", "value": self.gitrepo }

        data['spec']['template']['spec']['containers'][0]['env'].append(repo)

        self.k8s.k8s_action("deployments", self.ns, data)

    def createSvc(self):

        template = "jenkins-svc.json.tmpl"
        data = self.openFile(template)

        for svc in data['items']:

            svc['metadata']['namespace'] = self.ns

            self.k8s.k8s_action("service", self.ns, svc)

    def openFile(self, the_file):
        
        src = self.source + "/" + the_file

        with open(src) as data_file:    
            data = json.load(data_file)
            return data
