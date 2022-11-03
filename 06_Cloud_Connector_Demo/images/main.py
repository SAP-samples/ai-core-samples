import requests
import os


def get_jwt_token(settings):
    granttype = 'client_credentials'
    token_response = requests.get(url=settings['token_service_url'], params={'grant_type': granttype},
                                  auth=(settings['clientid'], settings['clientsecret']))
    if token_response.status_code != 200:
        print(token_response.status_code, token_response.text)
        exit(-1)
    jwt = token_response.json()['access_token']
    return jwt


def test_http(host, port, path, token, proxyHostname):
    r = requests.get(f"http://{host}:{port}{path}",
                     headers={'SAP-CP-Connectivity-Service-Token': token},
                     proxies={'http': proxyHostname})
    return r


if __name__ == '__main__':
    jwt_settings = {
        "clientid": os.getenv("CP_CLIENT_ID", "Not set"),
        "clientsecret": os.getenv("CP_CLIENT_SECRET", "Not set"),
        "token_service_url": os.getenv("CP_TOKEN_SERVICE_URL", "Not set")
    }
    host = os.getenv("SERVICE_HOST", "virtual-simple-service-vafbahqycpb.eastus.azurecontainer.io")
    port = os.getenv("SERVICE_PORT", 5050)
    proxyHostname = os.getenv("CONNECTIVITY_PROXY_HOST", "http://connectivity-proxy.connectivity-proxy.svc.cluster.local:20003")

    try:
        print(f"Attempting to establish connection for client {jwt_settings['clientid']}")
        print("### Testing Connection ###")
        req = test_http(host, port, "/aicore", get_jwt_token(jwt_settings), proxyHostname)
        print("Connection Established")
        print(f"Request was processed with status code {req.status_code}")
        print(f"The response received was: {req.content}")
    except Exception as e:
        print(e)
        assert False
