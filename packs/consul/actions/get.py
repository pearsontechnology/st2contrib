from lib import action


class ConsulGetAction(action.ConsulBaseAction):
    def run(self, key, recurse=None):
        list, value = self.consul.kv.get(key, recurse=recurse)
        return value
