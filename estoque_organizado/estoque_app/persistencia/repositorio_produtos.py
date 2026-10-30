from decimal import Decimal
from ..entidades import Fornecedor, Produto
from .operacoes_comuns import ControllerBase
from .repositorio_fornecedores import ControllerFornecedor
from .excecoes_estoque import AssociacaoInvalida
from .formatacao_sql import id_sql


class ControllerProduto(ControllerBase):
    TABELA = 'PRODUTO'
    PK = 'id_produto'
    ALIAS = 'p'
    CAMPOS = ('nome', 'descricao', 'preco', 'quantidade', 'id_fornecedor')
    SELECT = ('SELECT p.id_produto, p.nome, p.descricao, p.preco, p.quantidade, '
              'f.id_fornecedor, ' + ', '.join('f.' + c for c in ControllerFornecedor.CAMPOS)
              + ' FROM PRODUTO p JOIN FORNECEDOR f ON f.id_fornecedor = p.id_fornecedor')

    def _validar(self, cursor, objeto):
        fornecedor = objeto.get_fornecedor()
        if not isinstance(fornecedor, Fornecedor) or fornecedor.get_id_fornecedor() is None:
            raise AssociacaoInvalida('Informe um objeto Fornecedor já cadastrado.')
        sql = 'SELECT id_fornecedor FROM FORNECEDOR WHERE id_fornecedor = '
        sql += id_sql(fornecedor.get_id_fornecedor())
        cursor.execute(sql)
        if cursor.fetchone() is None:
            raise AssociacaoInvalida('Fornecedor não encontrado no banco.')
        preco = objeto.get_preco()
        if not isinstance(preco, Decimal) or not preco.is_finite() or preco < 0:
            raise ValueError('Preço deve ser Decimal finito e não negativo.')
        if preco > Decimal('99999999.99') or preco != preco.quantize(Decimal('0.01')):
            raise ValueError('Preço deve caber em NUMBER(10,2), sem arredondamento.')
        quantidade = objeto.get_quantidade()
        if type(quantidade) is not int or not 0 <= quantidade <= 9999999999:
            raise ValueError('Quantidade deve ser um inteiro entre 0 e 9999999999.')

    def _dados(self, objeto):
        return {'nome': objeto.get_nome(), 'descricao': objeto.get_descricao(),
                'preco': objeto.get_preco(), 'quantidade': objeto.get_quantidade(),
                'id_fornecedor': objeto.get_fornecedor().get_id_fornecedor()}

    @staticmethod
    def _objeto(linha):
        fornecedor = ControllerFornecedor._objeto(linha[5:])
        return Produto(id_produto=int(linha[0]), nome=linha[1], descricao=linha[2],
                       preco=Decimal(str(linha[3])), quantidade=int(linha[4]),
                       fornecedor=fornecedor)
