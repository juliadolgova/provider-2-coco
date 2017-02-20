# -*- encoding: utf-8 -*-
import pgpxmlrpc


class CoconutService:
    def __init__(self, **dict_api):
        self.coconut = pgpxmlrpc.Service(
            uri=dict_api['uri'],
            service_key=dict_api['skey'],
            gpg_homedir=dict_api['dir_keyring'],
            gpg_key=dict_api['key'],
            gpg_password=dict_api['pswd']
        )
        self.company = 'mks'

    # TODO: сделать по-человечески
    def import_providers(self, providers):
        return self.coconut.balance.import_providers(self.company, providers)

    def import_services(self, provider, services):
        return self.coconut.balance.import_services(self.company, provider, services)

    def import_accounts(self, provider, accounts):
        return self.coconut.balance.import_accounts(self.company, provider, accounts)

    def import_balances(self, provider, balances):
        return self.coconut.balance.import_balances(self.company, provider, balances)

    def account_balance(self, provider, fnd_balance_args):
        return self.coconut.balance.account_balance(self.company, provider, fnd_balance_args)

    # fnd_account_args - словарь вида {'street': u'Ленина', 'house': u'1', 'lastname': u'Петров'}
    def search_account(self, provider, fnd_account_args):
        return self.coconut.balance.search_account(self.company, provider, fnd_account_args)

    def get_providers(self, *args):
        return self.coconut.balance.get_providers(self.company, *args)

    def get_services(self, *args):
        return self.coconut.balance.get_services(self.company, *args)

    def del_accounts(self, *args):
        return self.coconut.balance.del_accounts(self.company, *args)

    def del_balances(self, *args):
        return self.coconut.balance.del_balances(self.company, *args)

    def print_methods_help(self):
        method_names = ('balance.import_providers',
                        'balance.import_services',
                        'balance.import_accounts',
                        'balance.import_balances',
                        'balance.account_balance',
                        'balance.search_account',
                        'balance.get_providers',
                        'balance.get_services',
                        'balance.del_accounts',
                        'balance.del_balances',
                        )
        for method in method_names:
            print method
            res = self.coconut.system.methodHelp(method)
            print res


'''
    get_providers и get_services

    def del_balances(self, company, provider, accounts, date_from=None, date_to=None):
        """
    Удаление баланса третих лиц
        :type company: str Код организации
        :type provider: str Код поставщика
        :type accounts: tuple Кортеж ЛС для удаления балансов
        :type date_from: date Дата с которой удаляем балансы ЛС
        :type date_to: date Дата по которую удаляем балансы ЛС
        :rtype list: Список удаленных балансов
        """
    def del_accounts(self, company, provider, accounts):
        """
    Удаление ЛС третих лиц
        :type company: str Код организации
        :type provider: str Код поставщика
        :type accounts: tuple Кортеж ЛС для удаления балансов
        :rtype tuple: Кортеж из списка логов и списка ошибок
        """
'''