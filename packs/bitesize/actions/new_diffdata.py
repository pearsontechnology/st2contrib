import json
from st2actions.runners.pythonrunner import Action

from string import split

class diffData(Action):

  def run(self, src, dst):
  # only copy items that don't exist in dst already

    output = []
    
    dnames = []
    slist = []

    for dentry in dst:
      dnames.append(dentry['metadata']['name'])

    for sentry in src:
      name = sentry['metadata']['name']
      if name not in dnames:
        slist.append(sentry)

    return (True, slist)
