from connection.connection_confg import DBconnection
from repository import repository
from models.model_api import *
from log.logger import log
import requests
from fastapi.responses import JSONResponse

logger = log()


# Funcao assincrona para gerar jogadas
async def gera_jogadas(compra):
    try:
        # feito a requisição na API do "Meu Nagumo", caso o cliente, não tenha cadastro.
        url = "http://54.160.6.32:9002/login"
        body = {
            "id": compra.cpf
        }
        requests.post(url=url, json=body)
        # Feito a conexão com o banco de dados.
        with DBconnection() as db:
            # Buscando o ID do cliente.
            id_client = repository.busca_id_cliente(cpf=compra.cpf, db=db.session)
            # Função para inserir a compra no banco
            id_compra = await repository.insere_compra(id_client=id_client, compra=compra, db=db.session)
            # Verificar se a compra gera jogada.
            if compra.gera_jogada == 0:
                pass
            else:
                # inserindo a jogada no banco.
                await repository.insere_jogada(id_client=id_client, id_compra=id_compra, db=db.session)
            db.session.commit()

    except Exception as e:
        print(e)
        logger.error(f"Erro ao gerar jogadas, cliente: {compra.cpf}, erro: {e}")
        db.session.rollback()


# Função para consultar jogadas e voucher
def jogadas_vouchers(cpf):
    try:
        # Iniciando as listas
        lista_jogadas = []
        lista_voucher = []
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # Buscando o ID do cliente.
            id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)
            # Consultando as jogadas disponiveis.
            jogadas = repository.consulta_jogadas(id_user=id_client, db=db.session)
            # Montando o arquivo de jogadas e inserindo na lista
            for jogada in jogadas:
                arq = {
                    "id_jogada": jogada.id_jogada,
                    "id_compra": jogada.id_compra,
                    "id_usuario": jogada.id_usuario,
                    "data_inclusao": str(jogada.data_inclusao)
                }
                lista_jogadas.append(arq)
            # Consultando os vouchers cliente.
            vouchers = repository.consulta_voucher(id_user=id_client, db=db.session)
            # Montando o arquivo de voucher e inserindo na lista
            for voucher in vouchers:
                prod = repository.consulta_produto(id_prod=voucher.id_produto, db=db.session)
                arq2 = {
                    "id_compra": voucher.id_compra,
                    "id_produto": voucher.id_produto,
                    "codigo_acesso": prod.cod_acesso,
                    "descricao_produto": prod.descricao_produto,
                    "data_inclusao": str(voucher.data_inclusao),
                    "data_vencimento": str(voucher.data_vencimento),
                    "utilizado": voucher.utilizado,
                    "data_atualizacao": str(voucher.data_atualizacao),
                    "codigo_voucher": str(voucher.codigo_voucher)
                }
                lista_voucher.append(arq2)
        # Montando o json
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


# Função para consumir as jogadas
def consumir_jogada(cpf: str):
    try:
        # Iniciando as listas
        lista_jogadas = []
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # Buscando o ID do cliente.
            id_client = repository.busca_id_cliente(cpf=cpf, db=db.session)
            # Validando se o cliente existe no banco, caso contrario retorna vazio
            if id_client == False:
                return ListaJogadas(quant_jogada=0, jogadas=[])
            # Consumindo a jogada cliente
            com_jogadas = repository.consumir_jogada(id_user=id_client, db=db.session)
            # Validando se jogada existe
            if com_jogadas == False:
                return ListaJogadas(quant_jogada=0, jogadas=[])
            else:
                # Montando o arquivo de jogadas e inserindo na lista
                for jogada in com_jogadas[0]:
                    arq = {
                        "id_jogada": jogada.id_jogada,
                        "id_compra": jogada.id_compra,
                        "id_usuario": jogada.id_usuario,
                        "data_inclusao": str(jogada.data_inclusao)
                    }
                    lista_jogadas.append(arq)
            # Sortendo um produto para essa jogada.
            produto = repository.random_produtos(db=db.session)
            # Montando o json
            jogadas = {
                "produto_sorteado": {
                    "plu": produto.plu,
                    "cod_acesso": produto.cod_acesso,
                    "descricao_produto": produto.descricao_produto,
                    "categoria": produto.categoria,
                    "tipo": produto.tipo
                },
                "quant_jogada": len(com_jogadas[0]),
                "jogadas": lista_jogadas
            }
            # Gerando voucher para o cliente.
            repository.gera_voucher(jogada=com_jogadas[1], produto=produto, db=db.session)
            db.session.commit()
            return jogadas
    except Exception as e:
        print(e)
        logger.error(f"Erro ao buscar informações, cliente: {cpf}, erro: {e}")
        db.session.rollback()
        return False


# Funcão para consultar a disponibilidade do voucher
def consultar_voucher(voucher: str):
    try:
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # Consultar o voucher
            dados_voucher = repository.cons_voucher_uni(voucher=voucher, db=db.session)
            # Validando se o voucher existe
            if dados_voucher == False:
                return dados_voucher
            # Buscando os dados do produto
            dados_produto = repository.consulta_produto(id_prod=dados_voucher.id_produto, db=db.session)
            # Montando os arquivo json
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


# Função para consumir o voucher
def consumir_voucher(dados):
    try:
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # enviando o voucher para ser consumido
            use_voucher = repository.consumir_voucher(dados, db.session)
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
