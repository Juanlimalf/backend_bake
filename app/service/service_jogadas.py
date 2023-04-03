from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import status

from app.connection.connection_confg import DBconnection
from app.repository import repository
from app.models import ListaJogadas, Message, GeraJogada, JogadasConsumidas, Voucher, Produto, Aceite
from app.routes_api.router_request import valida_cpf
from app.log.logger import log


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
                return JSONResponse(response, status_code=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        print(e)
        logger.error(f"Erro ao gerar jogadas, cliente: {compra.cpf}, erro: {e}")
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao gerar jogadas, por gentileza entrar em contato com o suporte")


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
                    "data_ativacao": str(voucher.data_ativacao),
                    "utilizado": voucher.utilizado,
                    "data_atualizacao": str(voucher.data_atualizacao),
                    "codigo_voucher": str(voucher.codigo_voucher),
                    "valor": voucher.valor
                }
                lista_voucher.append(arq2)
            
            aceite_client = repository.consulta_aceite(id_cliente=id_client, db=db.session)

        # Montando o json
        arquivo = {
            "quant_jogada": len(jogadas),
            "vouchers": lista_voucher,
            "aceite_termos": aceite_client
        }
        return arquivo
    except Exception as e:
        print(e)
        logger.error(f"Erro ao buscar informações, cliente: {cpf}, erro: {e}")
        return False


# Função para consumir as jogadas
def consumir_jogada(jogada):
    try:
        # Iniciando as listas
        lista_jogadas = []
        # Abrindo a conexão com o Banco
        with DBconnection() as db:
            # Buscando o ID do cliente.
            id_client = repository.busca_id_cliente(cpf=jogada.cpf, db=db.session)
            # Validando se o cliente existe no banco, caso contrario retorna vazio
            if id_client == False:
                return ListaJogadas(quant_jogada=0)
            # Consumindo a jogada cliente
            cons_jogadas = repository.consumir_jogada(id_user=id_client, db=db.session)
            # Validando se jogada existe
            if cons_jogadas == False:
                return ListaJogadas(quant_jogada=0)

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
                "quant_jogada": len(cons_jogadas[0])
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
    

def aceite_termos(aceite):
    try:
        # Abrindo a conexão com o Banco
    
        with DBconnection() as db:
            # Buscando o ID do cliente.
            id_client = repository.busca_id_cliente(cpf=aceite.cpf, db=db.session)
            # Inserindo o aceite do cliente
            resp = repository.aceite_termos(id_cliente=id_client, db=db.session)

            if resp == False:
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "usuário já aceitou os termos dessa campanha"})
            else:
                db.session.commit()

                response = Message(message="Suscesso ao aceitar os termos.")
                return response
    except Exception as e:
        print(e)
        logger.error(f"Erro ao aceitar os termos. Erro: {e}")    
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao aceitar os termos. Por gentileza entrar em contato com o suporte")
