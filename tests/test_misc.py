# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import provgate


class TestProvgate(unittest.TestCase):

    def test_get_debt_date(self):
        filename = r'.\misc\simple_file.txt'

        debt_date = provgate.get_debt_date(filename, provgate.DS_DATE_FILE_CREATED)
        expected_date = datetime(2017, 4, 19)
        delta_seconds = abs((debt_date - expected_date).total_seconds())
        self.assertLess(delta_seconds, 60)

        debt_date = provgate.get_debt_date(filename, provgate.DS_DATE_FILE_MODIFIED)
        expected_date = datetime(2017, 4, 19)
        delta_seconds = abs((debt_date - expected_date).total_seconds())
        self.assertLess(delta_seconds, 60)

        debt_date = provgate.get_debt_date(filename, provgate.DS_DATE_NOW)
        t_day = datetime.today()
        expected_date = datetime(t_day.year, t_day.month, t_day.day)
        delta_seconds = abs((debt_date - expected_date).total_seconds())
        self.assertLess(delta_seconds, 60)

        debt_date = provgate.get_debt_date(filename, provgate.DS_MONTH_BEGIN)
        expected_date = datetime(datetime.today().year, datetime.today().month, 1)
        self.assertEqual(debt_date, expected_date)