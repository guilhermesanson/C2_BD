from decimal import Decimal, InvalidOperation


class Entrada:
    def __init__(self, leitor=input, saida=print):
        self.ler = leitor
        self.saida = saida

    def texto(self, rotulo, tamanho, obrigatorio=True, atual=None, edicao=False):
        while True:
            dica = ' [Enter mantém; - limpa opcional]' if edicao else ''
            valor = self.ler(rotulo + dica + ': ').strip()
            if edicao and valor == '':
                return atual
            if not obrigatorio and valor in ('', '-'):
                return None
            if valor and len(valor) <= tamanho:
                return valor
            self.saida('Informe um texto de 1 a ' + str(tamanho) + ' caracteres.')

    def inteiro(self, rotulo, minimo=0, maximo=9999999999, atual=None):
        while True:
            valor = self.ler(rotulo + (' [Enter mantém]' if atual is not None else '') + ': ').strip()
            if valor == '' and atual is not None:
                return atual
            try:
                numero = int(valor)
                if minimo <= numero <= maximo:
                    return numero
            except ValueError:
                pass
            self.saida('Informe um inteiro entre ' + str(minimo) + ' e ' + str(maximo) + '.')

    def preco(self, atual=None):
        while True:
            valor = self.ler('Preço unitário' + (' [Enter mantém]' if atual is not None else '') + ': ').strip()
            if valor == '' and atual is not None:
                return atual
            try:
                numero = Decimal(valor.replace(',', '.'))
                if numero.is_finite() and Decimal('0') <= numero <= Decimal('99999999.99'):
                    if numero == numero.quantize(Decimal('0.01')):
                        return numero
            except (InvalidOperation, ValueError):
                pass
            self.saida('Informe um preço não negativo com até duas casas decimais, sem separador de milhar.')

    def confirmar(self, mensagem):
        while True:
            valor = self.ler(mensagem + ' [s/n]: ').strip().lower()
            if valor in ('s', 'sim'):
                return True
            if valor in ('n', 'não', 'nao'):
                return False
            self.saida('Responda s ou n.')
