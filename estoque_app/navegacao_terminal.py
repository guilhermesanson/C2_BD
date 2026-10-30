from .persistencia import ControllerFornecedor, ControllerProduto
from .entidades import Fornecedor, Produto
from .consultas.indicadores_estoque import Relatorios
from .interface import menu_estoque
from .interface.leitura_campos import Entrada
from .interface.abertura_sistema import SplashScreen


class Aplicacao:
    def __init__(self, fornecedores=None, produtos=None, relatorios=None, leitor=input, saida=print):
        self.fornecedores = fornecedores if fornecedores is not None else ControllerFornecedor()
        self.produtos = produtos if produtos is not None else ControllerProduto()
        self.relatorios = relatorios if relatorios is not None else Relatorios()
        self.saida = saida
        self.entrada = Entrada(leitor, saida)

    def executar(self):
        SplashScreen().exibir(self.relatorios, self.saida)
        while True:
            self.saida(menu_estoque.MENU_PRINCIPAL)
            opcao = self.entrada.ler('Opção: ').strip()
            if opcao == '0':
                self.saida('Sistema encerrado.')
                return
            if opcao == '1':
                self.reports()
            elif opcao in ('2', '3', '4'):
                self.manter({'2': 'inserir', '3': 'excluir', '4': 'atualizar'}[opcao])
            else:
                self.saida('Opção inválida.')

    def _listar(self, controller, entidade):
        registros = controller.listar()
        if not registros:
            self.saida('Nenhum registro cadastrado.')
        for registro in registros:
            identificador = getattr(registro, 'get_id_' + entidade)()
            self.saida(str(identificador) + ' | ' + registro.get_nome())
        return registros

    def _escolher_fornecedor(self, atual=None):
        if not self._listar(self.fornecedores, 'fornecedor'):
            raise ValueError('Cadastre um fornecedor antes de cadastrar produtos.')
        while True:
            ident = self.entrada.inteiro('ID do fornecedor', minimo=1, maximo=10**38-1,
                atual=atual.get_id_fornecedor() if atual else None)
            fornecedor = self.fornecedores.buscar_por_id(ident)
            if fornecedor is not None:
                return fornecedor
            self.saida('Fornecedor não encontrado. Escolha um ID da listagem.')

    def _ler_fornecedor(self, atual=None):
        campos = [('nome',100,True), ('cnpj',18,True), ('telefone',20,False),
                  ('email',100,False), ('logradouro',100,True), ('numero',10,True),
                  ('complemento',50,False), ('bairro',60,True), ('cidade',60,True),
                  ('estado',2,True), ('cep',9,True)]
        dados = {}
        for campo, tamanho, obrigatorio in campos:
            valor_atual = getattr(atual, 'get_' + campo)() if atual else None
            rotulo = campo + (' (atual: ' + str(valor_atual) + ')' if atual else '')
            dados[campo] = self.entrada.texto(rotulo, tamanho, obrigatorio,
                                            atual=valor_atual, edicao=atual is not None)
        dados['estado'] = dados['estado'].upper()
        if atual is not None:
            dados['id_fornecedor'] = atual.get_id_fornecedor()
        return Fornecedor(**dados)

    def _ler_produto(self, atual=None):
        fornecedor = self._escolher_fornecedor(atual.get_fornecedor() if atual else None)
        nome = self.entrada.texto('Nome',100,atual=atual.get_nome() if atual else None,edicao=atual is not None)
        descricao = self.entrada.texto('Descrição',200,False,
            atual=atual.get_descricao() if atual else None,edicao=atual is not None)
        preco = self.entrada.preco(atual.get_preco() if atual else None)
        quantidade = self.entrada.inteiro('Quantidade',atual=atual.get_quantidade() if atual else None)
        return Produto(nome,preco,quantidade,fornecedor,
                       id_produto=atual.get_id_produto() if atual else None,descricao=descricao)

    def manter(self, acao):
        while True:
            self.saida('\n' + acao.upper() + menu_estoque.MENU_ENTIDADES)
            opcao = self.entrada.ler('Entidade: ').strip()
            if opcao == '0':
                return
            if opcao not in ('1', '2'):
                self.saida('Opção inválida.')
                continue
            entidade = 'fornecedor' if opcao == '1' else 'produto'
            ctrl = self.fornecedores if opcao == '1' else self.produtos
            leitor = self._ler_fornecedor if opcao == '1' else self._ler_produto
            try:
                if acao == 'inserir':
                    objeto = leitor()
                    ctrl.inserir(objeto)
                    self.saida('Registro inserido: ' + objeto.to_string())
                else:
                    if not self._listar(ctrl, entidade):
                        continue
                    ident = self.entrada.inteiro('ID do registro',minimo=1,maximo=10**38-1)
                    objeto = ctrl.buscar_por_id(ident)
                    if objeto is None:
                        self.saida('Registro não encontrado.')
                        continue
                    self.saida(objeto.to_string())
                    if acao == 'excluir':
                        if not self.entrada.confirmar('Confirma a exclusão deste registro?'):
                            return
                        ctrl.excluir(ident)
                        self.saida('Registro excluído.')
                    else:
                        atualizado = leitor(objeto)
                        ctrl.atualizar(atualizado)
                        self.saida('Registro atualizado: ' + ctrl.buscar_por_id(ident).to_string())
            except Exception as erro:
                self.saida('Não foi possível concluir: ' + str(erro))
            if not self.entrada.confirmar('Deseja realizar outra operação de ' + acao + '?'):
                return

    def reports(self):
        while True:
            self.saida(menu_estoque.MENU_RELATORIOS)
            opcao = self.entrada.ler('Relatório: ').strip()
            if opcao == '0':
                return
            if opcao not in ('1', '2', '3'):
                self.saida('Opção inválida.')
                continue
            try:
                nome = {'1':'resumo','2':'produtos','3':'baixo'}[opcao]
                limite = self.entrada.inteiro('Estoque máximo para o alerta') if opcao == '3' else 5
                colunas,linhas = self.relatorios.consultar(nome,limite)
                self.saida(' | '.join(colunas))
                for linha in linhas:
                    self.saida(' | '.join('' if valor is None else str(valor) for valor in linha))
                self.saida(str(len(linhas)) + ' linha(s) no relatório.')
            except Exception as erro:
                self.saida('Não foi possível gerar o relatório: ' + str(erro))


def main():
    import os
    from getpass import getpass
    try:
        # Solicita credenciais uma vez. Elas não são gravadas em arquivo.
        if not os.environ.get('ORACLE_USER'):
            os.environ['ORACLE_USER'] = input('Usuário Oracle: ').strip()
        if not os.environ.get('ORACLE_DSN'):
            os.environ['ORACLE_DSN'] = input('DSN Oracle (servidor:porta/serviço): ').strip()
        if not os.environ.get('ORACLE_PASSWORD'):
            os.environ['ORACLE_PASSWORD'] = getpass('Senha Oracle: ')
        Aplicacao().executar()
        return 0
    except (KeyboardInterrupt, EOFError):
        print('\nOperação interrompida. Sistema encerrado.')
        return 0
    except Exception as erro:
        print('Falha ao iniciar. Confira a conexão Oracle e a criação das tabelas.')
        print(str(erro))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
