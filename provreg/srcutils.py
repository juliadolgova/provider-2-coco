# -*- encoding: utf-8 -*-


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


def source_error_print(**kwargs):
    print 'Ошибка при преобразовании данных из файла {}'.format(kwargs['file'])
    print 'Запись: {}'.format(kwargs['record'])
    print '#: {}'.format(kwargs['at'])
    print 'Exception: {}'.format(kwargs['exception'])


def process_error(description):
    print description
