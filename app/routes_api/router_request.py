import requests
from app.models import UserReturn
from app.service.security import encode_jwt


users_admin = [
    {
        "nome": "Juan Lima",
        "usuario_ad": "juan.costa",
        "role_client": 2,
        "password": "JUan2837",
        "loja": "51"
    }, {
        "nome": "Leonardo",
        "usuario_ad": "leonardo.abe",
        "role_client": 2,
        "password": "senhas123",
        "loja": "51"
    }, {
        "nome": "Marcelo",
        "usuario_ad": "marcelo.thome",
        "role_client": 2,
        "password": "senhas123",
        "loja": "51"
    }, {
        "nome": "Franklin",
        "usuario_ad": "franklin.campos",
        "role_client": 1,
        "password": "senhas123",
        "loja": "51"
    }, {
        "nome": "Vania",
        "usuario_ad": "vania.felipe",
        "role_client": 2,
        "password": "123456",
        "loja": "51"
    }, {
        "nome": "Balcao",
        "usuario_ad": "balcao.loja51",
        "role_client": 1,
        "password": "123456",
        "loja": "51"
    }, {
        "nome": "Vitrine Loja 51",
        "usuario_ad": "Vitrine.loja51",
        "role_client": 1,
        "password": "123456",
        "loja": "51"
    }, {
        "nome": "Vitrine Loja 15",
        "usuario_ad": "Vitrine.loja15",
        "role_client": 1,
        "password": "123456",
        "loja": "15"
    }
]


def valida_cpf(cpf):
    url = "http://54.160.6.32:9002/login"

    body = {
        "id": cpf
    }
    requests.post(url=url, json=body)


def requestLoginAd(user: str, password: str):

    url = "https://apigc.nagumo.com.br/api/v1/login"

    body = {
        "username_ad": user,
        "password_ad": password
    }

    retorno = requests.post(url, body)
    token = encode_jwt()

    if retorno.status_code != 200:
        for u in users_admin:
            if u["usuario_ad"].lower() == user.lower() and u["password"] == password:

                response = UserReturn(
                    nome=u["nome"],
                    usuario_ad=u["usuario_ad"],
                    role_client=u["role_client"],
                    access_token=token,
                    loja=u["loja"]
                )

                return response
            else:
                False
    else:
        nome = retorno.json()["data"]["user"]["name"]
        user_ad = retorno.json()["data"]["user"]["username_ad"]

        for u in users_admin:
            if u["usuario_ad"].lower() == user.lower():
                role_client = 2
                break
            else:
                role_client = 1

        response = UserReturn(
            nome=nome,
            usuario_ad=user_ad,
            role_client=role_client,
            access_token=token,
            loja="601"
        )

        return response


def consulta_produto_c5(plu):
    token = {
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvIjoiZGVzZW52b2x2aW1lbnRvVGkiLCJzZW5oYSI6InRlbGV2ZW5kYXMifQ.daDE-VRKV4y_1pqDxDLdSu3474b_J1sDBkwigWbTv8Q",
    }
    url = f"https://endpointtelevendas.mixteratacadista.com.br/pedido/item/51/0/{plu}"

    response = requests.get(url, headers=token)

    return response
