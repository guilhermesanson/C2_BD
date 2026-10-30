import os
from contextlib import contextmanager


def conectar():
    """Abre uma conexão usando variáveis de ambiente, sem senha no código."""
    import oracledb
    nomes = ("ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN")
    faltantes = [nome for nome in nomes if not os.environ.get(nome)]
    if faltantes:
        raise RuntimeError("Configure as variáveis: " + ", ".join(faltantes))
    return oracledb.connect(user=os.environ["ORACLE_USER"],
                            password=os.environ["ORACLE_PASSWORD"],
                            dsn=os.environ["ORACLE_DSN"])


@contextmanager
def sessao(fabrica, escrita=False):
    conexao = fabrica()
    try:
        with conexao.cursor() as cursor:
            yield cursor
        if escrita:
            conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
