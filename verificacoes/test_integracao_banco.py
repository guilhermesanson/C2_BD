import os
import unittest
import uuid
from decimal import Decimal
from estoque_app.persistencia import ControllerFornecedor, ControllerProduto
from estoque_app.persistencia.excecoes_estoque import RegistroJaExiste, AssociacaoInvalida, RegistroNaoEncontrado
from estoque_app.entidades import Fornecedor, Produto
from estoque_app.consultas.indicadores_estoque import Relatorios


@unittest.skipUnless(os.environ.get('EXECUTAR_TESTES_ORACLE') == '1', 'Integração Oracle não habilitada')
class TestOracle(unittest.TestCase):
    def test_ciclo_completo(self):
        cf,cp=ControllerFornecedor(),ControllerProduto()
        cnpj=str(uuid.uuid4().int % (10**14)).zfill(14)
        f=Fornecedor("Teste D'Ávila",cnpj,'Rua Teste','1','Centro','Vitória','ES','29000-000')
        p=Produto('Teste integração',Decimal('12.50'),2,f)
        try:
            cf.inserir(f)
            self.assertTrue(cf.existe(f.get_id_fornecedor()))
            with self.assertRaises(RegistroJaExiste):cf.inserir(f)
            duplicado=Fornecedor('Duplicado',cnpj,'Rua','2','Centro','Vitória','ES','29000-000')
            with self.assertRaises(RegistroJaExiste):cf.inserir(duplicado)
            f.set_nome('Fornecedor atualizado');cf.atualizar(f)
            self.assertEqual(cf.buscar_por_id(f.get_id_fornecedor()).get_nome(),f.get_nome())
            self.assertTrue(any(x.get_id_fornecedor()==f.get_id_fornecedor() for x in cf.listar()))
            cp.inserir(p)
            self.assertTrue(cp.existe(p.get_id_produto()))
            self.assertEqual(cp.buscar_por_id(p.get_id_produto()).get_fornecedor().get_id_fornecedor(),f.get_id_fornecedor())
            p.set_preco(Decimal('25.90'));p.set_quantidade(4);cp.atualizar(p)
            self.assertEqual(cp.buscar_por_id(p.get_id_produto()).get_preco(),Decimal('25.90'))
            self.assertTrue(any(x.get_id_produto()==p.get_id_produto() for x in cp.listar()))
            relatorios=Relatorios()
            self.assertGreaterEqual(relatorios.contagens()['PRODUTO'],1)
            _,resumo=relatorios.consultar('resumo')
            linha=next(x for x in resumo if int(x[0])==f.get_id_fornecedor())
            self.assertEqual(int(linha[2]),1)
            self.assertEqual(int(linha[3]),4)
            self.assertEqual(Decimal(str(linha[4])),Decimal('103.60'))
            _,itens=relatorios.consultar('produtos')
            self.assertTrue(any(int(x[0])==p.get_id_produto() for x in itens))
            _,baixos=relatorios.consultar('baixo',4)
            self.assertTrue(any(int(x[0])==p.get_id_produto() for x in baixos))
            with self.assertRaises(AssociacaoInvalida):cf.excluir(f.get_id_fornecedor())
            cp.excluir(p.get_id_produto())
            self.assertFalse(cp.existe(p.get_id_produto()))
            with self.assertRaises(RegistroNaoEncontrado):cp.atualizar(p)
            with self.assertRaises(RegistroNaoEncontrado):cp.excluir(p.get_id_produto())
            cf.excluir(f.get_id_fornecedor())
            self.assertIsNone(cf.buscar_por_id(f.get_id_fornecedor()))
        finally:
            # Remove somente os registros criados por este teste, produto primeiro.
            if p.get_id_produto() is not None and cp.existe(p.get_id_produto()):cp.excluir(p.get_id_produto())
            if f.get_id_fornecedor() is not None and cf.existe(f.get_id_fornecedor()):cf.excluir(f.get_id_fornecedor())


if __name__ == '__main__':unittest.main()
