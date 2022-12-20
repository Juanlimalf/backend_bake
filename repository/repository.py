from models.schemas import BakeProdutos, BakeVoucher, BakeCompras, Usuario, BakeJogadas
import random


def busca_id_cliente(cpf: str, db: object) -> int:
    query = db.query(Usuario.id_usuario).filter(Usuario.username == f'{cpf}').all()[0][0]
    return query


async def insere_compra(id_client: int, compra, db: object) -> int:
    compra = BakeCompras(
        loja=str(compra.loja),
        coo=str(compra.coo),
        checkout=str(compra.checkout),
        id_usuario=int(id_client),
        gera_jogada=bool(compra.gera_jogada)
    )
    db.add(compra)

    id_compra = db.query(BakeCompras.id_compra). \
        filter(BakeCompras.coo == compra.coo and
               BakeCompras.checkout == compra.checkout and
               BakeCompras.loja == compra.loja).order_by(BakeCompras.id_compra.desc()).first()[0]
    return id_compra


async def insere_jogada(id_compra: int, id_client: int, db: object):
    jogada = BakeJogadas(
        id_compra=id_compra,
        id_usuario=id_client,
        utilizado=0
    )
    db.add(jogada)


def consulta_jogadas(id_user: int, db: object) -> list:

    query = db.query(BakeJogadas).filter_by(id_usuario=id_user, utilizado=False).all()

    return query


def consulta_voucher(id_user: int, db: object) -> list:

    query = db.query(BakeVoucher).filter_by(id_usuario=id_user).order_by(BakeVoucher.utilizado.asc()).all()

    return query


def consumir_jogada(id_user: int, db: object):

    jogada = db.query(BakeJogadas).filter_by(id_usuario=id_user, utilizado=False).\
        order_by(BakeJogadas.id_compra.asc()).first()
    if jogada == None:
        return False
    else:
        jogada.utilizado = 1
        query = db.query(BakeJogadas).filter_by(id_usuario=id_user, utilizado=False).all()

        return query, jogada


def random_produtos(db: object) -> object:

    query = db.query(BakeProdutos.categoria).distinct().all()

    cat_rand = random.choice(query)[0]

    prod = db.query(BakeProdutos).filter_by(categoria=str(cat_rand), ativo=1).all()

    return random.choice(prod)


def gera_voucher(jogada: object, id_prod: int, db: object):

    voucher = BakeVoucher(
        id_compra=jogada.id_compra,
        id_produto=id_prod,
        id_usuario=jogada.id_usuario,
        id_jogada=jogada.id_jogada
    )
    db.add(voucher)
