from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.models.models_user import *
from app.models.models_produtos import *
from app.models.models_jogadas import *
from app.models.models_vouches import *
from app.models.models_compras import *
from app.service import service_vouchers, service_jogadas, service_compras
from app.routes import router_request
from app.service.security import decode_jwt


# Configurando o FAST-API
metadata = [{
    "name": "API - Roleta Bakeshop",
    "description": "Backend game roleta bakeshop "
}]

app = FastAPI(title="Roleta Bakeshop",
              description="API - Roleta Bakeshop",
              version="1.0.0",
              openapi_tags=metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


security = HTTPBearer()


def validar_token(token: str = Depends(security)):

    validatoken = decode_jwt(token.credentials)
    if not validatoken:
        raise HTTPException(status_code=400, detail="Token invalido ou expirado, faça o login novamente.")


@app.post("/login", status_code=200, tags=["Login"], description="Endpoint para login e geração de token",
          response_model=UserReturn, response_description="Resposta Padrão")
def login(user: User):
    response_token = router_request.requestLoginAd(user=user.user, password=user.password)
    if not response_token:
        raise HTTPException(status_code=401, detail="Usuario ou senha invalido")
    return response_token


# Endpoint para gerar as jogadas, PDV vai gerar para todas as compras acima de R$50
@app.post("/jogadas/gerar", status_code=200, tags=["Admin"], description="Gerar jogadas para o cliente",
          response_model=Message, response_description="Resposta Padrão")
async def gerar_jogadas(compra: Compras, token: str = Depends(validar_token)):

    jogada = service_jogadas.gera_jogadas(compra)

    return jogada


# Endpoint para consultar a disponibilidade do voucher antes da utilização do mesmo.
@app.get("/voucher/{loja}/{data}", status_code=200, tags=["Admin"], description="Consultar o voucher do cliente",
         response_description="Resposta Padrão")
def consultar_voucher(loja: str, data: str, token: str = Depends(validar_token)):

    response = service_vouchers.consultar_voucher(loja=loja, data=data)

    if response == []:
        raise HTTPException(status_code=400, detail="Não existe vouchers utilizados no periodo informado.")

    return response


@app.get("/compras/{cpf}", status_code=200, tags=["Admin"],
         description="Consultar todas as Compras registradas ref ao CPF",
         response_model=ListaCompras, response_description="Resposta Padrão")
def consulta_compras(cpf: str, token: str = Depends(validar_token)):

    response = service_compras.consulta_compras_cliente(cpf)

    return response


@app.get("/compras/{cpf}/{id}", status_code=200, tags=["Admin"], description="Consultar as Compra pelo ID",
         response_model=Compras, response_description="Resposta Padrão")
def consulta_compra(cpf: str, id: int, token: str = Depends(validar_token)):

    response = service_compras.consulta_compra(cpf, id)

    return response


# Endpoint para consultar as jogadas disponives e os vouchers ref ao CPF
# O Game irar consumir esse endpoint e disponibilizar para o usuario
@app.get("/jogadas/{cpf}", status_code=200, tags=["GAME"], description="Consultar as jogadas e vouchers do ref ao CPF",
         response_model=ListaJogadasVoucher, response_description="Resposta Padrão")
def jogadas(cpf: str,):

    jogadas = service_jogadas.jogadas_vouchers(cpf=cpf)
    if jogadas == False:
        response = {"message": "Não foi possivel localizar as jogadas"}
        return JSONResponse(response, status_code=401)
    else:
        return jogadas


# Endpoint para consumir a jogada disponivel e gerar um voucher para o CPF
@app.put("/jogadas", status_code=200, tags=["GAME"], description="Consumir as jogada e gerar voucher",
         response_model=JogadasConsumidas, response_description="Resposta Padrão")
def utilizar_jogadas(jogada: GeraJogada ):

    response = service_jogadas.consumir_jogada(jogada)

    if response == False:
        response = {"message": "Não foi possivel localizar as jogadas"}
        return JSONResponse(response, status_code=401)
    else:
        return response


@app.put("/voucher/{cod_voucher}/ativar", status_code=200, tags=["GAME"], description="Ativação de voucher para uso",
         response_model=Voucher, response_description="Resposta Padrão")
def ativar_voucher(cod_voucher):

    response = service_vouchers.ativar_voucher(cod_voucher)

    return response


# Endpoint para consumir o voucher, pdv ira enviar os dados do cupom que o consumiu o voucher
@app.put("/voucher/{cod_voucher}/utilizar", status_code=200, tags=["GAME"], description="Consumir o voucher do cliente",
         response_model=Message, response_description="Resposta Padrão")
def utilizar_voucher(cod_voucher):

    response = service_vouchers.consumir_voucher(cod_voucher)

    return response
