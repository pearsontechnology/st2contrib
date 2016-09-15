#!/usr/bin/env python

# take a cassandra cluster name, create a rule

import json

from st2actions.runners.pythonrunner import Action

class CreateRule(Action):

  def run(self, cluster):
    
    rule = { "key": { cluster: { "policy" : "write" }}, "service": { cluster: { "policy" : "write" }}, "event" : { cluster: { "policy" : "write" } }}

    return json.dumps(rule)
