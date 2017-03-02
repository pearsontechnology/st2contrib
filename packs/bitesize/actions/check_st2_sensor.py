from __future__ import print_function
import subprocess
import json
from st2actions.runners.pythonrunner import Action


class CheckSt2Sensor(Action):

    def run(self):

        sensor_output = subprocess.check_output(
            ['st2', 'sensor', 'list', '--pack=kubernetes', '-a', 'ref', 'enabled', '-j'])
        sensor_output = json.loads(sensor_output)
        registered_sensors = [str(sensor.values()[0].split('.')[1])
                              for sensor in sensor_output]
        ps = subprocess.Popen(('ps', '-ef'), stdout=subprocess.PIPE)
        running_sensors = subprocess.check_output(
            ('grep', 'sensor_wrapper'), stdin=ps.stdout)
        ps.wait()
        sensor_result = [
            s for s in registered_sensors if s not in running_sensors]
        if not sensor_result:
            return (True, "success")
        return (True, ','.join(sensor_result) + ":" + "failed")
