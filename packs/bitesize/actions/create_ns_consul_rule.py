#!/usr/bin/env python

# given a namesapce and policy, create a consul rule 

import json

from st2actions.runners.pythonrunner import Action

class CreateRule(Action):

  def run(self, cluster, policy):

    rule = { "key": { cluster: { "policy" : policy }}, "service": { cluster: { "policy" : policy }}, "event" : { cluster: { "policy" : policy } }}

    print json.dumps(rule)
