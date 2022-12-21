from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.model_api import *
from service import service

# Configurando o FAST-API
metadata = [{
    "name": "API - Roleta Bakeshop",
    "description": "Backend game roleta bakeshop "
}]


app = FastAPI(title="Roleta Bakeshop",
              description="API - Roleta Bakeshop",
              version="0.0.1",
              openapi_tags=metadata
              )

origins = [
    "*",
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/jogadas/gerar", status_code=200, tags=["PDV"], description="Gerar jogadas para o cliente",
          response_model=Message, response_description="Resposta Padrão")
async def gerar_jogadas(compras : Compras, background_task: BackgroundTasks):

    background_task.add_task(service.gera_jogadas, compras)

    if compras.gera_jogada != True:
        response = Message(message="Não foi gerado jogada para essa compra, valor abaixo de R$50")
        return response
    else:
        response = Message(message="Compra acima de R$50, jogada gerada com sucesso!")
        return response


@app.get("/voucher/consultar/{voucher}", status_code=200, tags=["PDV"], description="Consultar o voucher do cliente",
         response_model=ProdutoVoucher, response_description="Resposta Padrão")
def consultar_voucher(voucher: str):

    response = service.consultar_voucher(voucher=voucher)

    if response == False:
        response = {"message": "Voucher não localizado ou ja utilizado"}
        return JSONResponse(response, status_code=401)
    else:
        return response


@app.put("/voucher/utilizar", status_code=200, tags=["PDV"], description="Consumir o voucher do cliente",
         response_model= Message,response_description="Resposta Padrão")
def utilizar_voucher(dados_voucher: UtilizarVoucher):

    response = service.consumir_voucher(dados_voucher)

    return response


@app.get("/jogadas/{cpf}", status_code=200, tags=["GAME"], description="Consultar as jogadas e vouchers do ref ao CPF",
         response_model=ListaJogadasVoucher, response_description="Resposta Padrão")
def jogadas(cpf: str):

    jogadas = service.jogadas_vouchers(cpf=cpf)
    if jogadas == False:
        response = {"message": "Não foi possivel localizar as jogadas"}
        return JSONResponse(response, status_code=401)
    else:
        return jogadas


@app.put("/jogadas/{cpf}", status_code=200, tags=["GAME"], description="Consumir as jogada e gerar voucher",
         response_model=JogadasConsumidas, response_description="Resposta Padrão")
def utilizar_jogadas(cpf: str):

    response = service.consumir_jogada(cpf=cpf)

    if response == False:
        response = {"message": "Não foi possivel localizar as jogadas"}
        return JSONResponse(response, status_code=401)
    else:
        return response
