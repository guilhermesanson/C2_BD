import unittest
from decimal import Decimal
from estoque_app.persistencia.formatacao_sql import literal, id_sql


class TestLiterais(unittest.TestCase):
    def test_texto_com_apostrofo(self):
        self.assertEqual(literal("D'Ávila"), "'D''Ávila'")
        self.assertEqual(literal("x'); DELETE FROM PRODUTO; --"),
                         "'x''); DELETE FROM PRODUTO; --'")

    def test_nulos_e_numeros(self):
        self.assertEqual(literal(None), 'NULL')
        self.assertEqual(literal(Decimal('12.50')), '12.50')
        self.assertEqual(literal(Decimal('1E+2')), '100')
        self.assertEqual(literal(4), '4')

    def test_identificador_deve_ser_inteiro(self):
        for valor in ['1 OR 1=1', True, 1.5, None]:
            with self.assertRaises(TypeError): id_sql(valor)

    def test_rejeita_tipos_nao_suportados(self):
        for valor in [True, 1.2, Decimal('NaN'), Decimal('Infinity')]:
            with self.assertRaises(TypeError): literal(valor)
