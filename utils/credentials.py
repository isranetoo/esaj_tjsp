
import os
import json

CUR_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(CUR_DIR, "static")
CREDENTIALS_DIR = os.path.join(STATIC_DIR, "credentials")


def get_escavador_token() -> str:
    with open(os.path.join(CREDENTIALS_DIR, "escavador.cred"), 'r') as file:
        esc_cred = json.load(file)
    return esc_cred["TOKEN"]


def get_twocapthca_token() -> str:
    with open(os.path.join(CREDENTIALS_DIR, "twocaptcha.cred"), 'r') as file:
        twocaptcha_cred = json.load(file)
    return twocaptcha_cred["API_KEY"]


def get_serasa_login() -> tuple[str, str]:
    with open(os.path.join(CREDENTIALS_DIR, "serasa.cred"), 'r') as file:
        serasa_cred = json.load(file)
    return serasa_cred["username"], serasa_cred["password"]


def get_serasa_clientid() -> str:
    with open(os.path.join(CREDENTIALS_DIR, "serasa.cred"), 'r') as file:
        serasa_cred = json.load(file)
    return serasa_cred["client_id"]


def get_assertiva_login() -> str:
    with open(os.path.join(CREDENTIALS_DIR, "assertiva.cred"), 'r') as file:
        assertiva_cred = json.load(file)
    return assertiva_cred
