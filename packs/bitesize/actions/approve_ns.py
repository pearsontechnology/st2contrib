#!/usr/bin/python

import importlib
import logging
import os
import json
import sys
from datetime import datetime

from st2actions.runners.pythonrunner import Action
from lib import k8s

class ApproveNS(Action):

    def run(self, ns):
        """
        Entry into the action script

        """

        patch = {"metadata":{"labels":{"status":None}}}

        self.env = self.config.get('environment')
        region   = self.config.get('region')
        k8suser  = self.config.get('user')
        k8spass  = self.config.get('password')
        k8surl   = self.config.get('kubernetes_api_url')

        self.k8s = k8s.K8sClient(k8surl, k8suser, k8spass)

        nsdata = self.k8s.k8s[0].read_namespace(ns).to_dict()

        try:
            if 'status' in nsdata['metadata']['labels']:
                print json.dumps(self.k8s.k8s[0].patch_namespace(patch, ns).to_dict(), sort_keys=True, indent=2, default=self._json_serial)
                sys.exit(0)
        except Exception as e:
            sys.stderr.write("Namespace %s status label didnt exist: %s" % (ns, e))
            sys.exit(-1)

    def _json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")

