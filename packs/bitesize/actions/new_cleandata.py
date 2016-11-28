from st2actions.runners.pythonrunner import Action

from string import split

class getConfig(Action):

  def run(self, data):

    output = []

    if "items" in data['data']:
      for item in data['data']['items']:
        if "type" in item:
          if item['type'] == "kubernetes.io/service-account-token":
            continue
        if "status" in item:
          del item['status']
        if "metadata" in item:
          if "uid" in item['metadata']:
            del item['metadata']['uid']
          if "selfLink" in item['metadata']:
            del item['metadata']['selfLink']
          if "resourceVersion" in item['metadata']:
            del item['metadata']['resourceVersion']
          if "creationTimestamp" in item['metadata']:
            del item['metadata']['creationTimestamp']
          if "generation" in item['metadata']:
            del item['metadata']['generation']
          if "deletionGracePeriodSeconds" in item['metadata']:
            del item['metadata']['deletionGracePeriodSeconds']
          if "deletionTimestamp" in item['metadata']:
            del item['metadata']['deletionTimestamp']
          #if "annotations" in item['metadata']:
          #  del item['metadata']['annotations']
          #if "generateName" in item['metadata']:
          #  del item['metadata']['generateName']
          #if "namespace" in item['metadata']:
          #  del item['metadata']['namespace']
          #if "ownerReferences" in item['metadata']:
          #  del item['metadata']['ownerReferences']
          if "finalizers" in item['metadata']:
            del item['metadata']['finalizers']
          # if "labels" in item['metadata']:
          #  del item['metadata']['labels']
        if "spec" in item:
          if "finalizers" in item['spec']:
            del item['spec']['finalizers']
          if "template" in item['spec']:
            if "spec" in item['spec']['template']:
              if "generation" in item['spec']['template']['spec']:
                del item['spec']['template']['spec']['generation']
              if "dnsPolicy" in item['spec']['template']['spec']:
                del item['spec']['template']['spec']['dnsPolicy']
              if "terminationGracePeriodSeconds" in item['spec']['template']['spec']:
                del item['spec']['template']['spec']['terminationGracePeriodSeconds']
              if "restartPolicy" in item['spec']['template']['spec']:
                del item['spec']['template']['spec']['restartPolicy']
          if "clusterIP" in item['spec']:
            del item['spec']['clusterIP']
          if "strategy" in item['spec']:
            if "rollingUpdate" in item['spec']['strategy']:
              if 'maxSurge' in item['spec']['strategy']['rollingUpdate']:
                del item['spec']['strategy']['rollingUpdate']['maxSurge']
              if 'maxUnavailable' in item['spec']['strategy']['rollingUpdate']:
                del item['spec']['strategy']['rollingUpdate']['maxUnavailable']

        output.append(item)
    else:
      output.append(data)

    return output
