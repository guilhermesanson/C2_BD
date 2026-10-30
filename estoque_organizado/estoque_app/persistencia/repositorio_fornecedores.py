from ..entidades import Fornecedor
from .operacoes_comuns import ControllerBase
from .excecoes_estoque import RegistroJaExiste, AssociacaoInvalida
from .formatacao_sql import literal, id_sql


class ControllerFornecedor(ControllerBase):
    TABELA = 'FORNECEDOR'
    PK = 'id_fornecedor'
    ALIAS = 'f'
    CAMPOS = ('nome', 'cnpj', 'telefone', 'email', 'logradouro', 'numero',
              'complemento', 'bairro', 'cidade', 'estado', 'cep')
    SELECT = ('SELECT f.id_fornecedor, ' + ', '.join('f.' + c for c in CAMPOS)
              + ' FROM FORNECEDOR f')

    def _dados(self, objeto):
        return {campo: getattr(objeto, 'get_' + campo)() for campo in self.CAMPOS}

    def _validar(self, cursor, objeto):
        sql = 'SELECT id_fornecedor FROM FORNECEDOR WHERE cnpj = '
        sql += literal(objeto.get_cnpj())
        cursor.execute(sql)
        linha = cursor.fetchone()
        if linha is not None and int(linha[0]) != objeto.get_id_fornecedor():
            raise RegistroJaExiste('CNPJ já cadastrado.')

    def _antes_excluir(self, cursor, identificador):
        sql = 'SELECT id_produto FROM PRODUTO WHERE id_fornecedor = '
        sql += id_sql(identificador)
        cursor.execute(sql)
        if cursor.fetchone() is not None:
            raise AssociacaoInvalida('Fornecedor possui produtos; remova ou reassocie-os antes.')

    @staticmethod
    def _objeto(linha):
        dados = dict(zip(('id_fornecedor',) + ControllerFornecedor.CAMPOS, linha))
        dados['id_fornecedor'] = int(dados['id_fornecedor'])
        return Fornecedor(**dados)
