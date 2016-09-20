#!/usr/bin/env python
import json

from st2actions.runners.pythonrunner import Action

class CreateRule(Action):

  def run(self, tokens, cluster):

    tokens = json.loads(tokens)
    for token in tokens:
      if token['Name'] == cluster:
        print token['ID'],
        return "match"

    print ""
    return "missed"
