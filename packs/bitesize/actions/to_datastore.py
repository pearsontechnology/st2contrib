#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from st2actions.runners.pythonrunner import Action
from st2client.client import Client
from st2client.models import KeyValuePair

class ApproveNS(Action):

    def run(self, ns, key, value):
        """
        Entry into the action script

        """

        client = Client(base_url='http://localhost')

        keyname = ns + "." + key
        client.keys.update(KeyValuePair(name=keyname, value=value))

