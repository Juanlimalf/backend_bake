from app.connection import DBconnection
from app import repository
from app.models import *
from app.log.logger import log

logger = log()


def consulta_compras_cliente(cpf: str):
    try:
        lista_compra = []
        with DBconnection() as db:
            # Pega o id do cliente
            id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)

            compras = repository.consultaCompras(id_client=id_client, db=db.session)

            for compra in compras:
                arq = {
                    "cpf": cpf,
                    "loja": compra.loja,
                    "coo": compra.coo,
                    "checkout": compra.checkout,
                    "valor": compra.valor,
                    "user_inclusao": compra.usuario_inclusao
                }

                lista_compra.append(arq)                
        response = lista_compra

        return response

    except Exception as e:
        print(f"Erro ao buscar informações de compras, CPF: {cpf} erro: {e}")
        logger.error(f"Erro ao buscar informações de compras, CPF: {cpf} erro: {e}")


def consulta_compras(data: str, loja: str):
    try:
        lista_compra = []
        with DBconnection() as db:
            compras = repository.get_compras(data=data, loja=loja, db=db.session)

            for compra in compras:
                arq = {
                    "loja": compra.loja,
                    "coo": compra.coo,
                    "checkout": compra.checkout,
                    "valor": compra.valor,
                    "user_inclusao": compra.usuario_inclusao
                }

                lista_compra.append(arq)
        response = {
            "compras": lista_compra
        }
        return response

    except Exception as e:
        print(f"Erro ao buscar informações de compras, erro: {e}")
        logger.error(f"Erro ao buscar informações de compras erro: {e}")


def busca_produtos():
    lista_produtos = []
    with DBconnection() as db:

        produtos = repository.consulta_produto_full(db=db.session)

        for produto in produtos:
            arq = {
                "plu": produto.plu,
                "cod_acesso": produto.cod_acesso,
                "descricao_produto": produto.descricao_produto,
                "categoria": produto.categoria,
                "tipo": produto.tipo
            }
            lista_produtos.append(arq)

        return lista_produtos
