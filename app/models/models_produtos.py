from pydantic import BaseModel, Field


class Produto(BaseModel):
    plu: str = Field(example=123123)
    cod_acesso: str = Field(example=1231231231231)
    descricao_produto: str = Field(example="descrição Produto")
    categoria: str = Field(example="Categoria do produto")
    tipo: str = Field(example="P")


class ProdutoVoucher(BaseModel):
    id_client: int
    produto: Produto
