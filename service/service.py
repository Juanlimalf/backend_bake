from connection.connection_confg import DBconnection
from repository import repository
from models.model_api import *
from log.logger import log
import requests
from fastapi.responses import JSONResponse


logger = log()


async def gera_jogadas(compra):
    try:
        url = "http://54.160.6.32:9002/login"
        body = {
            "id": compra.cpf
        }
        requests.post(url=url, json=body)

        with DBconnection() as db:
            id_client = repository.busca_id_cliente(cpf=compra.cpf, db=db.session)

            id_compra = await repository.insere_compra(id_client=id_client, compra=compra, db=db.session)
            if compra.gera_jogada == 0:
                pass
            else:
                await repository.insere_jogada(id_client=id_client, id_compra=id_compra, db=db.session)
            db.session.commit()

    except Exception as e:
        print(e)
        logger.error(f"Erro ao gerar jogadas, cliente: {compra.cpf}, erro: {e}")
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
                    "checkout_utilizado": str(voucher.checkout_utilizado),
                    "utilizado": voucher.utilizado,
                    "data_atualizacao": str(voucher.data_atualizacao),
                    "codigo_voucher": str(voucher.codigo_voucher)
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
        logger.error(f"Erro ao buscar informações, cliente: {cpf}, erro: {e}")
        return False


def consumir_jogada(cpf: str):
    try:
        lista_jogadas = []
        with DBconnection() as db:
            id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)
            if id_client == False:
                return ListaJogadas(quant_jogada=0, jogadas=[])

            com_jogada = repository.consumir_jogada(id_user=id_client, db=db.session)

            if com_jogada == False:
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
                "produto_sorteado": {
                    "plu": produto.plu,
                    "cod_acesso": produto.cod_acesso,
                    "descricao_produto": produto.descricao_produto,
                    "categoria": produto.categoria
                },
                "quant_jogada": len(com_jogada[0]),
                "jogadas": lista_jogadas
            }

            repository.gera_voucher(jogada=com_jogada[1], produto=produto, db=db.session)
            db.session.commit()
            return jogadas
    except Exception as e:
        print(e)
        logger.error(f"Erro ao buscar informações, cliente: {cpf}, erro: {e}")
        db.session.rollback()
        return False


def consultar_voucher(voucher: str):
    try:
        with DBconnection() as db:

            dados_voucher = repository.cons_voucher_uni(voucher=voucher, db=db.session)

            if dados_voucher == False:
                return dados_voucher

            dados_produto = repository.consulta_produto(id_prod=dados_voucher.id_produto, db=db.session)

            produto = Produto(
                plu=dados_produto.plu,
                cod_acesso=dados_produto.cod_acesso,
                descricao_produto=dados_produto.descricao_produto,
                categoria=dados_produto.categoria,
                tipo=dados_produto.tipo
            )
            arquivo = ProdutoVoucher(
                id_client=int(dados_voucher.id_usuario),
                produto=produto
            )
            return arquivo

    except Exception as e:
        print(e)
        logger.error(f"Erro ao buscar informações, voucher: {voucher}, erro: {e}")
        return False


def consumir_voucher(dados):
    try:
        with DBconnection() as db:

            use_voucher = repository.consumir_voucher(dados, db.session)

            if use_voucher == False:
                response = {"message": "Voucher ja foi utilizado"}
                return JSONResponse(response, status_code=400)
            else:
                db.session.commit()
                response = {"message": "Voucher utilizado com sucesso"}
                return JSONResponse(response, status_code=200)
    except Exception as e:
        print(e)
        logger.error(f"Erro ao consumir voucher, voucher: {dados.voucher}, erro: {e}")
        db.session.rollback()
        response = {"message": "Não foi possivel utilizar o voucher"}
        return JSONResponse(response, status_code=400)
