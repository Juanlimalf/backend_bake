from pydantic import BaseModel, Field
from typing import List


class Compras(BaseModel):
    cpf: str = Field(max_length=11, min_length=11, example="99999999999")
    loja: str = Field(max_length=2, example="99")
    coo: str = Field(max_length=6, example="123456")
    checkout: str = Field(max_length=3, example="999")
    valor: float = Field(example=999.99)
    user_inclusao: str = Field(example="nome.sobrenome")
