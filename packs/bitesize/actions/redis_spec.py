import re
import json
import uuid

from st2actions.runners.pythonrunner import Action


class RedisSpec(Action):
    def run(self, payload):

        print json.dumps(payload, sort_keys=True, indent=2)
        # take the payload name and replace any non-alphanumerical characters with "-"
        # to create a name for the database
        try:
            db_name = re.sub('["-.]+', '', payload['name'])
        except:
            self.logger.exception('Cannot create valid name for database!')
            raise

        return {"name": db_name, "namespace": payload['namespace'], "action": payload['resource']}
