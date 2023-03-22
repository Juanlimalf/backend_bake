import requests
from app.models.models_user import *
from app.service.security import encode_jwt


users_admin = ["juan.costa", "leonardo.abe", "marcelo.thome"]


def valida_cpf(cpf):
    url = "http://54.160.6.32:9002/login"

    body = {
        "id": cpf
    }
    retorno = requests.post(url=url, json=body)


def requestLoginAd(user:str, password:str):

    url = "https://apigc.nagumo.com.br/api/v1/login"

    body = {
        "username_ad": user,
        "password_ad": password
    }

    retorno = requests.post(url, body)

    if retorno.status_code != 200:
        return False
    else:

        nome = retorno.json()["data"]["user"]["name"]
        user_ad = retorno.json()["data"]["user"]["username_ad"]
        token = encode_jwt()

        response = UserReturn(
            nome=nome,
            usuario_ad=user_ad,
            role_client=1 if user_ad not in users_admin else 2,
            access_token=token
        )

    return response


def consulta_produto_c5(plu):
    token = {
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvIjoiZGVzZW52b2x2aW1lbnRvVGkiLCJzZW5oYSI6InRlbGV2ZW5kYXMifQ.daDE-VRKV4y_1pqDxDLdSu3474b_J1sDBkwigWbTv8Q",
    }
    url = f"https://endpointtelevendas.mixteratacadista.com.br/pedido/item/51/0/{plu}"

    response = requests.get(url, headers=token)

    return response