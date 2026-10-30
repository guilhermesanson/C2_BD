"""Conversão de atributos em literais para o SQL concatenado da atividade."""
from decimal import Decimal


def literal(valor):
    if valor is None:
        return 'NULL'
    if isinstance(valor, str):
        return "'" + valor.replace("'", "''") + "'"
    if type(valor) is int:
        return str(valor)
    if isinstance(valor, Decimal) and valor.is_finite():
        return format(valor, 'f')
    raise TypeError('Use str, int, Decimal finito ou None nos atributos SQL.')


def id_sql(valor):
    if type(valor) is not int:
        raise TypeError('O identificador deve ser int.')
    return str(valor)
