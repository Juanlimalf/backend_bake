from app.models.schemas import BakeProdutos, BakeVoucher, BakeCompras, BakeJogadas
import random
from datetime import datetime
import pytz
from sqlalchemy import text


def busca_id_cliente(cpf: str, db: object) -> int:

    select = text(f"select u.id_usuario from meunagumo.usuario u where u.username = '{cpf}'")

    query = db.execute(select).all()

    if query == []:
        return False
    else:
        return query[0][0]


def insere_compra(id_client: int, gera_jogada: bool, compra: object, db: object) -> int:
    compra = BakeCompras(
        loja=str(compra.loja),
        coo=str(compra.coo),
        checkout=str(compra.checkout),
        valor=float(compra.valor),
        id_usuario=int(id_client),
        gera_jogada=gera_jogada,
        usuario_inclusao=str(compra.user_inclusao)
    )
    db.add(compra)

    id_compra = db.query(BakeCompras.id_compra). \
        filter(BakeCompras.coo == compra.coo and
               BakeCompras.checkout == compra.checkout and
               BakeCompras.loja == compra.loja).order_by(BakeCompras.id_compra.desc()).first()[0]

    return id_compra


def consultaCompras(id_client: int, db: object):

    compra = db.query(BakeCompras).filter(BakeCompras.id_usuario == id_client).all()

    return compra


def consulta_compra(id_client: int, id_compra: int, db: object):

    compra = db.query(BakeCompras)\
        .filter_by(id_usuario=id_client, id_compra=id_compra)\
        .all()

    return compra


def verifica_Compra(compra, db):

    query = db.query(BakeCompras).filter_by(coo=compra.coo, loja=compra.loja, checkout=compra.checkout).all()
    if query == []:
        return False
    else:
        return True


def insere_jogada(id_compra: int, id_client: int, db: object):
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

    query = db.query(BakeVoucher).filter_by(id_usuario=id_user)\
        .order_by(BakeVoucher.utilizado.asc(), BakeVoucher.ativo.asc()).all()

    return query


def cons_voucher_uni(voucher: str, db: object):

    query = db.query(BakeVoucher).filter_by(codigo_voucher=voucher).all()

    return query


def get_vouchers(loja: str, data: str, db: object):

    data_formatada = datetime.strptime(data, "%Y-%m-%d")

    select = f'''select bc.loja, bv.id_voucher, bv.codigo_voucher, 
                bp.descricao_produto, bv.valor, bv.data_inclusao, bv.ativo
                from bake_vouchers bv
                inner join bake_compras bc on bv.id_compra = bc.id_compra
                inner join bake_produtos bp on bp.id_produto = bv.id_produto 
                WHERE CAST(bv.data_atualizacao as date) = '{data_formatada}'
                and bc.loja = '{loja}'
                and bv.ativo = 1'''

    query = db.execute(select).all()

    return query


def consulta_produto(id_prod: int, db: object) -> list:

    query = db.query(BakeProdutos).filter_by(id_produto=id_prod).all()

    return query


def consulta_produto_full(db: object) -> list:

    query = db.query(BakeProdutos).filter_by(ativo=1).all()

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


def random_produtos(categoria: str, db: object) -> object:

    """ Sortear Backend escolhendo categoria e produto"""
    # controle = random.randint(1, 5)
    #
    # if controle == 1:
    #     query = db.query(BakeProdutos.categoria).filter_by(tipo="P").distinct().all()
    #     cat_rand = random.choice(query)[0]
    #     prod = db.query(BakeProdutos).filter_by(categoria=str(cat_rand), ativo=1).all()
    #     return random.choice(prod)
    # else:
    #     prod = db.query(BakeProdutos).filter_by(tipo="D", ativo=1).all()
    #     return random.choice(prod)
    # query = db.query(BakeProdutos.categoria).filter_by(tipo="P").distinct().all()
    # cat_rand = random.choice(query)[0]

    """ Sortear Frontend escolhendo a categoria """
    # prod = db.query(BakeProdutos).filter_by(categoria=str(categoria), ativo=1).all()

    """Sortear sem escolher a categoria"""
    prod = db.query(BakeProdutos).filter_by(ativo=1).all()
    print(prod)

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

    v.codigo_voucher = f"{'{:05d}'.format(jogada.id_usuario)}" \
                       f"{'{:06}'.format(produto.cod_acesso)}" \
                       f"{'{:05}'.format(v.id_voucher)}"


def consumir_voucher(voucher: object, db: object):

    query = db.query(BakeVoucher).filter_by(codigo_voucher=voucher).all()[0]
    if query.utilizado == 1:
        return False
    else:
        query.utilizado = 1
        return True


def ativar_voucher(voucher: object, valor:float, db: object):

    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz=tz)

    query = db.query(BakeVoucher).filter_by(codigo_voucher=voucher).all()[0]
    query.ativo = 1
    query.data_ativacao = now
    query.valor = valor

    response = db.query(BakeVoucher).filter_by(codigo_voucher=voucher).all()[0]

    return response


def aceite_termos(id_cliente, db):

    select = text(f"SELECT * FROM aceite_campanhas WHERE id_campanha = 1 and id_usuario = {id_cliente} and aceite = 1")

    select_query = db.execute(select).all()
    
    if len(select_query) > 0:
        return False
    else:
        insert = text(f"INSERT INTO aceite_campanhas(id_campanha, id_usuario, aceite) values(1, {id_cliente}, 1)")
        insert_query = db.execute(insert)

        return True
    

def consulta_aceite(id_cliente, db):

    select = text(f"SELECT aceite FROM aceite_campanhas WHERE id_campanha = 1 and id_usuario = {id_cliente}")

    select_query = db.execute(select).first()

    if select_query == None:
        return 0
    else:
        return select_query[0]
