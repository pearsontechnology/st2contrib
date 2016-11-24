import os
import json

from st2actions.runners.pythonrunner import Action

from string import split

class ParseNSList(Action):

  def _getkv(self, entries):
    data = {}
    for entry in entries:
      if entry['Value'] is not None:
        key = split(entry['Key'], '/')[-1]
        data[key] = entry['Value']

    return data

  def run(self, nslist):

    output = []

    allns = nslist['data']

    for entry in allns:
      last = split(entry['Key'], '/')[-1]
      if last == "unapproved":
        ns = entry['Key'].split('/')[2]
        output.append(ns)

    return (True, output)
