import sqlite3
import unittest
from pathlib import Path
from unittest.mock import MagicMock
from estoque_app.consultas.indicadores_estoque import Relatorios


class TestRelatorios(unittest.TestCase):
    def test_contagens_conectam_e_consultam_duas_tabelas(self):
        con=MagicMock();cur=con.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect=[(3,),(8,)]
        resultado=Relatorios(lambda:con).contagens()
        self.assertEqual(resultado,{'FORNECEDOR':3,'PRODUTO':8})
        self.assertIn('SELECT COUNT(1)',cur.execute.call_args_list[0].args[0])
        con.close.assert_called_once()

    def test_relatorio_baixo_concatena_limite(self):
        con=MagicMock();cur=con.cursor.return_value.__enter__.return_value
        cur.description=[('ID_PRODUTO',)];cur.fetchall.return_value=[]
        colunas,linhas=Relatorios(lambda:con).consultar('baixo',4)
        self.assertEqual(colunas,['ID_PRODUTO'])
        self.assertIn('WHERE p.quantidade <= 4',cur.execute.call_args.args[0])
        self.assertEqual(len(cur.execute.call_args.args),1)
        with self.assertRaises(ValueError):Relatorios(lambda:con).consultar('baixo',-1)

    def test_calculos_relatorios_em_sqlite_apenas(self):
        # Verifica cálculo e cardinalidade com SQLite; não valida sintaxe no Oracle.
        con=sqlite3.connect(':memory:')
        con.create_function('NVL',2,lambda a,b:b if a is None else a)
        try:
            con.executescript('''
                CREATE TABLE FORNECEDOR(id_fornecedor INTEGER, nome TEXT, cnpj TEXT, telefone TEXT);
                CREATE TABLE PRODUTO(id_produto INTEGER, nome TEXT, preco NUMERIC, quantidade INTEGER, id_fornecedor INTEGER);
                INSERT INTO FORNECEDOR VALUES(1,'A','11',NULL),(2,'B','22',NULL);
                INSERT INTO PRODUTO VALUES(1,'P1',10,3,1),(2,'P2',20,2,1);
            ''')
            pasta=Relatorios.PASTA_SQL
            linhas=con.execute((pasta/'saldo_por_fornecedor.sql').read_text()).fetchall()
            self.assertEqual(linhas,[(1,'A',2,5,70),(2,'B',0,0,0)])
            linhas=con.execute((pasta/'catalogo_com_fornecedores.sql').read_text()).fetchall()
            self.assertEqual(len(linhas),2)
            self.assertTrue(all(l[5]=='A' for l in linhas))
        finally:con.close()
