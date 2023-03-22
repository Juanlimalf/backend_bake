from pydantic import BaseModel, Field
from typing import List, Union, Optional
from .models_jogadas import Jogadas


class Voucher(BaseModel):
    id_compra: int = Field(example=1)
    id_produto: int = Field(example=1)
    codigo_acesso: str = Field(example="123456")
    descricao_produto: str = Field(example="Descrição produto voucher")
    data_inclusao: str = Field(example="2000-01-01 00:00:00")
    data_vencimento: str = Field(example="2000-01-01 00:00:00")
    ativo: bool = Field(example=0)
    data_ativacao: str = Field(example="2000-01-01 00:00:00")
    utilizado: bool = Field(example=0)
    data_atualizacao: str = Field(example="2000-01-01 00:00:00")
    codigo_voucher: str = Field(example="1234567891234567")
    valor: Union[float, None] = Field(example=999.99, default=None)


class ListaJogadasVoucher(BaseModel):
    quant_jogada: int = Field(example=0)
    vouchers: List[Voucher]
    aceite_termos: Optional[bool] = Field(example=0)


class UtilizarVoucher(BaseModel):
    voucher: int = Field(example=1231231231231231)
    coo: str = Field(example="123456")
    checkout: str = Field(example="123")
    utilizado: bool = Field(example=1)


class VoucherResponse(BaseModel):
    loja: str = Field(example="01")
    id_voucher: int = Field(example=123)
    codigo_voucher: str = Field(example="0123456789101213")
    descricao_produto: str = Field(example="Descrição produto voucher")
    valor: float = Field(example=999.99)
    data_inclusao: str = Field(example="2000-01-01 00:00:00")
    ativo: bool = Field(example=True)
