from pydantic import BaseModel, Field
from typing import List


class Mensage(BaseModel):
    mensage: str = Field(default="Success")


class Compras(BaseModel):
    loja: str = Field(max_length=2, default="99")
    coo: str = Field(max_length=6, default="123456")
    checkout: str = Field(max_length=3, default="999")
    cpf: str = Field(max_length=11, default="99999999999")
    gera_jogada: bool = Field(default=0)


class Jogadas(BaseModel):
    id_jogada: int = Field(default=1)
    id_compra: int = Field(default=1)
    id_usuario: int = Field(default=1)
    data_inclusao: str = Field(default="2000-01-01T00:00:00")
    data_utilizacao: str = Field(default="2000-01-01T00:00:00")
    utilizado: bool = Field(default=False)


class ProdutoSorteado(BaseModel):
    plu: str = Field(default=123123)
    cod_acesso: str = Field(default=1231231231231)
    descricao_produto: str = Field(default="descrição Produto")
    categoria:str = Field(default="Categoria do produto")


class Voucher(BaseModel):
    id_voucher: int = Field(default=1)
    id_compra: int = Field(default=1)
    id_produto: int = Field(default=1)
    id_usuario: int = Field(default=1)
    id_jogada: int = Field(default=1)
    data_inclusao: str = Field(default="2000-01-01T00:00:00")
    data_vencimento: str = Field(default="2000-01-01T00:00:00")
    cupom_utilizado: str = Field(max_length=6, default="123456")
    utilizado: bool = Field(default=0)
    data_utilizado: str = Field(default="2000-01-01T00:00:00")


class ListaJogadas(BaseModel):
    quant_jogada: int = Field(default=0)
    jogadas: List[Jogadas]
    vouchers: List[Voucher]


class JogadasConsumidas(BaseModel):
    produto_sorteado: List[ProdutoSorteado]
    quant_jogada: int = Field(default=0)
    jogadas: List[Jogadas]
