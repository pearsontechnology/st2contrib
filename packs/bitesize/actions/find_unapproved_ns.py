#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from pprint import pprint

from st2actions.runners.pythonrunner import Action

class GetUnapproved(Action):

    def run(self, allns):

        output = []

        for ns in allns['items']:
            if 'metadata' in ns and 'labels' in ns['metadata'] and ns['metadata']['labels'] is not None and 'status' in ns['metadata']['labels']:
                output.append(ns['metadata']['name'])

        if len(output) > 0:
            print json.dumps(output)
        else:
            print "{}"

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")
