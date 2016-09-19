#!/usr/bin/env python

import json
import sys

from st2actions.runners.pythonrunner import Action

class CreateRule(Action):

  def run(self, tokens, cluster):

    tokens = json.loads(tokens)
    for token in tokens:
      #print json.dumps(token, sort_keys=True, indent=2)
      #print "token['Name']: %s" % token['Name']
      #print "cluster: %s" % cluster
      if token['Name'] == cluster:
        print token['ID']
        sys.exit(1)
