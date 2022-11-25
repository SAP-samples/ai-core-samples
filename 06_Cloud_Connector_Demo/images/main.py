import requests
import os


def get_jwt_token(settings):
    granttype = 'client_credentials'
    token_service_url= settings['token_service_url'][:-1]
    client_id = settings['clientid'][:-1]
    client_secret = settings['clientsecret']
    token_response = requests.get(url=token_service_url, params={'grant_type': granttype},
                                  auth=(client_id, client_secret))
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
    host = os.getenv("SERVICE_HOST", "virtual-service-exposed-by-cloud-connector") #to be replaced by cloud connector hostname
    port = os.getenv("SERVICE_PORT", 5050) #to be replaced by cloud connector port
    proxyHostname = os.getenv("CONNECTIVITY_PROXY_HOST", "http://connectivity-proxy.connectivity-proxy.svc.cluster.local:20003") #to be replaced by connectivity proxy hostname

    try:
        print(f"Attempting to establish connection for client {jwt_settings['clientid']}")
        print("### Testing Connection ###")
        req = test_http(host, port, "/aicore", get_jwt_token(jwt_settings), proxyHostname)
        print("Connection Established")
    except Exception as e:
        print(e)
        assert False
