from pathlib import Path
from ..persistencia.sessao_oracle import conectar, sessao
from ..persistencia.formatacao_sql import id_sql


class Relatorios:
    PASTA_SQL = Path(__file__).resolve().parents[1] / 'consultas_sql'
    ARQUIVOS = {
        'resumo': 'saldo_por_fornecedor.sql',
        'produtos': 'catalogo_com_fornecedores.sql',
        'baixo': 'alerta_reposicao.sql',
    }

    def __init__(self, fabrica_conexao=conectar):
        self._fabrica = fabrica_conexao

    def contagens(self):
        resultado = {}
        with sessao(self._fabrica) as cursor:
            for tabela in ('FORNECEDOR', 'PRODUTO'):
                sql = 'SELECT COUNT(1) total_' + tabela.lower() + ' FROM ' + tabela
                cursor.execute(sql)
                resultado[tabela] = int(cursor.fetchone()[0])
        return resultado

    def consultar(self, nome, limite=5):
        # O nome de arquivo vem apenas deste mapa interno.
        arquivo = self.ARQUIVOS[nome]
        sql = (self.PASTA_SQL / arquivo).read_text(encoding='utf-8').strip().rstrip(';')
        if nome == 'baixo':
            if type(limite) is not int or limite < 0:
                raise ValueError('O limite de estoque deve ser um inteiro não negativo.')
            sql += ' WHERE p.quantidade <= ' + id_sql(limite)
            sql += ' ORDER BY p.quantidade, p.nome'
        with sessao(self._fabrica) as cursor:
            cursor.execute(sql)
            colunas = [item[0] for item in cursor.description]
            linhas = cursor.fetchall()
        return colunas, linhas
