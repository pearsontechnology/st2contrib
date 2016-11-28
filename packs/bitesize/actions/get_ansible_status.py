from st2actions.runners.pythonrunner import Action
from collections import defaultdict
from subprocess import Popen, PIPE
import sys
import json
import boto3

class GetAnsibleStatus(Action):
    def run(self, stack_name_or_id):
        region = self.config['region']
        environment = self.config['environment']

        ec2 = boto3.resource('ec2', region_name=region)
        cfclient = boto3.client('cloudformation', region_name=region)

        stack_states = ['CREATE_COMPLETE']

        status = cfclient.describe_stacks(StackName=stack_name_or_id)['Stacks'][0]['StackStatus']
        if status in stack_states:
            instanceID = cfclient.describe_stacks(StackName=stack_name_or_id)['Stacks'][0]['Outputs'][0]['OutputValue']
            instance = ec2.Instance(id=instanceID)
            private_ip_address = instance.private_ip_address

            writeHostCmd = "echo \"Host {0}\n\tStrictHostKeyChecking no\n\" >> ~/.ssh/config".format(private_ip_address)
            stdout,stderr,errorCode = self.run_command(writeHostCmd)
            if(errorCode != 0):
                sys.stderr.write("Unable to verify ansible playbook execution. Failed to configure SSH")
                sys.exit(2)

            command = "rm -f ~/.ssh/known_hosts"
            stdout,stderr,errorCode = self.run_command(command)
            if(errorCode != 0):
                sys.stderr.write("Unable to verify ansible playbook execution. Failed to clean up known hosts")
                sys.exit(2)

            command = "chown root:root  ~/.ssh/config"
            stdout,stderr,errorCode = self.run_command(command)
            if(errorCode != 0):
                sys.stderr.write("Unable to verify ansible playbook execution. Failed to set SSH config ownership")
                sys.exit(2)


            command = "ssh -i ~/.ssh/bitesize.key root@{0} 'cat /var/log/cloud-init-output.log | grep -o RECAP | wc -l'".format(private_ip_address)
            stdout,stderr,errorCode = self.run_command(command)
            if("2" not in stdout or errorCode != 0):
                sys.stderr.write("Ansible Playbook Execution still in progress on NFS instance")
                sys.exit(2)

            command = "ssh -i ~/.ssh/bitesize.key root@{0} 'cat /var/log/cloud-init-output.log | grep -A 2 RECAP | grep -o 'failed=[1-9][0-9]*''".format(private_ip_address)
            stdout,stderr,errorCode = self.run_command(command)
            if(errorCode == 0):
                sys.stderr.write("Failures reported during Ansible Playbook Execution on NFS instance")
                sys.exit(2)

            payload= {
                'private_ip_address': private_ip_address
            }

            print json.dumps(payload, sort_keys=True, indent=2)

            return payload

    def run_command(self, command):
        process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        errorCode = process.returncode
        #print("CMD= %s" % command)
        #print("Stdout= %s" % stdout)
        #print("Stderr= %s" % stderr)
        #print("Code= %s" % errorCode)
        return stdout,stderr,errorCode
