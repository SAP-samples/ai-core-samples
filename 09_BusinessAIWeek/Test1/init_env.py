import os
import json
import configparser

from hdbcli import dbapi

import variables

ROOT_PATH_DIR = os.path.dirname(os.getcwd())
AICORE_CONFIG_FILENAME = '.aicore-config.json'
USER_CONFIG_FILENAME = '.user.ini'

def set_environment_variables() -> None:
    with open(os.path.join(ROOT_PATH_DIR, AICORE_CONFIG_FILENAME), 'r') as config_file:
        config_data = json.load(config_file)

    os.environ["AICORE_AUTH_URL"]=config_data["url"]+"/oauth/token"
    os.environ["AICORE_CLIENT_ID"]=config_data["clientid"]
    os.environ["AICORE_CLIENT_SECRET"]=config_data["clientsecret"]
    os.environ["AICORE_BASE_URL"]=config_data["serviceurls"]["AI_API_URL"]

    os.environ["AICORE_RESOURCE_GROUP"]=variables.RESOURCE_GROUP

def connect_to_hana_db() -> dbapi.Connection:
    config = configparser.ConfigParser()
    config.read(os.path.join(ROOT_PATH_DIR, USER_CONFIG_FILENAME))
    return dbapi.connect(
        address=config.get('hana', 'url'),
        port=config.get('hana', 'port'),
        user=config.get('hana', 'user'),
        password=config.get('hana', 'passwd'),
        autocommit=True,
        sslValidateCertificate=False
    )