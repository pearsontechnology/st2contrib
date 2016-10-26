#!/usr/bin/env python
# given a namesapce and policy, create a consul rule 

import json
from st2actions.runners.pythonrunner import Action

class CreateRule(Action):
  def run(self, namespace, policy):
    rule = { "key": { namespace: { "policy" : policy }}, "service": { namespace: { "policy" : policy }}, "event" : { namespace: { "policy" : policy } }}
    print json.dumps(rule)
