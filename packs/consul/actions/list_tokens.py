from lib import action

class ConsulAclListAction(action.ConsulBaseAction):
    def run(self):

        acl_list = self.consul.acl.list()
        return acl_list
