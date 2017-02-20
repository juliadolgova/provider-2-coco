# -*- encoding: utf-8 -*-
import traceback
import sys


def split_fio(fio):
    lastname, firstname, middlename = ['', '', '']

    splitted_fio = fio.strip().rsplit(None, 2)
    if len(splitted_fio) > 0:
        lastname = splitted_fio[0]
        if len(splitted_fio) > 1:
            firstname = splitted_fio[1]
            if len(splitted_fio) > 2:
                middlename = splitted_fio[2]
            else:
                # Пытаемся разбить через точку
                splitted_io = splitted_fio[1].split('.', 1)
                if len(splitted_io) > 1:
                    firstname = splitted_io[0].strip()
                    middlename = splitted_io[1].strip().rstrip('.')
                else:
                    # Оставляем отчество пустым
                    pass
        else:
            # Оставляем И.О. пустыми
            pass
    else:
        # Оставляем Ф.И.О. пустыми
        pass
    return [lastname, firstname, middlename]


def process_source_exception(description, instance_exception):
    print description
    print traceback.format_exception(*sys.exc_info())


def process_error(description):
    print description
