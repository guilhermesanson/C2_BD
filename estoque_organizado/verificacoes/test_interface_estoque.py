import unittest
from copy import deepcopy
from decimal import Decimal
from unittest.mock import MagicMock
from estoque_app.navegacao_terminal import Aplicacao
from estoque_app.entidades import Fornecedor, Produto
from estoque_app.interface.leitura_campos import Entrada


class Memoria:
    """Double de teste: não é um banco nem faz parte da aplicação."""
    def __init__(self, entidade):
        self.entidade=entidade
        self.dados={}

    def inserir(self,objeto):
        ident=max(self.dados,default=0)+1
        getattr(objeto,'set_id_'+self.entidade)(ident)
        self.dados[ident]=deepcopy(objeto)
        return ident

    def listar(self): return list(self.dados.values())
    def buscar_por_id(self,ident): return deepcopy(self.dados.get(ident))
    def atualizar(self,objeto):
        ident=getattr(objeto,'get_id_'+self.entidade)()
        self.dados[ident]=deepcopy(objeto)
    def excluir(self,ident): del self.dados[ident]


class TestAplicacao(unittest.TestCase):
    def setUp(self):
        self.cf=Memoria('fornecedor');self.cp=Memoria('produto');self.saidas=[]
        self.f=Fornecedor('Fornecedor','00','Rua','1','Centro','Vitória','ES','29000-000')
        self.cf.inserir(self.f)

    def app(self,respostas):
        it=iter(respostas)
        return Aplicacao(self.cf,self.cp,leitor=lambda _:next(it),saida=self.saidas.append)

    def test_insercao_produto(self):
        self.app(['2','1','Teclado','USB','89,90','20','n']).manter('inserir')
        p=self.cp.buscar_por_id(1)
        self.assertEqual(p.get_preco(),Decimal('89.90'))
        self.assertEqual(p.get_fornecedor().get_id_fornecedor(),1)

    def test_insercao_fornecedor_e_repeticao(self):
        campos=['Nome','11','','','Rua','2','','Bairro','Cidade','es','29000-000']
        self.app(['1']+campos+['s','0']).manter('inserir')
        self.assertEqual(len(self.cf.listar()),2)
        self.assertEqual(self.cf.buscar_por_id(2).get_estado(),'ES')

    def test_atualizar_produto_exibe_resultado(self):
        self.cp.inserir(Produto('Antes',Decimal('1'),2,self.f))
        self.app(['2','1','','Depois','','2,50','7','n']).manter('atualizar')
        p=self.cp.buscar_por_id(1)
        self.assertEqual((p.get_nome(),p.get_quantidade()),('Depois',7))
        self.assertTrue(any('Registro atualizado:' in s and 'Depois' in s for s in self.saidas))

    def test_atualizar_fornecedor_preserva_id_e_limpa_opcional(self):
        self.app(['1','1','Atualizado','','-','','','','','','','','','n']).manter('atualizar')
        f=self.cf.buscar_por_id(1)
        self.assertEqual(f.get_nome(),'Atualizado')
        self.assertIsNone(f.get_telefone())
        self.assertEqual(f.get_id_fornecedor(),1)

    def test_exclusao_cancelada(self):
        self.app(['1','1','n']).manter('excluir')
        self.assertIsNotNone(self.cf.buscar_por_id(1))

    def test_exclusao_confirmada(self):
        self.app(['1','1','s','n']).manter('excluir')
        self.assertIsNone(self.cf.buscar_por_id(1))

    def test_menu_invalido_continua_e_relatorios_retornam(self):
        app=self.app(['x','1','1','2','3','5','0','0'])
        rel=MagicMock()
        rel.contagens.return_value={'FORNECEDOR':1,'PRODUTO':0}
        rel.consultar.return_value=(['COLUNA'],[(1,)])
        app.relatorios=rel
        app.executar()
        self.assertEqual(rel.consultar.call_count,3)
        for nome in ['Guilherme Sanson Malarcarne','Luan Gonçalves dos Santos','Howard Roatti','2026/2']:
            self.assertTrue(any(nome in s for s in self.saidas))
        self.assertIn('PRODUTO: 0 registro(s) - sem registros',self.saidas)
        self.assertIn('Sistema encerrado.',self.saidas)

    def test_entrada_rejeita_numero_invalido(self):
        it=iter(['abc','-1','1.001','NaN','12,50'])
        e=Entrada(lambda _:next(it),self.saidas.append)
        self.assertEqual(e.preco(),Decimal('12.50'))
