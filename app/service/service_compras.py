from app.connection.connection_confg import DBconnection
from app.repository import repository
from app.models.models_compras import *
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
                    "cpf":cpf,
                    "loja":compra.loja,
                    "coo":compra.coo,
                    "checkout":compra.checkout,
                    "valor":compra.valor,
                    "user_inclusao":compra.usuario_inclusao
                }

                lista_compra.append(arq)
        response = {
            "compras": lista_compra
        }
        return response

    except Exception as e:
        print(f"Erro ao buscar informações de compras, CPF: {cpf} erro: {e}")
        logger.error(f"Erro ao buscar informações de compras, CPF: {cpf} erro: {e}")


def consulta_compra(cpf, id_compra):
    with DBconnection() as db:

        id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)

        compra = repository.consulta_compra(id_client=id_client, id_compra=id_compra, db=db.session)

        response = Compras(
            cpf=cpf,
            loja=compra[0].loja,
            coo=compra[0].coo,
            checkout=compra[0].checkout,
            valor=compra[0].valor,
            user_inclusao=compra[0].usuario_inclusao
        )

    return response
