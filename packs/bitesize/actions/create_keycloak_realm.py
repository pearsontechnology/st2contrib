import requests
import json
from st2actions.runners.pythonrunner import Action


class CreateKeycloakRealm(Action):

    def run(self):

        environment = self.config.get('environment')
        domain = self.config.get('domain')
        base_url = "http://auth" + "." + environment + "." + domain + "/"
        token_endpoint_url = base_url + "auth/realms/master/protocol/openid-connect/token"
        realms_endpoint_url = base_url + "auth/admin/realms"

        response = requests.post(
            token_endpoint_url,
            data={
                "username": "admin",
                "password": "test",
                "grant_type": "password",
                "client_id": "admin-cli"})
        json_response = json.loads(response.text)

        access_token = json_response["access_token"]

        bearer_token = "Bearer " + access_token

        headers = {
            "Authorization": bearer_token,
            "Content-Type": "application/json"}

        with open('/opt/keycloak_bitesize_realm.json') as json_data:
            realm_data = json.load(json_data)

        client = requests.post(
            realms_endpoint_url,
            headers=headers,
            data=json.dumps(realm_data))

        if client.status_code in [201, 409]:
            print "whoopee! all done"
        else:
            print " we got a prblem :( "
