from pydantic import BaseModel, Field
from typing import List, Optional
from .models_produtos import Produto


class Jogadas(BaseModel):
    id_jogada: int = Field(example=1)
    id_compra: int = Field(example=1)
    id_usuario: int = Field(example=1)
    data_inclusao: str = Field(example="2000-01-01T00:00:00")
    utilizado: bool = Field(example=False)


class ListaJogadas(BaseModel):
    quant_jogada: int = Field(example=0)
    jogadas: List[Jogadas]


class JogadasConsumidas(BaseModel):
    produto_sorteado: Optional[Produto]
    quant_jogada: int = Field(example=0)
    jogadas: List[Jogadas]


class GeraJogada(BaseModel):
    cpf: str = Field(max_length=11, min_length=11, example="99999999999")
    categoria: str = Field(example="CATEGORIA")