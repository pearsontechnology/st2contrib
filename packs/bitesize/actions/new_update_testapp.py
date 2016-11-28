import os
import json
import yaml
import string

from st2actions.runners.pythonrunner import Action

class UpdateTestApp(Action):

  def update_vars(self, srcfile):

    output = []

    #with open(srcfile, 'r') as yamlfile:
    #  data = yaml.load_all(yamlfile)
    stream = open(srcfile, "r")
    data = yaml.load_all(stream)

    for single in data:
      print single
      output.append(single)

    return output

  def run(self, templatedir):

    self.allvars = {}
    output = {}

    for key, thefile in [('dep', 'jenkins-deployment.yaml'), ('ing', 'jenkins-ing.yaml'), ('svc', 'jenkins-svc.yaml')]:
      thefile = templatedir + "/" + thefile
      output[key] = self.update_vars(thefile)

    return output
