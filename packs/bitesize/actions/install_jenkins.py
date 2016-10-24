#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from st2actions.runners.pythonrunner import Action
from st2client.client import Client
from st2client.models import KeyValuePair

from lib import k8s

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
        domain   = self.config.get('domain')

        self.project, suffix = ns.split("-")

        # only install jenkins if dev, otherwise carry on
        if suffix != "dev":
            return 0

        self.k8s = k8s.K8sClient(k8surl, k8suser, k8spass)
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

        jenkins_url = self.project + self.domain

        data['spec']['rules'][0]['host'] = jenkins_url

        self.k8s.k8s_action("ingress", self.ns, data, action_type="create")

    def createDep(self):

        template = "jenkins-deployment.json.tmpl"
        data = self.openFile(template)

        data['metadata']['namespace'] = self.ns
        repo = { "name": "SEED_JOBS_REPO", "value": self.gitrepo }

        data['spec']['template']['spec']['containers'][0]['env'].append(repo)

        self.k8s.k8s_action("deployments", self.ns, data, action_type="create")

    def createSvc(self):

        template = "jenkins-svc.json.tmpl"
        data = self.openFile(template)

        for svc in data['items']:

            svc['metadata']['namespace'] = self.ns

            self.k8s.k8s_action("service", self.ns, svc, action_type="create")

    def openFile(self, the_file):

        src = self.source + "/" + the_file

        with open(src) as data_file:
            data = json.load(data_file)
            return data
