import json
import importlib
from datetime import datetime
import time

from st2actions.runners.pythonrunner import Action


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


class K8sMigrateAction(Action):

    def run(
            self,
            ns_migration,
            src_k8s_url,
            src_k8s_password,
            dst_k8s_url,
            dst_k8s_password):

        self.k8s_src = (
            self._get_k8s_client(
                'k8sv1',
                'ApivApi',
                src_k8s_url,
                src_k8s_password),
            self._get_k8s_client(
                'k8sv1beta1',
                'ApisextensionsvbetaApi',
                src_k8s_url,
                src_k8s_password))
        self.k8s_dst = (
            self._get_k8s_client(
                'k8sv1',
                'ApivApi',
                dst_k8s_url,
                dst_k8s_password),
            self._get_k8s_client(
                'k8sv1beta1',
                'ApisextensionsvbetaApi',
                dst_k8s_url,
                dst_k8s_password))

        def get_post_compare(datatype, name, **kwargs):
            srcdata = self.get_data(self.k8s_src, datatype, ns=name)
            try:
                res = post(srcdata, datatype, ns=name)
            except Exception as e:
                print "Excepetion occurred when posting datatype '{0}' for namespace '{1}' to the destination K8S API. Reason: {2}".format(datatype,name,e.reason)
            dstdata = self.get_data(self.k8s_dst, datatype, ns=name)

            if srcdata and not dstdata:
                print ("--------- Entering Retry Logic ----------------")
                print "Re-querying desitination for datatype: '{0}'".format(datatype)
                time.sleep(5)  #Wait a brief moment and then query the destination again
                dstdata = self.get_data(self.k8s_dst, datatype, ns=name)
                if srcdata and not dstdata:  #Still not there, try a single repost
                    print "Retrying post to destination for datatype: '{0}'".format(datatype)
                    try:
                        res = post(srcdata, datatype, ns=name)
                    except Exception as e:
                        print "Excepetion occurred when posting datatype '{0}' for namespace '{1}' to the destination K8S API. Reason: {2}".format(datatype,name,e.reason)
                    time.sleep(10)  #Wait a brief moment and then query the destination one last time before failing workflow
                    dstdata = self.get_data(self.k8s_dst, datatype, ns=name)
                    if srcdata and not dstdata:
                        print "Datatype '{0}' for namespace '{1}' exists on src but was not successfully migrated to destination".format(datatype,name)
                        raise Exception("Source Data was not created on Destination ")

            #print ("Source Data:")
            #print json.dumps(srcdata, sort_keys=True, indent=2, default=json_serial)
            #print ("Destination Data:")
            #print json.dumps(dstdata, sort_keys=True, indent=2, default=json_serial)

        def post(data, datatype, **kwargs):

            """
            Copy data from one cluster to another

            :param object data: json object of data to be posted
            :param str datatype: the type of k8s object (required)
            :param str ns: k8s namespace (optional)

            """

            # namespaces don't need a namespace argument when they're created
            if datatype == "ns":
                kwargs = {}

            if datatype == "thirdparty":
                print json.dumps(data, sort_keys=True, indent=2, default=json_serial)
                # split third party resources and post per namespace
                for tpr in data:
                    print "++++"
                    print json.dumps(tpr, sort_keys=True, indent=2, default=json_serial)
                    print "++++"
                    if 'namespace' in tpr['metadata']:
                        kwargs['ns'] = tpr['metadata']['namespace']
                        if kwargs['ns'] in ['default', 'kube-system']:
                            print "not migrating 3pr system ns"
                            return
                        res = self.post_data(datatype, tpr, **kwargs)
                    else:
                        print "no namespace for %s - skipping" % tpr['metadata']['name']
            else:
                # post data to second cluster
                res = self.post_data(datatype, data, **kwargs)
            return res
            #print "RESP:"
            #print json.dumps(res, sort_keys=True, indent=2, default=json_serial)
        nsdata = self.k8s_src[0].list_namespace().to_dict()
        if ns_migration == "kube-system":
            print "Operating on Namespace: kube-system"
            get_post_compare("secret", ns_migration)
        else:
            for ns in nsdata['items']:
                name = ns['metadata']['name']
                if name in ['default', 'test-runner', 'kube-system']:
                    continue
                else:
                    print "Operating on Namespace: " + name
                    get_post_compare("ns", name)
                    get_post_compare("service", name)
                    get_post_compare("deployments", name)
                    get_post_compare("ds", name)
                    get_post_compare("rc", name)
                    get_post_compare("secret", name)
                    get_post_compare("ingress", name)
                    get_post_compare("limitrange", name)
                    get_post_compare("resquota", name)

    def get_data(self, target, datatype, **kwargs):
        """
        Given a datatype and optional namespace, requests data from a kubernetes cluster

        :param str datatype: type of k8s object
        :param str ns: namespace to insert data to (optional)
        :return: list of dicts with k8s data structures
        """

        myfunc = self._lookup_func(datatype, "list")

        # lookup which api the function lives in and set that to be the api
        # endpoint to use
        if(myfunc in dir(target[0])):
            myapi = target[0]
        if(myfunc in dir(target[1])):
            myapi = target[1]

        # third party resources don't need a namespace argument when they're queried,
        # but will when posted. best to strip it out here
        if datatype == "thirdparty":
            kwargs = {}

        # if a namespace is set, make the function call with it. return a dict
        if "ns" in kwargs:
            data = getattr(myapi, myfunc)(kwargs['ns']).to_dict()
        else:
            data = getattr(myapi, myfunc)().to_dict()

        output = []

        # print "^^^^^^^^^^^^^^^^^^^^"
        # print json.dumps(data, sort_keys=True, indent=2, default=json_serial)
        # print "^^^^^^^^^^^^^^^^^^^^"

        # a few calls return data with a slightly different structure
        # we ignore this to keep consistancy when reinserting
        if "items" not in data:
            tmp = {}
            tmp['items'] = []
            tmp['items'].append(data)
            data = tmp

        # delete objects that shouldn't be transferred between clusters
        if "items" in data:
            for item in data['items']:
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
                    if "annotations" in item['metadata']:
                        del item['metadata']['annotations']
                    if "generateName" in item['metadata']:
                        del item['metadata']['generateName']
                    if "namespace" in item['metadata']:
                        del item['metadata']['namespace']
                    if "ownerReferences" in item['metadata']:
                        del item['metadata']['ownerReferences']
                    if "finalizers" in item['metadata']:
                        del item['metadata']['finalizers']
                    # if "labels" in item['metadata']:
                    #  del item['metadata']['labels']
                if "spec" in item:
                    if "finalizers" in item['spec']:
                        del item['spec']['finalizers']
                    if "template" in item['spec']:
                        if "spec" in item['spec']['template']:
                            if "generation" in item[
                                    'spec']['template']['spec']:
                                del item['spec']['template'][
                                    'spec']['securityContext']
                            if "dnsPolicy" in item['spec']['template']['spec']:
                                del item['spec']['template'][
                                    'spec']['dnsPolicy']
                            if "terminationGracePeriodSeconds" in item[
                                    'spec']['template']['spec']:
                                del item['spec']['template']['spec'][
                                    'terminationGracePeriodSeconds']
                            if "restartPolicy" in item[
                                    'spec']['template']['spec']:
                                del item['spec']['template'][
                                    'spec']['restartPolicy']
                            if "containers" in item['spec']['template']['spec']:
                                for cont in item['spec']['template']['spec']['containers']:
                                    if cont['livenessProbe'] is not None:
                                        if "_exec" in cont['livenessProbe']:
                                            cont['livenessProbe']['exec'] = cont['livenessProbe'].pop('_exec')
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


    def _lookup_func(self, func, functype):
        """
        Given a k8s object, and an operation type, return the library function
        This will break if the library changes..

        :param str func: object type
        :param str functype: choice between list (read) or create
        :return: function name
        """

        funcmap = {"ns": {"list": "read_namespace",
                          "create": "create_namespace"},
                   "service": {"list": "list_namespaced_service",
                               "create": "create_namespaced_service"},
                   "pod": {"list": "list_namespaced_pod",
                           "create": "create_namespaced_pod"},
                   "rc": {"list": "list_namespaced_replication_controller",
                          "create": "create_namespaced_replication_controller"},
                   "secret": {"list": "list_namespaced_secret",
                              "delete": "delete_namespaced_secret",
                              "create": "create_namespaced_secret"},
                   "ingress": {"list": "list_namespaced_ingress_0",
                               "create": "create_namespaced_ingress"},
                   "thirdparty": {"list": "list_third_party_resource",
                                  "create": "create_namespaced_third_party_resource"},
                   "ds": {"list": "list_namespaced_daemon_set_0",
                          "create": "create_namespaced_daemon_set"},
                   "deployments": {"list": "list_namespaced_deployment_0",
                                   "create": "create_namespaced_deployment"},
                   "rs": {"list": "list_namespaced_replica_set",
                          "create": "create_namespaced_replica_set"},
                   "endpoint": {"list": "list_namespaced_endpoints_20",
                                "create": "create_namespaced_endpoints"},
                   "pv": {"list": "list_persistent_volume",
                          "create": "create_persistent_volume"},
                   "pvclaim": {"list": "list_namespaced_persistent_volume_claim",
                               "create": "create_namespaced_persistent_volume_claim"},
                   "jobs": {"list": "list_namespaced_job_5",
                            "create": "create_namespaced_job"},
                   "hpa": {"list": "list_namespaced_horizontal_pod_autoscaler_3",
                           "create": "create_namespaced_horizontal_pod_autoscaler"},
                   "networkpol": {"list": "list_namespaced_network_policy",
                                  "create": "create_namespaced_network_policy"},
                   "configmap": {"list": "list_namespaced_config_map_19",
                                 "create": "create_namespaced_config_map"},
                   "limitrange": {"list": "list_namespaced_limit_range_0",
                                  "create": "create_namespaced_limit_range"},
                   "podtemplate": {"list": "list_namespaced_pod_template",
                                   "create": "create_namespaced_pod_template"},
                   "resquota": {"list": "list_namespaced_resource_quota",
                                "create": "create_namespaced_resource_quota"}
                   }

        return funcmap[func][functype]

    def post_data(self, datatype, body, **kwargs):
        """
        Takes a datatype and structure, and posts it to the kubernetes cluster

        :param str datatype: type of k8s object
        :param str body: json structure
        :param str ns: namespace to insert data to (optional)
        :return: list of dicts with results for each input
        """
        if datatype == 'secret':
            mydeletefunc = self._lookup_func(datatype, "delete")

        myfunc = self._lookup_func(datatype, "create")

        # lookup which api the function lives in and set that to be the api
        # endpoint to use
        if(myfunc in dir(self.k8s_dst[0])):
            myapi = self.k8s_dst[0]
        if(myfunc in dir(self.k8s_dst[1])):
            myapi = self.k8s_dst[1]

        if "ns" in kwargs:
            print "Posting Datatype {0} to namespace:{1}".format(datatype,kwargs['ns'])
        else:
            print "Posting Datatype {0}".format(datatype)
        #print "body: "
        #print json.dumps(body, sort_keys=True, indent=2, default=json_serial)
        #print type(body)
        output = []

        for item in body:

            #print "++++++++++++++"
            #print json.dumps(item, sort_keys=True, indent=2, default=json_serial)
            #print "++++++++++++++"

            # if a namespace is set, make the function call with it. return a
            # dict
            if "ns" in kwargs:
                myns = kwargs['ns']
                if datatype == 'secret':
                    try:
                        getattr(myapi, mydeletefunc)(item, kwargs['ns'], item['metadata']['name']).to_dict()
                    except Exception:
                    continue
                data = getattr(myapi, myfunc)(item, kwargs['ns']).to_dict()
                if datatype == 'ns':
                    time.sleep(2)
            else:
                data = getattr(myapi, myfunc)(item).to_dict()

            output.append(data)
        return output

    def _get_k8s_client(self, api_version, api_library, url, password):

        api_version = importlib.import_module(api_version)
        api_library = getattr(api_version, api_library)
        api_version.Configuration().verify_ssl = False
        api_version.Configuration().username = 'admin'
        api_version.Configuration().password = password
        host = url

        apiclient = api_version.ApiClient(
            host,
            header_name="Authorization",
            header_value=api_version.configuration.get_basic_auth_token())
        apiclient.default_headers['Content-Type'] = 'application/json'

        client = api_library(apiclient)
        return client
