from .menu_estoque import NOME_SISTEMA, INTEGRANTES, PROFESSOR, DISCIPLINA, SEMESTRE


class SplashScreen:
    def exibir(self, relatorios, saida=print):
        saida('=' * 65)
        saida(NOME_SISTEMA)
        saida('Integrantes: ' + ' | '.join(INTEGRANTES))
        saida('Professor: ' + PROFESSOR)
        saida('Disciplina: ' + DISCIPLINA + ' | Semestre: ' + SEMESTRE)
        for entidade, quantidade in relatorios.contagens().items():
            situacao = 'possui registros' if quantidade else 'sem registros'
            saida(entidade + ': ' + str(quantidade) + ' registro(s) - ' + situacao)
        saida('=' * 65)
