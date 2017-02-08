import json
from st2actions.runners.pythonrunner import Action

from string import split

class LayerTerraformConfig(Action):

  def run(self, config, outfile):

    with open(outfile, 'w') as thefile:
      for k in config:
        thefile.write("%s = \"%s\"\n" % (k, config[k]))
      thefile.close()

    return True
