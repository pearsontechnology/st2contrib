from st2actions.runners.pythonrunner import Action

from string import split

class getConfig(Action):

  def run(self):

    return self.config
