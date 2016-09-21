#!/usr/bin/env python
# given a namesapce and policy, create a vault rule 

import json
from st2actions.runners.pythonrunner import Action

class CreateVaultRule(Action):
  def run(self, namespace, policy):
    rule = { "path": { "sys/*": { "policy" : "deny" }}, "path": { "secret/" + namespace + "/*" : { "policy" : policy }}}
    print json.dumps(rule)
