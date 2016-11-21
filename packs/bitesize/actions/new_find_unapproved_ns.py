#!/usr/bin/python

import importlib
import logging
import os
import json
from datetime import datetime

from pprint import pprint

from st2actions.runners.pythonrunner import Action

class FindUnapproved(Action):

    def run(self, allns):
        output = []

        tmp = allns.replace('\'', '"')
        tmp = tmp.replace('u"', '"')

        tmpj = json.loads(tmp)

        unapp = {}

        for item in tmpj:

            k = item['Key']

            tree = k.split('/')
            if tree[-1] == "unapproved":
              proj = tree[1]
              ns = tree[2]

              if proj not in unapp:
                unapp[proj] = []
              unapp[proj].append(ns)

        return (True, json.dumps(unapp))
