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
from pathlib import Path

__author__ = """\n""".join(['Marcelo G Facioli (mgfacioli@yahoo.com.br)'])
__version__ = "3.0.4"


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
            data_inicio - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx";
                a data inicial do periodo desejado (inclusive).

            data_fim - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx";
                a data final do periodo desejado (exclusive).

            num_dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao
                argumento Data_Fim.

            path_arquivo - (OPCIONAL/OBRIGATORIO) - seu uso é opcional para as opções 1 e 2 e obrigatório para a opção 3
            (nesta opção, o arquivo contendo os feriados será necessário para a correta execucão da funcão. Portanto,
            quando path_arquivo for obrigatório, será a cadeia de caracteres(string) representando o caminho (path)
            para o arquivo tipo csv contendo os feriados nacionais, no formato (c:\\foo\\arquivo.csv).
            O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data,
            dia_da_semana e descricão do feriado - dar preferencia para o arquivo da 'Anbima'
            (site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx')
            o qual vem no formato xls (Excel) e que pode ser facilmente convertido para o formato csv, a partir do menu
             "Salvar como" e escolhendo-se como Tipo "CSV - separado por virgula" a partir do Excel.
            Apos a conversao, excluir o cabecalho (primeira linha) e informacoes adicionais (ultimas quatro ou cinco
            linhas) para o arquivo manter somente os dados que nos interessam - data, dia da semana e nomemclatura do
            feriado.

        Exemplos
        --------

            1- Criando variaveis auxiliares:

                >>> var_path= "C:\\foo\\feriados.csv"
                >>> dt_ini = "01/01/2013"
                >>> dt_fin = "28/02/2013"


            2- Criando um instancia da classe DatasFinanceiras:

                >>> import FinDt
                >>> periodo = FinDt.DatasFinanceiras(dt_ini, dt_fin, path_arquivo = var_path)


            3- Gerando uma lista de dias do periodo:
                - formato datetime.date(aaaa, mm, dd):

                    >>> periodo.dias()          # dias corridos
                    >>> periodo.dias(opt=2)     # sem sabados e domingos
                    >>> periodo.dias(2)         # sem sabados e domingos
                    >>> periodo.dias(opt=3)     # sem sabados, domingos e feriados
                    >>> periodo.dias(3)         # sem sabados, domingos e feriados
            ou
                - formato string 'dd/mm/aaaa'

                    >>> periodo.dias(1, 'str')      # dias corridos
                    >>> periodo.dias(2, 'str')      # sem sabados e domingos
                    >>> periodo.dias(3, 'str')      # sem sabados, domingos e feriados


            4- Obtendo um dicionário ordenado contendo todos os feriados do periodo:
                (key : value = data : feriado)

                >>> periodo.lista_feriados()        # formato datetime.date(aaaa, mm, dd)
            ou
                >>> periodo.lista_feriados('str')   # formato string 'dd/mm/aaaa'


            5- Obtendo o dia da semana em que determinada data ira cair (mesmo com tal data nao
                estando no periodo):

                    >>> periodo.dia_semana('03/04/2013')

                    Resultado: 'quarta-feira'


            6- Criando uma lista de todas terca-feiras do periodo:

                >>> periodo.lista_dia_especifico_semana(3)           # formato datetime.date(aaaa, mm, dd)
            ou
                >>> periodo.lista_dia_especifico_semana(3, 'str')   # formato string 'dd/mm/aaaa'


            7- Obtendo o primeiro ou o último dia de determinado mês:
                >>> periodo.primeiro_dia_mes('23/02/2015')  # formato datetime.date(aaaa, mm, dd)
            ou
                >>> periodo.ultimo_dia_mes('23/02/2015', 'str')  # formato string 'dd/mm/aaaa'


            8- Gerando uma lista que representa um subperiodo de dias de DatasFinanceiras:

                >>> periodo.subperiodo('15/01/2013', '15/02/2013')

            9- Obtendo um dicionario ordenado 'Mes/Ano':
                (key : value = (Mes/Ano) : (dias uteis por mes))

               >>> periodo.dias_uteis_por_mes()
    """

    def __init__(self, data_inicio=None, data_fim=None, num_dias=None, path_arquivo=''):
        super().__init__()
        if data_inicio is None:
            raise ValueError('A Data Inicial e imprescindivel!!!')
        else:
            self._cData_Inicio = FormataData(data_inicio).str_para_data()

            if data_fim is None and num_dias is None:
                raise ValueError("Uma data final ou número de dias tem que ser fornecido!")
            else:
                if data_fim is not None:
                    self._cData_Fim = FormataData(data_fim).str_para_data()
                    self._ListaDatas = [self._cData_Inicio + timedelta(x)
                                        for x in range(0, abs(int((self._cData_Fim - self._cData_Inicio).days) + 1))]
                elif num_dias is not None:
                    self._cNum_Dias = num_dias
                    if self._cNum_Dias >= 1:
                        self._ListaDatas = [self._cData_Inicio + timedelta(x) for x in range(0, abs(self._cNum_Dias))]
                    else:
                        self._ListaDatas = [
                            (self._cData_Inicio - timedelta(days=abs(self._cNum_Dias) - 1) + timedelta(x))
                            for x in range(0, abs(self._cNum_Dias))]
                    self._cData_Fim = self._ListaDatas[-1]
        self._cPath_Arquivo = Path(path_arquivo)

    def dias(self, opt=1, dt_type='date'):
        """
        Cria uma lista de Dias entre uma data inicial e uma data final.

        Parametros
        ----------
            opt - (OPICIONAL) Permite selecionar entre 3 opcoes para gerar a lista de dias:
                Opcao 1: gera uma lista de dias corridos (incluindo sabados, domingos e feriados).
                Opcao 2: gera uma lista de dias excluindo sabados e domingos.
                Opcao 3: gera uma lista de dias excluindo sabados e domingos e feriados.

            dt_type - (OPICIONAL) Permite determinar o tipo de dados que será retornado:
                Opção date: retorna datas no formato datetime.date(aaaa, mm, dd) do python
                Opção str:  retorna datas no formato string "dd/mm/aaaa"
        """

        if dt_type == 'date':
            if opt == 1:
                return [dia for dia in self._ListaDatas]
            elif opt == 2:
                return [dia for dia in self._ListaDatas if
                        (dia.isoweekday() != 6 and dia.isoweekday() != 7)]
            elif opt == 3:
                if self._cPath_Arquivo is None:
                    raise ValueError('E necessario um path/arquivo!')
                else:
                    return [dia for dia in self.dias(opt=2) if
                            dia not in self.lista_feriados()]
        elif dt_type == 'str':
            return [FormataData(dia).data_para_str() for dia in self.dias(opt, dt_type='date')]

    def lista_feriados(self, dt_type='date'):
        """
        Cria um Dicionario ou uma Lista com os feriados entre a Data Inicial e a Data Final.

        Parametros
        ----------
            opt - (OPICIONAL) Permite selecionar entre 2 opcoes para gerar a lista de dias:
                Opcao 1: gera uma lista de dias corridos (incluindo sabados, domingos e feriados).
                Opcao 2: gera uma lista de dias excluindo sabados e domingos.
                Opcao 3: gera uma lista de dias excluindo sabados e domingos e feriados.

            dt_type - (OPICIONAL) Permite determinar o tipo de dados que será retornado:
                Opção date: retorna datas no formato datetime.date(aaaa, mm, dd) do python
                Opção str:  retorna datas no formato string "dd/mm/aaaa"
        """
        try:
            with open(self._cPath_Arquivo, 'r', encoding="ISO-8859-1") as csvfile:
                feriados = csv.reader(csvfile, dialect='excel', delimiter=';')
                dic_selic = {FormataData(row[0]).str_para_data(): row[2] for row in feriados}

            if dt_type == 'date':
                return OrderedDict(sorted({dt: dic_selic[dt] for dt in self._ListaDatas if
                                           dt in dic_selic}.items(), key=lambda t: t[0]))
            elif dt_type == 'str':
                return OrderedDict(sorted({FormataData(dt).data_para_str(): dic_selic[dt] for dt in self._ListaDatas if
                                           dt in dic_selic}.items(), key=lambda t: t[0]))
        except IOError as IOerr:
            print("Erro de leitura do arquivo:" + str(IOerr))
        except KeyError as Kerr:
            print("Erro na chave do Dicionario" + str(Kerr))

    def lista_dia_especifico_semana(self, dia_da_semana=1, dt_type='date'):
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

            dt_type - (OPICIONAL) Permite determinar o tipo de dados que será retornado:
                Opção date: retorna datas no formato datetime.date(aaaa, mm, dd) do python
                Opção str:  retorna datas no formato string "dd/mm/aaaa"
        """
        if dt_type == 'date':
            return [dia for dia in self._ListaDatas if dia.isoweekday() == dia_da_semana]
        elif dt_type == 'str':
            return [FormataData(dia).data_para_str() for dia in self._ListaDatas if dia.isoweekday() == dia_da_semana]

    @staticmethod
    def dia_semana(data):
        """
        Obtem o dia da semana a partir de uma data no formato String

        Parametros
            data - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
        """
        return FormataData(data).str_para_data().strftime("%A")

    @staticmethod
    def primeiro_dia_mes(data, dt_type='date'):
        """
        Fornecida uma data qualquer no formato string, retorna o primeiro dia do mes daquela data, tambem
            no formato string.

        Parametros
        ----------
            data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).

            dt_type - (OPICIONAL) Permite determinar o tipo de dados que será retornado:
                Opção date: retorna datas no formato datetime.date(aaaa, mm, dd) do python
                Opção str:  retorna datas no formato string "dd/mm/aaaa"
        """
        if dt_type == 'date':
            return FormataData(FormataData(data).str_para_data().strftime("01/%m/%Y")).str_para_data()
        elif dt_type == 'str':
            return FormataData(data).str_para_data().strftime("01/%m/%Y")

    @staticmethod
    def ultimo_dia_mes(data, dt_type='date'):
        """
        Fornecida uma data qualquer no formato string, retorna o ultimo dia do mes daquela data, tambem
            no formato string.

        Parametros
        ----------
            data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).

            dt_type - (OPICIONAL) Permite determinar o tipo de dados que será retornado:
                Opção date: retorna datas no formato datetime.date(aaaa, mm, dd) do python
                Opção str:  retorna datas no formato string "dd/mm/aaaa"
        """
        data_seguinte = FormataData(data).str_para_data()
        while data_seguinte.month == FormataData(data).str_para_data().month:
            data_seguinte = date.fromordinal(data_seguinte.toordinal() + 1)
        if dt_type == 'date':
            return date.fromordinal(data_seguinte.toordinal() - 1)
        elif dt_type == 'str':
            return FormataData(date.fromordinal(data_seguinte.toordinal() - 1)).data_para_str()

    def dias_uteis_por_mes(self):
        """
        Cria um dicionario contendo o numero de dias uteis (sem sabados, domingos e feriados) mensais entre uma
        data inicial e uma data final.

        """

        lista_mes_dias_uteis = []

        for dia in self._ListaDatas:
            if dia == self.ultimo_dia_mes(dia):
                if self.primeiro_dia_mes(dia) < self._cData_Inicio:
                    dias_uteis_do_mes = DatasFinanceiras(self._cData_Inicio, self.ultimo_dia_mes(dia, 'str'),
                                                         path_arquivo=self._cPath_Arquivo)
                    lista_mes_dias_uteis.append(
                        ("{}".format(dia.strftime("%m/%Y")), len(dias_uteis_do_mes.dias(opt=3))))
                else:
                    dias_uteis_do_mes = DatasFinanceiras(self.primeiro_dia_mes(dia, 'str'),
                            self.ultimo_dia_mes(dia, 'str'), path_arquivo=self._cPath_Arquivo)
                    lista_mes_dias_uteis.append(
                        ("{}".format(dia.strftime("%m/%Y")), len(dias_uteis_do_mes.dias(opt=3))))
            elif dia == self._cData_Fim:
                dias_uteis_do_mes = DatasFinanceiras(self.primeiro_dia_mes(dia, 'str'), self._cData_Fim,
                                                     path_arquivo=self._cPath_Arquivo)
                lista_mes_dias_uteis.append(
                    ("{}".format(dia.strftime("%m/%Y")), len(dias_uteis_do_mes.dias(opt=3))))

        return OrderedDict(sorted({per[0]: per[1] for per in lista_mes_dias_uteis}.items(), key=lambda t: t[0]))

    def subperiodo(self, data_inicio=None, data_fim=None, num_dias=1, dt_type='date'):
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
            data_inicio - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx";
                a data inicial do periodo desejado (inclusive).

            data_fim - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx";
                a data final do periodo desejado (exclusive).

            num_dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao
                argumento Data_Fim.

            dt_type - (OPICIONAL) Permite determinar o tipo de dados que será retornado:
                Opção date: retorna datas no formato datetime.date(aaaa, mm, dd) do python
                Opção str:  retorna datas no formato string "dd/mm/aaaa"

        """
        if data_inicio is None or data_fim is None:
            subper = DatasFinanceiras(self._cData_Inicio, self._cData_Fim, self._cNum_Dias,
                                      path_arquivo=self._cPath_Arquivo)
            return subper.dias(1, dt_type)
        else:
            if FormataData(data_inicio).str_para_data() in self._ListaDatas:
                print("")
                if FormataData(data_fim).str_para_data() in self._ListaDatas:
                    subper = DatasFinanceiras(data_inicio, data_fim, path_arquivo=self._cPath_Arquivo)
                    return subper.dias(1, dt_type)
                else:
                    raise ValueError("Data Final do subperiodo fora do conjunto de dias do periodo principal!")
            else:
                raise ValueError("Data Inicial do subperiodo fora do conjunto de dias do periodo principal!")


def main():
    pass


if __name__ == '__main__':
    main()