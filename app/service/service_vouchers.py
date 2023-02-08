from app.connection.connection_confg import DBconnection
from app.repository import repository
from app.models.models_produtos import *
from app.models.models_jogadas import *
from app.models.models_vouches import *
from app.log.logger import log
from fastapi.responses import JSONResponse
from app.routes.router_request import consulta_produto_c5


logger = log()


# Funcão para consultar a disponibilidade do voucher
def consultar_voucher(loja: str, data: str):
    try:
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # Consultar o voucher
            dados_voucher = repository.get_vouchers(loja=loja, data=data, db=db)

            return dados_voucher

    except Exception as e:
        print(e)
        logger.error(f"Erro ao buscar informações, erro: {e}")
        return False


def ativar_voucher(cod_voucher):
    try:
        with DBconnection() as db:

            # Verificando se o codigo do voucher esta correto.
            voucher = repository.cons_voucher_uni(voucher=cod_voucher, db=db.session)

            if voucher == []:
                response = {"message": "Voucher não foi encontrado"}
                return JSONResponse(response, status_code=400)

            # Verificando se o voucher ja foi ativado
            if voucher[0].ativo == True:
                response = {"message": "Voucher ja foi ativado"}
                return JSONResponse(response, status_code=400)

            id_prod = voucher[0].id_produto

            # buscando os dados do produto pelo id
            produto = repository.consulta_produto(id_prod=id_prod, db=db.session)
            cod_plu = produto[0].plu
            descricao_prod = produto[0].descricao_produto
            prod_consinco = consulta_produto_c5(cod_plu).json()
            valor_prod = prod_consinco["itens"][0]["valorC5"]

            response = repository.ativar_voucher(voucher=cod_voucher, valor=valor_prod, db=db.session)

            voucher = Voucher(
                id_compra=response.id_compra,
                id_produto=response.id_produto,
                codigo_acesso=cod_plu,
                descricao_produto=descricao_prod,
                data_inclusao=str(response.data_inclusao),
                data_vencimento=str(response.data_vencimento),
                ativo=response.ativo,
                utilizado=response.utilizado,
                data_atualizacao=str(response.data_atualizacao),
                codigo_voucher=response.codigo_voucher,
                valor=response.valor
            )
            db.session.commit()

            return voucher

    except Exception as e:
        print(e)
        logger.error(f"Erro ao ativar voucher, voucher: {cod_voucher}, erro: {e}")
        db.session.rollback()
        response = {"message": "Não foi possivel ativar o voucher, tente novamente"}
        return JSONResponse(response, status_code=400)


# Função para consumir o voucher
def consumir_voucher(voucher):
    try:
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # enviando o voucher para ser consumido
            use_voucher = repository.consumir_voucher(voucher, db.session)
            # Verificando se o voucher é valido
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
