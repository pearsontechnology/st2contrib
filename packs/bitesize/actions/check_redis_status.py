from st2actions.runners.pythonrunner import Action


class CheckRedisStatus(Action):

    def run(self, name, data):

        rgs = data['ReplicationGroups']

        for rg in rgs:
            rgid = rg['ReplicationGroupId']
            if rgid == name:
                return (False, "matched")

        return True
