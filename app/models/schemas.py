from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta


Base = declarative_base()


def data_validade():
    validade = datetime.today() + timedelta(days=30)
    return validade


class BakeJogadas(Base):
    __tablename__ = "bake_jogadas"

    id_jogada = Column(Integer, primary_key=True, autoincrement=True)
    id_compra = Column(ForeignKey("bake_compras.id_compra"), nullable=False)
    id_usuario = Column(Integer, nullable=False)
    data_inclusao = Column(DateTime, server_default=func.now())
    data_utilizacao = Column(DateTime, onupdate=func.now())
    utilizado = Column(Boolean)

    def __repr__(self):
        return f"{self.id_jogada}, {self.id_compra}, {self.id_usuario}, {self.data_inclusao}, " \
               f"{self.data_utilizacao}, {self.utilizado}"


class BakeProdutos(Base):
    __tablename__ = "bake_produtos"

    id_produto = Column(Integer, primary_key=True, autoincrement=True)
    plu = Column(String(6))
    cod_acesso = Column(String(20))
    descricao_produto = Column(String(50))
    categoria = Column(String(15))
    ativo = Column(Boolean)
    tipo = Column(String(1))

    def __repr__(self):
        return f"""{self.id_produto}, {self.plu}, {self.cod_acesso}, {self.descricao_produto}, 
                    {self.categoria}, {self.ativo}, {self.tipo}"""


class BakeVoucher(Base):
    __tablename__ = "bake_vouchers"

    id_voucher = Column(Integer, primary_key=True, autoincrement=True)
    id_compra = Column(ForeignKey("bake_compras.id_compra"), nullable=False)
    id_produto = Column(ForeignKey("bake_produtos.id_produto"), nullable=False)
    id_usuario = Column(Integer, nullable=False)
    id_jogada = Column(ForeignKey("bake_jogadas.id_jogada"), nullable=False)
    data_inclusao = Column(DateTime, server_default=func.now())
    data_vencimento = Column(DateTime, default=data_validade)
    ativo = Column(Boolean, default=0)
    data_ativacao = Column(DateTime)
    utilizado = Column(Boolean, default=0)
    data_atualizacao = Column(DateTime, onupdate=func.now())
    codigo_voucher = Column(String(16))
    valor = Column(Float)

    def __repr__(self):
        return f"""{self.id_voucher}, {self.id_compra}, {self.id_produto}, {self.id_usuario}, {self.id_jogada}, 
                    {self.data_inclusao}, {self.data_vencimento}, {self.ativo}, {self.data_ativacao}, 
                    {self.utilizado}, {self.data_atualizacao}, {self.codigo_voucher}, {self.valor}"""


class BakeCompras(Base):
    __tablename__ = "bake_compras"

    id_compra = Column(Integer, primary_key=True, autoincrement=True)
    loja = Column(String(2))
    coo = Column(String(6))
    checkout = Column(String(3))
    valor = Column(Float)
    data_inclusao = Column(DateTime, server_default=func.now())
    id_usuario = Column(Integer, nullable=False)
    gera_jogada = Column(Boolean)
    usuario_inclusao = Column(String(50))

    def __repr__(self):
        return f"""{self.id_compra}, {self.loja}, {self.coo}, {self.checkout}, 
            {str(self.data_inclusao)}, {self.id_usuario}, {self.gera_jogada}, {self.usuario_inclusao}"""
