# -*- coding: UTF-8 -*-

r"""Classe base de suporte para operacoes com datas.

1)Objetivo:
-----------
    Esta classe fornece um conjunto de funcoes cujo principal objetivo e
    facilitar o trabalho com datas, voltadas, principalmente, para as financas:
    dias uteis, dias corridos, numero de dias uteis entre duas datas, numero de
    dias corridos entre duas datas.
"""

import csv
import re
import locale

locale.setlocale(locale.LC_ALL, '')
from datetime import date, timedelta
from collections import OrderedDict

__author__ = """\n""".join(['Marcelo G Facioli (mgfacioli@yahoo.com.br)'])
__version__ = "3.0.0"


class FormataData(object):
    """
    FormataData é uma classe auxiliar à classe FinDt e que forncede métodos para transformar datas no formato 'string'
    para o formato 'date' do Python e vice-versa. Quando fornecida uma data no formato 'string', transforma o separador
    de data de diversos formatos (/, :, - ou espaço em branco) no separador padrao "/", antes de convertê-la no formato
    date.

    Parametros
    ----------
        Data - cadeia de caracteres (string) que representa uma data que pode ser de diversos formatos:
             "xx/xx/xxxx"
             "xx:xx:xxxx"
             "xx-xx-xxxx"
             "xx xx xxxx"
    """

    def __init__(self, data=None):
        self._data = data

    def normaliza_data(self):
        """

        Converte o separador de data de diversos formatos no separador padrao "/".

        """
        if self._data is not None:
            try:
                data_mask = re.compile(r'^(\d{2})\D*(\d{2})\D*(\d{4})$')
                partes = data_mask.search(self._data).groups()
                return "{}/{}/{}".format(partes[0], partes[1], partes[2])
            except AttributeError as AttErr:
                print("Separador Indefinido: {}".format(str(AttErr)))
                return
            except TypeError as TyErr:
                print("O parametro deve ser uma string: {}".format(str(TyErr)))
                return
        else:
            return None

    def str_para_data(self):
        """

        Transforma uma Data do formato String para formato Date

        """

        if self._data is not None:
            if type(self._data) is date:
                return self._data
            elif type(self._data) is str:
                partes = self.normaliza_data().split("/")
                return date(int(partes[2]), int(partes[1]), int(partes[0]))
        else:
            return None

    def data_para_str(self):
        """
        Transforma uma Data no formato Date para formato String.

        """

        if self._data is not None:
            if type(self._data) is str:
                self._data = self.normaliza_data()
                return self._data
            elif type(self._data) is date:
                return self._data.strftime("%d/%m/%Y")
        else:
            return None


class DatasFinanceiras(FormataData):
    """
        Classe base de suporte para operacoes com datas.

        Parametros
        ----------
            Data_Inicio - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx";
                a data inicial do periodo desejado (inclusive).

            Data_Fim - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx";
                a data final do periodo desejado (exclusive).

            Num_Dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao
                argumento Data_Fim.

            Path_Arquivo - (OPCIONAL/OBRIGATORIO) - seu uso e opcional para as opcoes 1 e 2 e obrigatorio para a opcao 3
            (nesta opcao, o arquivo contendo os feriados sera necessario para a correta execucao da funcao. Portanto,
            quando cPath_Arquivo for obrigatorio, sera a cadeia de caracteres(string) representando o caminho (path)
            para o arquivo tipo csv contendo os feriados nacionais, no formato (c:\\foo).
            O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data,
            dia_da_semana e descricao do feriado - dar preferencia para o arquivo da 'Anbima'
            (site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx')
            o qual vem no formato xls (Excel) e que pode ser facilmente convertido para o formato csv, a partir do menu
             "Salvar como" e escolhendo-se como Tipo "CSV - separado por virgula" a partir do Excel.
            Apos a conversao, excluir o cabecalho (primeira linha) e informacoes adicionais (ultimas quatro ou cinco
            linhas) para o arquivo manter somente os dados que nos interessam - data, dia da semana e nomemclatura do
            feriado.

        Exemplos
        --------
            1)
                Criando variaveis auxiliares:

                    >>> varPath= "C:\\foo\\feriados.csv"
                    >>> dtIni = "01/01/2013"
                    >>> dtFin = "28/02/2013"

                Criando um instancia da classe DatasFinanceiras:

                    >>> a = DatasFinanceiras(dtIni, dtFin, Path_Arquivo=varPath)

                Gerando uma lista de dias da data inicial ate final:

                    >>> a.Dias()

                Gerando uma lista de dias sem sabados e domingos da data inicial ate final:

                    >>> a.Dias(Opt=2)

                Gerando uma lista de dias sem sabados, domingos e feriados da data inicial ate final:

                    >>> a.Dias(Opt=3)

                                Obtendo um dicionario ordenado 'Mes/Ano':(Dias Uteis por Mes)

                                        >>> a.DiasUteisPorMes()

                                Criando uma lista de todas terca-feiras entre dtIni e dtFim:

                                        >>> a.ListaDiaEspecificoSemana(3)

                                Obtendo o dia da semana em que determinada data ira cair (mesmo com tal data nao
                                    estando entre dtIni e dtFim):

                                        >>> a.DiaSemana('03/04/2013')

                                        Resultado: 'quarta-feira'

                Gerando uma lista que representa um subperiodo de dias de DatasFinanceiras:

                    >>> a.subperiodo('15/01/2013', '15/02/2013')

    """

    def __init__(self, data_inicio=None, data_fim=None, num_dias=None, opt=1, path_arquivo=''):
        super().__init__()
        if data_inicio is None:
            raise ValueError('A Data Inicial e imprescindivel!!!')
        else:
            self._cData_Inicio = FormataData(data_inicio).str_para_data()
        if data_fim is None and num_dias is None:
            raise ValueError("Uma data final ou número de dias tem que ser fornecido!")
        else:
            self._cData_Fim = FormataData(data_fim).str_para_data()
            self._cNum_Dias = num_dias
        self._cPath_Arquivo = path_arquivo
        self._ListaDatas = []

    @staticmethod
    def __lista_dias(a, b, c):
        """
        Este método permite gerar todas as datas contidas no periodo selecionado, dia a dia.
        :rtype : list
        """
        return [FormataData(a + timedelta(x)).str_para_data() for x in range(b, abs(c))]

    def dias(self, opt=1):
        """
        Cria uma lista de Dias entre uma data inicial e uma data final.

        Parametros
        ----------
            Opt - (OPICIONAL) Permite selecionar entre 3 opcoes para gerar a lista de dias:
                Opcao 1: gera uma lista de dias corridos (incluindo sabados, domingos e feriados).
                Opcao 2: gera uma lista de dias excluindo sabados e domingos.
                Opcao 3: gera uma lista de dias excluindo sabados e domingos e feriados.
        """

        if self._cData_Fim is not None:
            self._ListaDatas = self.__lista_dias(self._cData_Inicio, 0,
                                                 int((self._cData_Fim - self._cData_Inicio).days) + 1)
        else:
            if self._cNum_Dias >= 1:
                self._ListaDatas = self.__lista_dias(self._cData_Inicio, 0, self._cNum_Dias)
            else:
                self._ListaDatas = self.__lista_dias(self._cData_Inicio - timedelta(days=abs(self._cNum_Dias) - 1),
                                                     0, self._cNum_Dias)

        if opt == 1:
            return [FormataData(dia).data_para_str() for dia in self._ListaDatas]
        elif opt == 2:
            return [FormataData(dia).data_para_str() for dia in self._ListaDatas if
                    (dia.isoweekday() != 6 and dia.isoweekday() != 7)]
        elif opt == 3:
            if self._cPath_Arquivo is None:
                raise ValueError('E necessario um path/arquivo!')
            else:
                if self._cData_Fim is None and self._cNum_Dias >= 1:
                    self._cData_Fim = self._ListaDatas[-1]
                return [dia for dia in self.dias(opt=2) if
                        FormataData(dia).data_para_str() not in self.lista_feriados()]

    def lista_feriados(self):
        """
        Cria um Dicionario com os feriados entre a Data Inicial e a Data Final.

        """
        try:
            with open(self._cPath_Arquivo, 'rU') as csvfile:
                feriados = csv.reader(csvfile, dialect='excel', delimiter=';')
                dic_selic = {FormataData(row[0]).str_para_data(): row[2] for row in feriados}

            return OrderedDict(sorted({FormataData(dt).data_para_str(): dic_selic[dt] for dt in self._ListaDatas if
                                       dt in dic_selic}.items(), key=lambda t: t[0]))

        except IOError as IOerr:
            print("Erro de leitura do arquivo:" + str(IOerr))
        except KeyError as Kerr:
            print("Erro na chave do Dicionario" + str(Kerr))

    def lista_dia_especifico_semana(self, dia_da_semana=1):
        """
        Cria uma Lista com os dias em que um determinado dia da semana se repete entre a Data Inicial e a Data Final.

        Parametros
        ----------
            dia_da_semana - (OPICIONAL) numero inteiro que representa o dia da semana desejado, conforme tabela:
                Segunda-Feira = 1
                Terca-Feira = 2
                Quarta-Feira = 3
                Quinta-Feira = 4
                Sexta-Feira = 5
                Sabado = 6
                Domingo = 7
        """
        return [FormataData(dia).data_para_str() for dia in self._ListaDatas if dia.isoweekday() == dia_da_semana]

    @staticmethod
    def dia_semana(data):
        """
        Obtem o dia da semana a partir de uma data no formato String

        Parametros
            Data - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
        """
        return FormataData(data).str_para_data().strftime("%A")

    @staticmethod
    def primeiro_dia_mes(data):
        """
        Fornecida uma data qualquer no formato string, retorna o primeiro dia do mes daquela data, tambem
            no formato string.

        Parametros
        ----------
            Data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).
        """
        return FormataData(data).str_para_data().strftime("01/%m/%Y")

    @staticmethod
    def ultimo_dia_mes(data):
        """
        Fornecida uma data qualquer no formato string, retorna o ultimo dia do mes daquela data, tambem
            no formato string.

        Parametros
        ----------
            Data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).
        """

        data_seguinte = FormataData(data).str_para_data()
        while data_seguinte.month == FormataData(data).str_para_data().month:
            data_seguinte = date.fromordinal(data_seguinte.toordinal() + 1)

        return FormataData(date.fromordinal(data_seguinte.toordinal() - 1)).data_para_str()

    def dias_uteis_por_mes(self):
        """
        Cria um dicionario contendo o numero de dias uteis (sem sabados, domingos e feriados) mensais entre uma
        data inicial e uma data final.

        """

        lista_mes_dias_uteis = []

        for dia in self._ListaDatas:
            if FormataData(dia).data_para_str() == self.ultimo_dia_mes(dia):
                dias_uteis_do_mes = DatasFinanceiras(self.primeiro_dia_mes(dia), self.ultimo_dia_mes(dia), opt=3,
                            path_arquivo=self._cPath_Arquivo)
                lista_mes_dias_uteis.append(
                    ("{}".format(dia.strftime("%m/%Y")), len(dias_uteis_do_mes.dias(opt=3))))

        return OrderedDict(sorted({per[0]: per[1] for per in lista_mes_dias_uteis}.items(), key=lambda t: t[0]))

    def subperiodo(self, data_inicio=None, data_fim=None, num_dias=1, opt=1):
        """

        Cria uma lista contendo um subperiodo de dias do periodo principal.
        subperiodo é um subconjunto de dias do periodo principal.

        Restrições
        ----------
        A Data Inicial do subperiodo tem que ser maior ou igual a Data Inicial do Periodo Principal.
        A Data Final do subperiodo tem que ser menor ou igual a Data Final do Periodo Principal.
        Se Data Inicial e/ou Data Final estiverem fora dos limites do Periodo Principal, um ValueError será gerado.
        Se uma Data Inicial e uma Data Final não forem especificados, subperiodo será igual ao
        Período Principal (DatasFinanceiras).

        Parametros
        ----------
        Os mesmos da Classe DatasFinanceiras.
        """
        if data_inicio is None or data_fim is None:
            subper = DatasFinanceiras(self._cData_Inicio, self._cData_Fim, self._cNum_Dias, opt,
                                      path_arquivo=self._cPath_Arquivo)
            return subper.dias(opt)
        else:
            if data_inicio in self.dias() or data_fim in self.dias():
                subper = DatasFinanceiras(data_inicio, data_fim, num_dias, opt, path_arquivo=self._cPath_Arquivo)
                return subper.dias(opt)
            else:
                raise ValueError('Subperiodo fora da range do periodo!')
                pass


def main():
    pass


if __name__ == '__main__':
    main()