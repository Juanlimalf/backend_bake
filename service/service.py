from connection.connection_confg import DBconnection
from repository import repository
from models.model_api import *
import requests


async def gera_jogadas(compra):
    try:
        with DBconnection() as db:
            id_client = repository.busca_id_cliente(cpf=compra.cpf, db=db.session)
            if not id_client:
                # requests.get()
                while not id_client:
                    id_client = repository.busca_id_cliente(cpf=compra.cpf, db=db.session)

            id_compra = await repository.insere_compra(id_client=id_client, compra=compra, db=db.session)
            if compra.gera_jogada == 0:
                pass
            else:
                await repository.insere_jogada(id_client=id_client, id_compra=id_compra, db=db.session)
            db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()


def jogadas_vouchers(cpf):
    try:
        lista_jogadas = []
        lista_voucher = []
        with DBconnection() as db:

            id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)

            jogadas = repository.consulta_jogadas(id_user=id_client, db=db.session)
            for jogada in jogadas:
                arq = {
                    "id_jogada": jogada.id_jogada,
                    "id_compra": jogada.id_compra,
                    "id_usuario": jogada.id_usuario,
                    "data_inclusao": str(jogada.data_inclusao),
                    "data_utilizacao": str(jogada.data_utilizacao),
                    "utilizado": jogada.utilizado
                }
                lista_jogadas.append(arq)

            vouchers = repository.consulta_voucher(id_user=id_client, db=db.session)
            for voucher in vouchers:
                arq2 = {
                    "id_voucher": voucher.id_voucher,
                    "id_compra": voucher.id_compra,
                    "id_produto": voucher.id_produto,
                    "id_usuario": voucher.id_usuario,
                    "id_jogada": voucher.id_jogada,
                    "data_inclusao": str(voucher.data_inclusao),
                    "data_vencimento": str(voucher.data_vencimento),
                    "cupom_utilizado": str(voucher.cupom_utilizado),
                    "utilizado": voucher.utilizado,
                    "data_utilizado": str(voucher.data_utilizado)
                }
                lista_voucher.append(arq2)

        arquivo = {
            "quant_jogada": len(jogadas),
            "jogadas": lista_jogadas,
            "vouchers": lista_voucher
        }

        return arquivo
    except Exception as e:
        print(e)
        response = Mensage(message=f"Não foi possivel localizar as jogadas")
        return response


def consumir_jogada(cpf: str):
    try:
        lista_jogadas = []
        with DBconnection() as db:
            id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)
            com_jogada = repository.consumir_jogada(id_user=id_client, db=db.session)

            if com_jogada[0] == False:
                return ListaJogadas(quant_jogada=0, jogadas=[])
            else:
                for q in com_jogada[0]:
                    jogada = {
                        "id_jogada": q.id_jogada,
                        "id_compra": q.id_compra,
                        "id_usuario": q.id_usuario,
                        "data_inclusao": str(q.data_inclusao),
                        "data_utilizacao": str(q.data_utilizacao),
                        "utilizado": q.utilizado
                    }
                    lista_jogadas.append(jogada)

            produto = repository.random_produtos(db=db.session)

            jogadas = {
                "produto_sortedo": {
                    "plu": produto.plu,
                    "cod_acesso": produto.cod_acesso,
                    "descricao_produto": produto.descricao_produto,
                    "categoria": produto.categoria
                },
                "quant_jogada": len(com_jogada[0]),
                "jogadas": lista_jogadas
            }

            voucher = repository.gera_voucher(jogada=com_jogada[1], id_prod=produto.id_produto, db=db.session)

            db.session.commit()

            return jogadas
    except Exception as e:
        print(e)
        db.session.rollback()
        response = Mensage(message=f"Não foi possivel localizar as jogadas")
        return response
