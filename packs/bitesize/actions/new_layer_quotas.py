import os
import json

from st2actions.runners.pythonrunner import Action

from string import split

class LayerQuotas(Action):

  def _getkv(self, entries):
    data = {}
    for entry in entries:
      if entry['Value'] is not None:
        key = split(entry['Key'], '/')[-1]
        data[key] = entry['Value']

    return data

  def run(self, lquota=None, pquota=None, bquota=None):

    output = {}
    ldata = {}
    bdata = {}
    pdata = {}

    if lquota['data'] is not None:
      ldata = self._getkv(lquota['data'])

    if pquota['data'] is not None:
      pdata = self._getkv(pquota['data'])

    if bquota['data'] is not None:
      bdata = self._getkv(bquota['data'])

    print json.dumps(bdata, sort_keys=True, indent=2)
    print json.dumps(pdata, sort_keys=True, indent=2)
    print json.dumps(ldata, sort_keys=True, indent=2)

    output = bdata.copy()
    output.update(pdata)
    output.update(ldata)

    return (True, json.dumps(output))
