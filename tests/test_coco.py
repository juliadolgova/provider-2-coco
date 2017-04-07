# -*- coding: utf-8 -*-
import unittest
import random

import settings
import coco
from test_parse import regs_data
from provreg.srcutils import source_error_print


class TestCoco(unittest.TestCase):

    def test_connection_to_coco(self):
        coco_service = coco.CoconutService(**settings.TEST_COCONUT_SETTINGS)
        coco_service.print_methods_help()

    # TODO: Не забыть протестировать балансы
    def test_random_import(self):
        coco_service = coco.CoconutService(**settings.TEST_COCONUT_SETTINGS)

        for reg_name in regs_data:

            data = regs_data[reg_name]
            prov_class = data['class']
            provider_code = data['mnemo_coco']

            random_num = random.randint(0, data['count']-1)

            # noinspection PyCallingNonCallable
            registry = prov_class(**data['args_init'])
            for key in data:
                if hasattr(registry, key):
                    setattr(registry, key, data[key])
            registry.error_processor = source_error_print

            i = 0

            for item in registry.generate_accounts_decoded():
                if i == random_num:
                    response = ''
                    expected_response = ''
                    try:
                        coco_service.import_accounts(provider_code, [item])
                        coco_service.import_balances(provider_code, [item])

                        response = coco_service.search_account(provider_code,
                                                               {'number': item['number']})[item['number']]

                        expected_response = {
                            'fio': ' '.join([item['lastname'], item['firstname'], item['middlename']]),
                            'address': ' '.join([
                                item['region'],
                                item['city'],
                                item['territory'],
                                item['pfxstreet'] + '.' + item['street'],
                                u'д.' + item['house'],
                                u'кв.' + item['flat']
                            ])
                        }

                        self.assertEqual(response, expected_response)
                    except:
                        print [provider_code, item]
                        print str(response).decode('unicode-escape')
                        print str(expected_response).decode('unicode-escape')
                        raise
                    break
                i += 1


if __name__ == '__main__':
    pass
