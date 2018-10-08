import sys

sys.path.append('..')
sys.path.append('../gedcomValidater')

from gedcomValidater import validate
from gedcomValidater.gedcomParser.fileToDataframes import parseFileToDFs
import unittest
from unittest import TestCase
import numpy as np


class TestDivorceBeforeDeath(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_files/test_divorce_before_death.ged")
        div_after_death = validate.divorce_before_death(indivs_df, fams_df)
        expected = {'ID': {0: '@shmi@'}, 'NAME': {0: 'Shmi /Skywalker/'}, 'DEATH': {0: '16 MAY 1977'},
                    'DIVORCED': {0: '10 MAY 1978'}}
        self.assertEqual(div_after_death[['ID', 'NAME', 'DEATH', 'DIVORCED']].to_dict(), expected)


class TestLessThan150yearsOld(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_files/test_less_than_150_years_old.ged")
        indivs_150 = validate.less_than_150_years_old(indivs_df)
        expected = {'ID': {0: '@ani@', 2: '@luke@'}, 'NAME': {0: 'Anakin /Skywalker/', 2: 'Luke /Skywalker/'},
                    'BIRTHDAY': {0: '25 MAY 1777', 2: '26 SEP 1865'}, 'DEATH': {0: '19 MAY 2005', 2: np.nan},
                    'AGE': {0: 227.0, 2: 153.0}}
        self.assertEqual(indivs_150[['ID', 'NAME', 'BIRTHDAY', 'DEATH', 'AGE']].to_dict(), expected)


if __name__ == '__main__':
    unittest.main()