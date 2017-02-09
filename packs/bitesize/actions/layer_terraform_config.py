import os
import json

from st2actions.runners.pythonrunner import Action

from string import split

class LayerTerraformConfig(Action):

  def _getkv(self, entries):
    data = {}
    for entry in entries:
      if entry['Value'] is not None:
        key = split(entry['Key'], '/')[-1]
        data[key] = entry['Value']

    return data

  def run(self, gdefaults=None, rdefaults=None, rspecifics=None):

    output = {}
    rspdata = {}
    gddata = {}
    rddata = {}

    if rspecifics['data'] is not None:
      rspdata = self._getkv(rspecifics['data'])

    if rdefaults['data'] is not None:
      rddata = self._getkv(rdefaults['data'])

    if gdefaults['data'] is not None:
      gddata = self._getkv(gdefaults['data'])

    print json.dumps(gddata, sort_keys=True, indent=2)
    print json.dumps(rddata, sort_keys=True, indent=2)
    print json.dumps(rspdata, sort_keys=True, indent=2)

    output = gddata.copy()
    output.update(rddata)
    output.update(rspdata)

    return (True, output)
