import unittest
from decimal import Decimal
from unittest.mock import MagicMock
from estoque_app.entidades import Fornecedor, Produto
from estoque_app.persistencia import ControllerFornecedor, ControllerProduto
from estoque_app.persistencia.excecoes_estoque import RegistroJaExiste, RegistroNaoEncontrado, AssociacaoInvalida


def fornecedor():
    return Fornecedor("D'Ávila", '00.000.000/0001-00', 'Rua', '1', 'Centro', 'Vitória', 'ES', '29000-000')


class TestControllers(unittest.TestCase):
    def setUp(self):
        self.con = MagicMock()
        self.cur = self.con.cursor.return_value.__enter__.return_value
        self.factory = MagicMock(return_value=self.con)
        self.cf = ControllerFornecedor(self.factory)
        self.cp = ControllerProduto(self.factory)
        self.cur.rowcount = 1
        self.cur.lastrowid = 'AAATESTAAAAAAAABAAA'

    def test_inserir_identity_e_concatenacao(self):
        f = fornecedor()
        self.cur.fetchone.side_effect = [None, (42,)]
        self.assertEqual(self.cf.inserir(f), 42)
        sql = self.cur.execute.call_args_list[-2].args[0]
        self.assertNotIn("D'Ávila", sql)
        self.assertIn("'D''Ávila'", sql)
        self.assertIn('NULL', sql)
        self.assertIn("WHERE ROWID = 'AAATESTAAAAAAAABAAA'", self.cur.execute.call_args.args[0])
        self.assertTrue(all(len(call.args) == 1 for call in self.cur.execute.call_args_list))
        self.assertEqual(f.get_id_fornecedor(), 42)
        self.con.commit.assert_called_once()
        self.con.close.assert_called_once()

    def test_pk_duplicada(self):
        f = fornecedor(); f.set_id_fornecedor(42)
        self.cur.fetchone.return_value = (42,)
        with self.assertRaises(RegistroJaExiste): self.cf.inserir(f)
        self.con.rollback.assert_called_once()
        self.con.commit.assert_not_called()

    def test_cnpj_duplicado(self):
        self.cur.fetchone.return_value = (4,)
        with self.assertRaises(RegistroJaExiste): self.cf.inserir(fornecedor())

    def test_atualizacao_inexistente(self):
        self.cur.fetchone.return_value = None
        f=fornecedor(); f.set_id_fornecedor(42)
        with self.assertRaises(RegistroNaoEncontrado): self.cf.atualizar(f)

    def test_exclusao_inexistente(self):
        self.cur.fetchone.return_value = None
        with self.assertRaises(RegistroNaoEncontrado): self.cp.excluir(42)

    def test_fornecedor_em_uso(self):
        self.cur.fetchone.side_effect = [(42,), (9,)]
        with self.assertRaises(AssociacaoInvalida): self.cf.excluir(42)

    def test_produto_sem_fornecedor_persistido(self):
        p=Produto('Teste',Decimal('5.00'),1,fornecedor())
        with self.assertRaises(AssociacaoInvalida): self.cp.inserir(p)

    def test_produto_fornecedor_inexistente(self):
        f=fornecedor(); f.set_id_fornecedor(42)
        self.cur.fetchone.return_value=None
        with self.assertRaises(AssociacaoInvalida):
            self.cp.inserir(Produto('Teste',Decimal('5.00'),1,f))

    def test_produto_preco_e_quantidade_invalidos(self):
        f=fornecedor();f.set_id_fornecedor(42)
        self.cur.fetchone.return_value=(42,)
        for preco,quantidade in [(Decimal('-1'),1),(Decimal('1.001'),1),(Decimal('1'),-1),(Decimal('1'),1.5)]:
            with self.subTest(preco=preco,quantidade=quantidade):
                with self.assertRaises(ValueError):
                    self.cp.inserir(Produto('Teste',preco,quantidade,f))

    def test_atualizar_produto(self):
        f=fornecedor();f.set_id_fornecedor(42)
        p=Produto('Novo',Decimal('12.50'),3,f,id_produto=9)
        self.cur.fetchone.side_effect=[(9,),(42,)]
        self.cp.atualizar(p)
        sql=self.cur.execute.call_args.args[0]
        self.assertTrue(sql.startswith('UPDATE PRODUTO'))
        self.assertIn('id_fornecedor = 42',sql)
        self.assertIn('preco = 12.50',sql)
        self.con.commit.assert_called_once()

    def test_excluir_produto(self):
        self.cur.fetchone.return_value=(9,)
        self.cp.excluir(9)
        self.assertEqual(self.cur.execute.call_args.args,('DELETE FROM PRODUTO WHERE id_produto = 9',))
        self.con.commit.assert_called_once()

    def test_reconstrucao_associacao(self):
        self.cur.fetchone.return_value=(9,'Produto',None,12.5,3,42,"D'Ávila",'00',None,None,'Rua','1',None,'Centro','Vitória','ES','29000-000')
        p=self.cp.buscar_por_id(9)
        self.assertIsInstance(p.get_fornecedor(),Fornecedor)
        self.assertEqual(p.get_fornecedor().get_id_fornecedor(),42)
        self.assertEqual(p.get_preco(),Decimal('12.5'))

    def test_busca_inexistente_e_listagem(self):
        self.cur.fetchone.return_value=None
        self.assertIsNone(self.cf.buscar_por_id(1))
        self.cur.fetchall.return_value=[]
        self.assertEqual(self.cp.listar(),[])

    def test_falha_commit_preserva_id(self):
        f=fornecedor();self.cur.fetchone.side_effect=[None,(42,)]
        self.con.commit.side_effect=RuntimeError('Falha')
        with self.assertRaises(RuntimeError):self.cf.inserir(f)
        self.assertIsNone(f.get_id_fornecedor())
        self.con.rollback.assert_called_once()
        self.con.close.assert_called_once()

    def test_existe_abre_conexao(self):
        self.cur.fetchone.return_value=(1,)
        self.assertTrue(self.cf.existe(1))
        self.factory.assert_called_once()
        self.con.close.assert_called_once()


if __name__ == '__main__': unittest.main()
