import requests
import re
import json
import uuid
import boto3
from urlparse import urljoin
from st2actions.runners.pythonrunner import Action

class NfsSpec(Action):

    def run(self, payload, config, customer, volsize):

        try:
            self.region = self.config.get('region')
            parameters_config = self.config['nfs']
            stack_name = stack_name_or_id = payload['name'] + "-" + payload['namespace']
            template_file = self.config.get('template_path') + 'nfs.template'
            environment = self.config['environment']

            template_body = open(template_file, 'r').read()

            parameters = []

            for item in parameters_config:
                if item in payload['labels']:
                    parameters.append([item, payload['labels'][item]])
                else:
                    parameters.append([item, parameters_config[item]])

            print json.dumps(parameters, sort_keys=True, indent=2)

            print type(parameters)

            vpcid = parameters_config['VpcId']

            vpcdata = self._get_vpc(vpcid)
            parameters.append(['Environment', environment])
            parameters.append(['Customer', customer])
            parameters.append(['NFSVolSize', volsize])

        except:
            self.logger.exception(
                'Cannot create valid name for Cloudformation Stack!')
            raise

        #print json.dumps(parameters, sort_keys=True, indent=2)

        newpayload = {
            'stack_name': stack_name,
            'stack_name_or_id': stack_name,
            'template_body': template_body,
            'parameters': parameters,
            'vpcid': vpcid
        }

        print json.dumps(newpayload, sort_keys=True, indent=2)

        return newpayload

    def _get_vpc(self, vpcid):
        ec2 = boto3.client('ec2', region_name=self.region)

        vpcdata = {}
        vpcdata['subnets' ] = []
        vpcdata['cidrblock'] = ec2.describe_vpcs( VpcIds=[ vpcid ])['Vpcs'][0]['CidrBlock']

        response = ec2.describe_route_tables( Filters=[ { 'Name': 'vpc-id', 'Values': [ vpcid ] }, ])['RouteTables']

        for rt in response:
            tags = rt['Tags']
            backend = 0
            for tag in tags:
                if 'backend' in tag['Value']:
                  backend = 1

            if backend == 0:
                continue

            for assoc in rt['Associations']:
                vpcdata['subnets'].append(assoc['SubnetId'])

        return vpcdata
