from st2actions.runners.pythonrunner import Action

class Testtprs3(Action):

    def run(
            self,
            payload):

        tprName = payload['name']
        bucket = payload['labels']['bucket']
        with open('/tmp/test-tpr-s3', 'w') as f:
                f.write(tprName)
        output_dict = {"tprName": tprName, "bucket": bucket }
        return (True, output_dict)
