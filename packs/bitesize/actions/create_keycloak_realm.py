import requests
import json
from st2actions.runners.pythonrunner import Action


class CreateKeycloakRealm(Action):

    def run(self):

        environment = self.config.get('environment')
        domain = self.config.get('domain')
        base_url = "https://auth" + "." + environment + "." + domain + "/"
        token_endpoint_url = base_url + "auth/realms/master/protocol/openid-connect/token"
        realms_endpoint_url = base_url + "auth/admin/realms"
        keycloak_password = self.config.get('keycloak_password')

        response = requests.post(
            token_endpoint_url,
            timeout=5,
            verify=False,
            data={
                "username": "admin",
                "password": keycloak_password,
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
            timeout=5,
            verify=False,
            data=json.dumps(realm_data))

        if client.status_code not in [201, 409]:
            raise Exception('keycloak realm not created.')

        return True
