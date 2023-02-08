from app.connection.connection_confg import DBconnection
from app.repository import repository
from app.models.models_user import *
from app.models.models_jogadas import *
from app.log.logger import log
from fastapi.responses import JSONResponse
from app.routes.router_request import valida_cpf


logger = log()


# Funcao para gerar jogadas
def gera_jogadas(compra):
    try:
        # feito a requisição na API do "Meu Nagumo", caso o cliente, não tenha cadastro.
        valida_cpf(compra.cpf)

        # Feito a conexão com o banco de dados.
        with DBconnection() as db:

            verifica_compra = repository.verifica_Compra(compra=compra, db=db.session)

            if verifica_compra == False:

                # Buscando o ID do cliente.
                id_client = repository.busca_id_cliente(cpf=compra.cpf, db=db.session)

                # Validando se a compra ira gerar jogada.
                if compra.valor >= 50:
                    gera_jog = 1
                else:
                    gera_jog = 0

                # Função para inserir a compra no banco
                id_compra = repository.insere_compra(id_client=id_client, gera_jogada=bool(gera_jog),
                                                     compra=compra, db=db.session)

                if gera_jog == 0:
                    db.session.commit()
                    response = Message(message="Valor abaixo de R$50, Não foi gerado jogada para essa compra.")
                    return response
                else:
                    # inserindo a jogada no banco.
                    repository.insere_jogada(id_client=id_client, id_compra=id_compra, db=db.session)
                    db.session.commit()

                    response = Message(message="Jogada gerada, valor acima de R$50.")
                    return response
            else:
                response = {
                    "message": 'Ja foi gerado jogada para a compra informada.'
                }
                return JSONResponse(response, status_code=401)

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
                    "data_inclusao": str(jogada.data_inclusao),
                    "utilizado": jogada.utilizado
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
                    "codigo_acesso": prod[0].cod_acesso,
                    "descricao_produto": prod[0].descricao_produto,
                    "data_inclusao": str(voucher.data_inclusao),
                    "data_vencimento": str(voucher.data_vencimento),
                    "ativo": voucher.ativo,
                    "utilizado": voucher.utilizado,
                    "data_atualizacao": str(voucher.data_atualizacao),
                    "codigo_voucher": str(voucher.codigo_voucher),
                    "valor": voucher.valor
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
def consumir_jogada(jogada):
    try:
        print(jogada.cpf, jogada.categoria)

        # Iniciando as listas
        lista_jogadas = []
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # Buscando o ID do cliente.
            id_client = repository.busca_id_cliente(cpf=jogada.cpf, db=db.session)
            # Validando se o cliente existe no banco, caso contrario retorna vazio
            if id_client == False:
                return ListaJogadas(quant_jogada=0, jogadas=[])
            # Consumindo a jogada cliente
            cons_jogadas = repository.consumir_jogada(id_user=id_client, db=db.session)

            # Validando se jogada existe
            if cons_jogadas == False:
                return ListaJogadas(quant_jogada=0, jogadas=[])

            else:
                # Montando o arquivo de jogadas e inserindo na lista
                for jog in cons_jogadas[0]:
                    arq = {
                        "id_jogada": jog.id_jogada,
                        "id_compra": jog.id_compra,
                        "id_usuario": jog.id_usuario,
                        "data_inclusao": str(jog.data_inclusao),
                        "utilizado": jog.utilizado
                    }
                    lista_jogadas.append(arq)

            # Sortendo um produto para essa jogada.
            produto = repository.random_produtos(categoria=jogada.categoria, db=db.session)

            # Montando o json
            jogadas = {
                "produto_sorteado": {
                    "plu": produto.plu,
                    "cod_acesso": produto.cod_acesso,
                    "descricao_produto": produto.descricao_produto,
                    "categoria": produto.categoria,
                    "tipo": produto.tipo
                },
                "quant_jogada": len(cons_jogadas[0]),
                "jogadas": lista_jogadas
            }

            # Gerando voucher para o cliente.
            repository.gera_voucher(jogada=cons_jogadas[1], produto=produto, db=db.session)
            db.session.commit()
            return jogadas
    except Exception as e:
        print(e)
        logger.error(f"Erro ao buscar informações, cliente: {jogada.cpf}, erro: {e}")
        db.session.rollback()
        return False