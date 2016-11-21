#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from st2actions.runners.pythonrunner import Action
from st2client.client import Client
from st2client.models import KeyValuePair

class UnapprovedNS(Action):

    def run(self, project, ns_list, gitrequired):
        """

        """

        client = Client(base_url='http://localhost')

        print type(ns_list)
        print type(gitrequired)
        if gitrequired: ns_list.append('jnk')

        #print "project: %s" % project
        #print "ns_list: %s" % ns_list
        #print "gitreq:  %s" % gitrequired

        key = "unapproved_" + project
        val = ','.join(ns_list)

        print client.keys.update(KeyValuePair(name=key, value=val))

        return (False, "for now")
