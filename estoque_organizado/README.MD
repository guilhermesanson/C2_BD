# Sistema de Controle de Estoque

Trabalho de Banco de Dados, semestre 2026/2, professor Howard Roatti.


## Situação da implementação

Aplicação de console em Python, com persistência Oracle e SQL montado em variáveis de texto por concatenação dos atributos. Não utiliza ORM. O projeto inclui as duas entidades relacionadas, CRUD, contagens na inicialização e relatórios.

Os testes locais foram executados no Windows com Python: verificam controladoras com mocks, fluxos de menu e cálculos dos relatórios em uma base SQLite usada exclusivamente no teste.
 

## Requisitos

- Python 3.10 ou superior com `pip` e `venv`.
- Banco Oracle acessível e um usuário de testes com permissão para criar as duas tabelas.
- Ambiente com suporte ao driver `python-oracledb` e às colunas `IDENTITY` do DDL.
- Dados de conexão do ambiente da disciplina: usuário, senha e DSN (`servidor:porta/serviço`).

## Execução no Linux

Todos os comandos abaixo devem ser executados na raiz do projeto, onde está este README.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dependencias.txt
```

Conecte ao esquema Oracle de testes pelo SQL Developer ou outra ferramenta e execute `banco_de_dados/estrutura_estoque.sql`. A ordem é FORNECEDOR e depois PRODUTO. Execute o DDL apenas uma vez em um esquema sem essas tabelas; o script não remove tabelas existentes.

Defina seu usuário e o DSN real do banco:

```bash
export ORACLE_USER='seu_usuario'
export ORACLE_DSN='servidor:1521/servico'
python executar_estoque.py
```

O programa solicita a senha sem exibi-la. Se usuário ou DSN não estiverem definidos, também serão solicitados. A senha não é gravada em arquivo. Não publique credenciais no GitHub.

Alternativa equivalente: `python -m estoque_app.navegacao_terminal`. Não execute diretamente `python estoque_app/navegacao_terminal.py`, pois os imports dessa versão usam o pacote `estoque_app`.

O exemplo da disciplina possui configurações próprias para sua VM. Confirme o DSN e a compatibilidade do driver nesse ambiente. Se a conexão falhar, guarde a mensagem de erro para diagnóstico; não considere os testes concluídos.

## Utilização

1. A tela inicial exibe o sistema, os dois integrantes, professor, disciplina e semestre. Duas consultas `COUNT(1)` informam quantos fornecedores e produtos existem.
2. **Relatórios:** escolha o resumo agrupado por fornecedor, os produtos com fornecedores ou o alerta de estoque baixo. No terceiro, informe a quantidade máxima. O submenu se repete até escolher 0.
3. **Inserir:** escolha Fornecedor ou Produto. Informe os campos. Campos opcionais podem ficar vazios; IDs são gerados pelo Oracle. Cadastre o fornecedor antes do produto. Na associação, selecione o ID de um fornecedor listado. Ao fim, responda se deseja inserir outro registro.
4. **Remover:** escolha a entidade, veja IDs e nomes, selecione o registro e confirme. Um fornecedor com produtos vinculados é bloqueado; remova ou reassocie os produtos antes. Não há exclusão em cascata. Uma confirmação negativa retorna ao menu principal.
5. **Atualizar:** escolha a entidade e o ID listado. Preencha os campos ou pressione Enter para manter o valor atual; digite `-` para limpar um campo opcional. A chave primária é preservada. O registro atualizado é exibido e o programa pergunta se deseja continuar.
6. **Sair:** escolha 0 no menu principal. Nos submenus, 0 volta ao menu principal.

Preço aceita ponto ou vírgula decimal, sem separador de milhar, com no máximo duas casas. Quantidade deve ser inteira e não negativa. CNPJ é armazenado como informado e deve ser único no banco; não há validação de dígitos verificadores nem normalização de formatos.

## Relatórios

| Arquivo em `estoque_app/consultas_sql` | Resultado |
|---|---|
| `saldo_por_fornecedor.sql` | COUNT de produtos, SUM de unidades e SUM de preço × quantidade, com GROUP BY por fornecedor. Inclui fornecedor sem produtos. |
| `catalogo_com_fornecedores.sql` | JOIN entre produtos e fornecedores, com identificadores, preço, quantidade e CNPJ. |
| `alerta_reposicao.sql` | JOIN com filtro de quantidade máxima montado pela classe Relatorios. |

O sistema registra o estoque atual. Não há tabela de compras ou histórico de movimentações; portanto, não apresenta a quantidade historicamente comprada como se fosse calculada a partir do saldo atual.


```text
executar_estoque.py        entrada do programa
conferir_banco_oracle.py   execução da integração no Oracle
dependencias.txt          bibliotecas para conexão ao banco
estoque_app/
  navegacao_terminal.py   classe Aplicacao e fluxo dos menus
  entidades/             Fornecedor e Produto
  persistencia/          CRUD, conexão e transações
  consultas/             leitura e execução dos relatórios
  consultas_sql/         consultas SQL dos relatórios
  interface/             menus, integrantes e leitura de dados
banco_de_dados/           criação das tabelas
modelos/                  diagrama Mermaid e PDF
verificacoes/             testes locais e integração Oracle
guias/                    instruções, entrega e mapa de arquivos
PROMPTS.md                registro da assistência de IA
.github/workflows/        testes locais no GitHub Actions
```

Produto armazena uma instância de `Fornecedor`. Somente ao montar SQL a controladora obtém o ID do fornecedor. As consultas de produto reconstroem a associação via JOIN.

As controladoras herdam operações comuns de `ControllerBase`. Cada operação abre uma conexão antes de executar comandos. Escritas confirmam com commit e falhas realizam rollback; conexão e cursor são fechados. Atualizações e exclusões verificam existência com `SELECT FOR UPDATE`. A PK, a UK de CNPJ, os CHECKs e a FK do Oracle são a garantia final de integridade, inclusive em concorrência.

As queries são montadas em uma variável `sql` e executadas com `cursor.execute(sql)`. Valores textuais passam por `literal()`, que duplica apóstrofos e trata `None` como `NULL`; números são convertidos em literais numéricos. Não há ORM, query builder ou parâmetros de valores nas chamadas execute. IDs novos devem ser `None`; a aplicação recupera o IDENTITY inserido usando o ROWID retornado pelo cursor, na mesma transação.



