from models.schemas import BakeProdutos, BakeVoucher, BakeCompras, Usuario, BakeJogadas
import random


def busca_id_cliente(cpf: str, db: object) -> int:
    query = db.query(Usuario.id_usuario).filter(Usuario.username == f'{cpf}').all()

    if query == []:
        return False
    else:
        return query[0][0]


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


def cons_voucher_uni(voucher: str, db: object):

    query = db.query(BakeVoucher).filter_by(codigo_voucher=voucher).all()
    if query == []:
        return False
    elif query[0].utilizado == True:
        return False
    else:
        return query[0]


def consulta_produto(id_prod: int, db: object) -> list:

    query = db.query(BakeProdutos).filter_by(id_produto=id_prod).all()[0]

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

    controle = random.randint(1, 5)

    if controle == 1:
        query = db.query(BakeProdutos.categoria).filter_by(tipo="P").distinct().all()
        cat_rand = random.choice(query)[0]
        prod = db.query(BakeProdutos).filter_by(categoria=str(cat_rand), ativo=1).all()
        return random.choice(prod)
    else:
        prod = db.query(BakeProdutos).filter_by(tipo="D", ativo=1).all()
        return random.choice(prod)


def gera_voucher(jogada: object, produto: object, db: object):

    voucher = BakeVoucher(
        id_compra=jogada.id_compra,
        id_produto=produto.id_produto,
        id_usuario=jogada.id_usuario,
        id_jogada=jogada.id_jogada
    )
    db.add(voucher)
    v = db.query(BakeVoucher).filter_by(id_compra=jogada.id_compra,
                                        id_produto=produto.id_produto,
                                        id_usuario=jogada.id_usuario,
                                        id_jogada=jogada.id_jogada).order_by(BakeVoucher.id_voucher.desc()).first()

    v.codigo_voucher = f"{'{:06}'.format(produto.cod_acesso)}" \
                       f"{'{:05}'.format(v.id_voucher)}" \
                       f"{'{:05d}'.format(jogada.id_usuario)}"


def consumir_voucher(dados_voucher: object, db: object):

    update = db.query(BakeVoucher).filter_by(codigo_voucher=dados_voucher.voucher).all()[0]
    if update.utilizado == 1:
        return False
    else:
        update.cupom_utilizado = dados_voucher.coo
        update.checkout_utilizado = dados_voucher.checkout
        update.utilizado = 1
    return True

