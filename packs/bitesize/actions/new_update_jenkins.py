import os
import json
import jinja2
import string

from st2actions.runners.pythonrunner import Action

class UpdateJenkins(Action):

  def _passgen(self):
    length = 16
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    password = ''
    for i in range(length):
      password += chars[ord(os.urandom(1)) % len(chars)]
    return password

  def update_vars(self, srcfile):

    with open(srcfile, 'r') as jsonfile:
      mydict = json.load(jsonfile)

    try:
      mydict['metadata']['namespace'] = self.allvars['namespace']
    except KeyError:
      pass

    try: 
      mydict['spec']['rules'][0]['host'] = self.allvars['jenkins_host']
    except KeyError:
      pass

    if 'template' in mydict['spec']:
      if 'spec' in mydict['spec']['template']:
        if 'containers' in mydict['spec']['template']['spec']:
          mydict['spec']['template']['spec']['containers'][0]['image'] = self.allvars['jenkins_version']
          for env in mydict['spec']['template']['spec']['containers'][0]['env']:
            #print env
            if env['name'] == u'JENKINS_ADMIN_USER':
              env['value'] = self.allvars['jenkins_admin_user']
 
            if env['name'] == u'JENKINS_ADMIN_PASSWORD':
              env['value'] = self.allvars['jenkins_admin_password']
 
            if env['name'] == u'SEED_JOBS_REPO':
              env['value'] = self.allvars['seed_jobs_repo']
 
            if env['name'] == u'GIT_PRIVATE_KEY':
              env['value'] = self.allvars['git_private_key']

    return mydict

  def run(self, namespace, templatedir, private_key, jenkins_host, jenkins_admin, jenkins_version, gitrepo):

    self.allvars = {}
    output = {}

    with open(private_key, 'r') as keyfile:
        data = keyfile.read()

    self.allvars['namespace'] = namespace
    self.allvars['jenkins_admin_user'] = jenkins_admin
    self.allvars['jenkins_host'] = jenkins_host
    self.allvars['jenkins_version'] = "bitesize-registry.default.svc.cluster.local:5000/geribatai/jenkins:" + jenkins_version
    self.allvars['seed_jobs_repo'] = gitrepo
    self.allvars['jenkins_admin_password'] = self._passgen()
    self.allvars['git_private_key'] = data

    for key, thefile in [('apt', 'apt-svc.json'), ('jnk', 'jenkins-svc.json'), ('ing', 'ingress.json'), ('dep', 'deployment.json')]:
      thefile = templatedir + "/" + thefile
      output[key] = self.update_vars(thefile)

    #print json.dumps(output, sort_keys=True, indent=2)
    return output
