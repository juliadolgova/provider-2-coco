# -*- encoding: utf-8 -*-
import re
from datetime import datetime

from provdata import ProvData
from srcutils import split_fio, array_pad


class ProvDataText(ProvData):
    """
    класс - поддержка текстового реестра имеющего заголовочные строки в формате
    # Параметр: Значение параметра
    Строки начинающиеся с # - заголовочные либо коментарии
    """
    def __init__(self, filename=''):
        ProvData.__init__(self)
        # код услуги, определить в наследнике
        self._service_code = ''
        # исходный файл
        self.filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'
        # пример регулярного выражения, переопределить в наследнике при необходимости
        self._line_re = '(?P<abonent>.*);(?P<address>.*);(?P<account>.*);(?P<debt>.*);(?P<datefrom>.*);(?P<dateto>.*)'
        # формат датовых полей в исходном файле
        self._format_datetime = r'%d/%m/%Y'

        # Размер в байтах когда требуется проанализировать только начало файла (достаточное чтобы попали все заголовки)
        self._bufferPreAnalyze = 3000
        # количество строк для предварительного анализа (достаточное чтобы попали все заголовки)
        self._linesCountPreAnalyze = 100

        # дата, которую использовать, если в реестре нет даты. Тип datetime
        self.debt_date = None
        # разделитель дробной и целой части
        self.delimiter = '.'

    def _dict_re_to_dict_api(self, dict_re):
        dict_api = self._default_dict()
        dict_api['number'] = dict_re.get('account')
        dict_api['lastname'], dict_api['firstname'], dict_api['middlename'] = split_fio(dict_re.get('abonent'))

        splitted_address = array_pad(dict_re.get('address').strip().rsplit(',', 3), 4, '')
        dict_api['city'], dict_api['street'], dict_api['house'], dict_api['flat'] = splitted_address

        dict_api['service'] = self._service_code

        dateto = dict_re.get('dateto')
        if dateto:
            dict_api['period'] = datetime.strptime(dateto, self._format_datetime)
        else:
            if self.debt_date:
                dict_api['period'] = self.debt_date
            else:
                raise IOError('No date specified')

        debt = dict_re.get('debt')
        if self.delimiter != '.':
            debt = debt.replace(self.delimiter, '.')
        dict_api['debt'] = float(debt) if debt else 0
        return dict_api

    def _get_header_param_value(self, param_name):
        with open(self.filename, 'r') as f:
            source_lines = f.readlines(self._bufferPreAnalyze)[:self._linesCountPreAnalyze]

        for line in source_lines:
            m = re.match(r"#%(ParamName)s\s(.*)(;.*)?" % {'ParamName': param_name}, line)
            if m:
                return m.group(1).strip()
        return None

    def generate_accounts_decoded(self):
        self.error_count = 0
        line_num = 0

        with open(self.filename, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    line_decoded = line.decode(self._coding)
                    if line_decoded.startswith("#"):
                        continue
                    m = re.match(self._line_re, line_decoded)
                    if m:
                        yield self._dict_re_to_dict_api(m.groupdict())
                    else:
                        if __debug__:
                            print line_decoded
                except Exception as exception_instance:
                    if self.error_processor:
                        self.error_count += 1
                        self.error_processor(
                            file=self.filename,
                            at=line_num,
                            record=line,
                            exception=exception_instance
                        )
                    else:
                        raise

    def source_data_correct(self):
        return True


class Domremstroy(ProvDataText):
    def __init__(self, filename=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = '2834'
        self.delimiter = ','

        # Пример строки для поставщика:
        # 006589;Ломов Леонид Георгиевич 1-я Малая 1а 12;Чита,1-я Малая,1а,12;456,86
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}

        self._line_re = ';'.join([
            account_re,
            abonent_re,
            address_re,
            debt_re
        ])

    def _dict_re_to_dict_api(self, dict_re):
        dict_api = ProvDataText._dict_re_to_dict_api(self, dict_re)
        fio = array_pad(dict_re['abonent'].replace('.', ' ').split(), 3, '')[:3]
        dict_api['lastname'], dict_api['firstname'], dict_api['middlename'] = fio
        return dict_api


class Dom(ProvDataText):
    def __init__(self, filename='', service_code=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = service_code

        # Пример строки для поставщика:
        # Ипатов Роман Михайлович;ЧИТА,БОГОМЯГКОВА,65,62;9010747;;;;;01/11/2016;30/11/2016;31:0
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'
        # В регулярке предусмотрен год длинный и короткий,
        # но в обработке полученного значения (например _dict_re_to_dict_api) не предусмотрено
        date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}
        f5_re = r'(?P<f5>.*)'
        f6_re = r'(?P<f6>.*)'
        f7_re = r'(?P<f7>.*)'
        datefrom_re = r'(?P<datefrom>%(date_re)s)' % {'date_re': date_re}
        dateto_re = r'(?P<dateto>%(date_re)s)' % {'date_re': date_re}
        f10_re = r'(?P<f10>.*)'

        self._line_re = ';'.join([
            abonent_re,
            address_re,
            account_re,
            debt_re,
            f5_re,
            f6_re,
            f7_re,
            datefrom_re,
            dateto_re,
            f10_re
        ])

    def source_data_correct(self):
        file_sum_header = float(self._get_header_param_value('FILESUM'))

        with open(self.filename, 'r') as f:
            file_sum_records = 0
            for line in f:
                m = re.match(self._line_re, line)
                if m:
                    file_sum_records += float(m.group('debt')) if m.group('debt') else 0
        return round(file_sum_header - file_sum_records, 2) == 0


class Oblgaz(ProvDataText):
    def __init__(self, filename=''):
        ProvDataText.__init__(self, filename)
        # Внешняя услуга
        self._service_code = '3149'
        self._format_datetime = r'%d/%m/%y'

        # Пример строки для облгаза:
        # АВДЕЕВА НАДЕЖДА АЛЕКСЕЕВНА;Кокуй,Комсомольская,16,18;0984;-153.83;;01/06/15;30/06/15
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'
        date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>.*)'  # Принимаются любые символы в лицевом счете!
        debt_re = r'(?P<debt>%(num_re)s)' % {'num_re': num_re}
        f5_re = r'(?P<f5>.*)'
        datefrom_re = r'(?P<datefrom>%(date_re)s)' % {'date_re': date_re}
        dateto_re = r'(?P<dateto>%(date_re)s)' % {'date_re': date_re}

        self._line_re = ';'.join([abonent_re, address_re, account_re, debt_re, f5_re, datefrom_re, dateto_re])

    def source_data_correct(self):
        file_sum_header = float(self._get_header_param_value('FILESUM'))

        with open(self.filename, 'r') as f:
            file_sum_records = 0
            for line in f:
                m = re.match(self._line_re, line)
                if m:
                    file_sum_records += float(m.group('debt'))
        return round(file_sum_header - file_sum_records, 2) == 0


# TODO Переделать: наследовать от Облгаза неправильно. В данном случае лучше повториться (?)
class Lider(Oblgaz):
    def __init__(self, filename=''):
        Oblgaz.__init__(self, filename=filename)
        # ЯНЕЕВА МАРИНА АЛЕКСАНДРОВНА;ЧИТА,БАТАРЕЙНЫЙ МКР,2,1;097283;14190.62;;01/12/16;31/12/16;31:14190.62:
        self._format_datetime = r'%d/%m/%y'
        self._service_code = self._get_header_param_value('SERVICE')


class Perspektiva(Oblgaz):
    def __init__(self, filename=''):
        Oblgaz.__init__(self, filename=filename)
        # Пример строки поставщика
        # Белова Екатерина Евгеньевна;Чита,Северный мкр,3,2;01003002;8302.85;;01/11/2016;30/11/2016;
        self._format_datetime = r'%d/%m/%Y'
        self._service_code = self._get_header_param_value('SERVICE')


class SMD(Oblgaz):
    def __init__(self, filename=''):
        Oblgaz.__init__(self, filename=filename)
        # Пример строки поставщика
        # КАЗАКОВА Е Н;ЧИТА,СИЛИКАТНЫЙ,5,1;1272001;660.00;;01/11/16;30/11/16;
        self._format_datetime = r'%d/%m/%y'
        self._service_code = self._get_header_param_value('SERVICE')


class Region(ProvDataText):
    def __init__(self, filename='', service_code=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = service_code
        self.delimiter = ','

        # Пример строки для поставщика:
        # 109100028;Выскубов Михаил Сергеевич;Чита,славянская,10 А,28;16443,36;
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}

        self._line_re = ';'.join([
            account_re,
            abonent_re,
            address_re,
            debt_re,
            ''
        ])


class Zhilkom(ProvDataText):
    def __init__(self, filename=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = '8468'
        self._set_debt_date_from_header()

        # Пример строки для поставщика:
        # Осипова Любовь Владимировна;Чита г,3-я Каштакская ул,1А,24;10024;1126.36
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}

        self._line_re = ';'.join([
            abonent_re,
            address_re,
            account_re,
            debt_re
        ])

    def _set_debt_date_from_header(self):
        """
        Устанавливает дату debt_date на основании заголовка.
        Пример заголовка:
        #NOTE 01.09.14-30.09.14
        """
        h_dates = self._get_header_param_value('NOTE')
        date_re_simple = r'(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d\d'
        notes_re = r'(?P<datefrom>%(date_re)s)-(?P<dateto>%(date_re)s)' % {'date_re': date_re_simple}
        m = re.match(notes_re, h_dates)
        if m:
            self.debt_date = datetime.strptime(m.group('dateto'), '%d.%m.%y')
        else:
            self.debt_date = None


class Ingoda(ProvDataText):
    def __init__(self, filename=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = '5708'

        # Пример строки для поставщика:
        # 112038;Отфиновский А. В.;Чита,Байкальская,15,1;2900.21
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}

        self._line_re = ';'.join([
            account_re,
            abonent_re,
            address_re,
            debt_re
        ])
