from .sessao_oracle import conectar, sessao
from .excecoes_estoque import RegistroJaExiste, RegistroNaoEncontrado
from .formatacao_sql import literal, id_sql


class ControllerBase:
    """CRUD comum. Identificadores SQL vêm somente das constantes das subclasses.

    Cada operação pública abre sua conexão; verificações internas compartilham
    a conexão e a transação da operação. O SQL concatena literais dos atributos.
    """
    def __init__(self, fabrica_conexao=conectar):
        self._fabrica = fabrica_conexao

    def _existe(self, cursor, identificador, bloquear=False):
        if identificador is None:
            return False
        sql = 'SELECT ' + self.PK + ' FROM ' + self.TABELA
        sql += ' WHERE ' + self.PK + ' = ' + id_sql(identificador)
        if bloquear:
            sql += " FOR UPDATE"
        cursor.execute(sql)
        return cursor.fetchone() is not None

    def existe(self, identificador):
        with sessao(self._fabrica) as cursor:
            return self._existe(cursor, identificador)

    def _exigir(self, cursor, identificador):
        if not self._existe(cursor, identificador, bloquear=True):
            raise RegistroNaoEncontrado(f"{self.TABELA}: registro não encontrado.")

    def _validar(self, cursor, objeto):
        pass

    def inserir(self, objeto):
        identificador = getattr(objeto, 'get_' + self.PK)()
        with sessao(self._fabrica, escrita=True) as cursor:
            if self._existe(cursor, identificador):
                raise RegistroJaExiste(f"{self.TABELA}: identificador já cadastrado.")
            if identificador is not None:
                raise ValueError("Para inserir, deixe o ID como None; o Oracle gera a chave.")
            self._validar(cursor, objeto)
            dados = self._dados(objeto)
            colunas = ', '.join(self.CAMPOS)
            valores = ', '.join(literal(dados[campo]) for campo in self.CAMPOS)
            sql = 'INSERT INTO ' + self.TABELA + ' (' + colunas + ')'
            sql += ' VALUES (' + valores + ')'
            cursor.execute(sql)
            # Recupera o IDENTITY da linha inserida na mesma transação.
            rowid = cursor.lastrowid
            if not isinstance(rowid, str) or not rowid:
                raise RuntimeError('O Oracle não retornou o ROWID da inserção.')
            sql = 'SELECT ' + self.PK + ' FROM ' + self.TABELA
            sql += ' WHERE ROWID = ' + literal(rowid)
            cursor.execute(sql)
            linha = cursor.fetchone()
            if linha is None:
                raise RuntimeError('Não foi possível recuperar o ID gerado.')
            novo_id = int(linha[0])
        # Só modifica o objeto depois de confirmar a transação.
        getattr(objeto, 'set_' + self.PK)(novo_id)
        return novo_id

    def atualizar(self, objeto):
        identificador = getattr(objeto, 'get_' + self.PK)()
        with sessao(self._fabrica, escrita=True) as cursor:
            self._exigir(cursor, identificador)
            self._validar(cursor, objeto)
            dados = self._dados(objeto)
            atribuicoes = ', '.join(campo + ' = ' + literal(dados[campo])
                                    for campo in self.CAMPOS)
            sql = 'UPDATE ' + self.TABELA + ' SET ' + atribuicoes
            sql += ' WHERE ' + self.PK + ' = ' + id_sql(identificador)
            cursor.execute(sql)
            if cursor.rowcount != 1:
                raise RegistroNaoEncontrado("Nenhum registro atualizado.")

    def excluir(self, identificador):
        with sessao(self._fabrica, escrita=True) as cursor:
            self._exigir(cursor, identificador)
            self._antes_excluir(cursor, identificador)
            sql = 'DELETE FROM ' + self.TABELA
            sql += ' WHERE ' + self.PK + ' = ' + id_sql(identificador)
            cursor.execute(sql)
            if cursor.rowcount != 1:
                raise RegistroNaoEncontrado("Nenhum registro excluído.")

    def _antes_excluir(self, cursor, identificador):
        pass

    def buscar_por_id(self, identificador):
        with sessao(self._fabrica) as cursor:
            sql = self.SELECT + ' WHERE ' + self.ALIAS + '.' + self.PK
            sql += ' = ' + id_sql(identificador)
            cursor.execute(sql)
            linha = cursor.fetchone()
            return self._objeto(linha) if linha is not None else None

    def listar(self):
        with sessao(self._fabrica) as cursor:
            sql = self.SELECT + ' ORDER BY ' + self.ALIAS + '.' + self.PK
            cursor.execute(sql)
            return [self._objeto(linha) for linha in cursor.fetchall()]
