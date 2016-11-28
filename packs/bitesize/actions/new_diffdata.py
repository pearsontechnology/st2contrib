import json
from st2actions.runners.pythonrunner import Action

from string import split

class diffData(Action):

  def run(self, src, dst):

    output = []
    
    print json.dumps(src, sort_keys=True, indent=2)
    print json.dumps(dst, sort_keys=True, indent=2)

    dnames = []
    slist = []

    for dentry in dst:
      dnames.append(dentry['metadata']['name'])

    for sentry in src:
      name = sentry['metadata']['name']
      if name not in dnames:
        slist.append(sentry)

    return (True, slist)
