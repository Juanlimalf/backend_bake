from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi import status
from typing import List

from app.models import User, UserReturn, Message, Compras, VoucherResponse, ListaJogadasVoucher,\
    JogadasConsumidas, GeraJogada, Voucher, Produto, Aceite
from app.service import service_vouchers, service_jogadas, service_compras
from app.routes_api import router_request
from app.service.security import decode_jwt


router_bakeshop = APIRouter()

security = HTTPBearer()


def validar_token(token: str = Depends(security)):

    validatoken = decode_jwt(token.credentials)
    if not validatoken:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Token invalido ou expirado, faça o login novamente.")


@router_bakeshop.get("/", tags=["Docs"], include_in_schema=False)
async def docs():

    return RedirectResponse(url="/docs")


@router_bakeshop.post("/login", status_code=status.HTTP_200_OK, tags=["Login"],
                      description="Endpoint para login e geração de token",
                      response_model=UserReturn, response_description="Resposta Padrão")
def login(user: User):
    response_token = router_request.requestLoginAd(user=user.user, password=user.password)
    if not response_token:
        raise HTTPException(status_code=401, detail="Usuario ou senha invalido")
    return response_token


# Endpoint para gerar as jogadas, PDV vai gerar para todas as compras acima de R$50
@router_bakeshop.post("/jogadas/gerar", status_code=status.HTTP_200_OK, tags=["Admin"],
                      description="Gerar jogadas para o cliente",
                      response_model=Message, response_description="Resposta Padrão")
async def gerar_jogadas(compra: Compras, token: str = Depends(validar_token)):
    jogada = service_jogadas.gera_jogadas(compra)

    return jogada


# Endpoint para consultar a disponibilidade do voucher antes da utilização do mesmo.
@router_bakeshop.get("/voucher/{loja}/{data}", status_code=status.HTTP_200_OK, tags=["Admin"],
                     description="Consultar o vouchers ativados na data",
                     response_description="Resposta Padrão", response_model=List[VoucherResponse])
def consultar_voucher(data: str, loja: str, token: str = Depends(validar_token)):

    response = service_vouchers.consultar_voucher(loja=loja, data=data)

    # if response == []:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, 
    #         detail="Não existe vouchers utilizados no periodo informado.")

    return response


# Endpoint para desativar o voucher caso o cliente não tenha utilizado o mesmo.
@router_bakeshop.put("/voucher/{cod_voucher}/desativar", status_code=status.HTTP_200_OK, tags=["Admin"],
                     description="Desativar o voucher")
def desativar_voucher(cod_voucher: str, token: str = Depends(validar_token)):
    response = service_vouchers.desativar_voucher(cod_voucher)

    return response


@router_bakeshop.get("/compras/{cpf}", status_code=status.HTTP_200_OK, tags=["Admin"],
                     description="Consultar todas as Compras registradas ref ao CPF",
                     response_model=List[Compras], response_description="Resposta Padrão")
def consulta_compras_cpf(cpf: str, token: str = Depends(validar_token)):

    response = service_compras.consulta_compras_cliente(cpf)

    return response


@router_bakeshop.get("/Compras/{loja}/{data}", status_code=status.HTTP_200_OK, tags=["Admin"], description="Consultar todas as Compras registradas")
def consulta_compras(data: str, loja: str, token: str = Depends(validar_token)):
    response = service_compras.consulta_compras(data, loja)

    return response


# O Game irar consumir esse endpoint e disponibilizar para o usuario
@router_bakeshop.get("/jogadas/{cpf}", status_code=status.HTTP_200_OK, tags=["GAME"], description="Consultar as jogadas e vouchers do ref ao CPF", 
                     response_model=ListaJogadasVoucher, response_description="Resposta Padrão")
def jogadas(cpf: str,):

    jogadas = service_jogadas.jogadas_vouchers(cpf=cpf)
    if jogadas == False:
        response = {"message": "Não foi possivel localizar as jogadas"}
        return JSONResponse(response, status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return jogadas


# Endpoint para consumir a jogada disponivel e gerar um voucher para o CPF
@router_bakeshop.put("/jogadas", status_code=status.HTTP_200_OK, tags=["GAME"], description="Consumir as jogada e gerar voucher", 
                     response_model=JogadasConsumidas, response_description="Resposta Padrão")
def utilizar_jogadas(jogada: GeraJogada):

    response = service_jogadas.consumir_jogada(jogada)

    if response == False:
        response = {"message": "Não foi possivel localizar as jogadas"}
        return JSONResponse(response, status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return response


@router_bakeshop.put("/voucher/{cod_voucher}/ativar", status_code=status.HTTP_200_OK, tags=["GAME"], description="Ativação de voucher para uso", 
                     response_model=Voucher, response_description="Resposta Padrão")
def ativar_voucher(cod_voucher):

    response = service_vouchers.ativar_voucher(cod_voucher)

    return response


# Endpoint para consumir o voucher, pdv ira enviar os dados do cupom que o consumiu o voucher
@router_bakeshop.put("/voucher/{cod_voucher}/utilizar", status_code=status.HTTP_200_OK, tags=["GAME"], description="Consumir o voucher do cliente", 
                     response_model=Message, response_description="Resposta Padrão")
def utilizar_voucher(cod_voucher):

    response = service_vouchers.consumir_voucher(cod_voucher)

    return response


@router_bakeshop.get("/produtos", status_code=status.HTTP_200_OK, tags=["GAME"], description="Busca todos os produtos ativos para a roleta", 
                     response_model=List[Produto], response_description="Resposta Padrão")
def get_produtos():
    produtos = service_compras.busca_produtos()

    return produtos


@router_bakeshop.post("/aceitetermos", status_code=status.HTTP_200_OK, tags=["GAME"], description="Aceite de termos game")
def termos(aceite: Aceite):

    response = service_jogadas.aceite_termos(aceite)

    return response


@router_bakeshop.get("/create_db", status_code=status.HTTP_200_OK, tags=["Admin"], description="Criar o banco de dados", include_in_schema=False)
def create_db():
    try:
        from app.connection.connection_confg import DBconnection
        db = DBconnection()
        db.create_tables()
        return {"message": "Banco de dados criado com sucesso"}
    except Exception as e:
        return {"message": "Erro ao criar o banco de dados", "error": e}
