from pydantic import BaseModel, Field
from typing import List, Optional


class Message(BaseModel):
    message: str = Field(example="Success")


class Compras(BaseModel):
    loja: str = Field(max_length=2, example="99")
    coo: str = Field(max_length=6, example="123456")
    checkout: str = Field(max_length=3, example="999")
    cpf: str = Field(max_length=11, example="99999999999")
    gera_jogada: bool = Field(example=0)


class Jogadas(BaseModel):
    id_jogada: int = Field(example=1)
    id_compra: int = Field(example=1)
    id_usuario: int = Field(example=1)
    data_inclusao: str = Field(example="2000-01-01T00:00:00")
    data_utilizacao: str = Field(example="2000-01-01T00:00:00")
    utilizado: bool = Field(example=False)


class Produto(BaseModel):
    plu: str = Field(example=123123)
    cod_acesso: str = Field(example=1231231231231)
    descricao_produto: str = Field(example="descrição Produto")
    categoria: str = Field(example="Categoria do produto")


class Voucher(BaseModel):
    id_voucher: int = Field(example=1)
    id_compra: int = Field(example=1)
    id_produto: int = Field(example=1)
    id_usuario: int = Field(example=1)
    id_jogada: int = Field(example=1)
    data_inclusao: str = Field(example="2000-01-01T00:00:00")
    data_vencimento: str = Field(example="2000-01-01T00:00:00")
    cupom_utilizado: str = Field(max_length=6, example="123456")
    checkout_utilizado: str = Field(max_length=4, example="123", default="123")
    utilizado: bool = Field(example=0)
    data_atualizacao: str = Field(example="2000-01-01T00:00:00")
    codigo_voucher: str = Field(example="1234567891234567")


class ListaJogadas(BaseModel):
    quant_jogada: int = Field(example=0)
    jogadas: List[Jogadas]


class JogadasConsumidas(BaseModel):
    produto_sorteado: Optional[Produto]
    quant_jogada: int = Field(example=0)
    jogadas: List[Jogadas]


class ListaJogadasVoucher(BaseModel):
    quant_jogada: int = Field(example=0)
    jogadas: List[Jogadas]
    vouchers: List[Voucher]


class UtilizarVoucher(BaseModel):
    voucher: int = Field(example=1231231231231231)
    coo: str = Field(example="123456")
    checkout: str = Field(example="123")
    utilizado: bool = Field(example=1)


class ProdutoVoucher(BaseModel):
    id_client: int
    produto: Produto

