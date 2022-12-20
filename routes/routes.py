from fastapi import FastAPI, BackgroundTasks
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


@app.post("/jogadas/gerar", status_code=200, tags=["PDV"],
          description="Gerar jogadas cliente", response_model=Mensage)
async def gerar_jogadas(compras : Compras, background_task: BackgroundTasks):

    background_task.add_task(service.gera_jogadas, compras)

    response = Mensage(mensage="jogada gerada com sucesso")

    return response


@app.get("/voucher/{voucher}")
def consultar_voucher(voucher: int):

    return


@app.put("/voucher/consumir", status_code=200, tags=["PDV"], description="Consumir o voucher do cliente")
def utilizar_voucher():
    pass


@app.get("/jogadas/{cpf}", status_code=200, tags=["GAME"], description="Busca jogadas e vouchers",
         response_model=ListaJogadas, response_description="Response")
def jogadas(cpf: str) -> dict:

    jogadas = service.jogadas_vouchers(cpf=cpf)

    return jogadas


@app.put("/jogadas/{cpf}", status_code=200, tags=["GAME"], description="Consumo de jogadas e geração de voucher")
def utilizar_jogadas(cpf: str):

    response = service.consumir_jogada(cpf=cpf)

    return response
