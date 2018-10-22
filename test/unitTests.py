#!/usr/bin/python3

import sys

sys.path.append('..')
sys.path.append('../gedcomValidater')

from gedcomValidater import validate
from gedcomValidater.gedcomParser.fileToDataframes import parseFileToDFs, indivs_columns, fams_columns
import unittest
from unittest import TestCase
import numpy as np
import pandas as pd


# US 01
class TestDatesBeforeCurrentDate(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/sprint1_acceptance_file.ged")
        _, dates_indiv, _, _ = validate.dates_before_current_date(indivs_df, fams_df)
        expected_indiv = {
            'ID': {0: '@mystery@'},
            'DEATH': {0: '20 MAY 2200'}}
        self.assertEqual(dates_indiv[['ID', 'DEATH']].to_dict(), expected_indiv)


# US 02 - Birth before marriage unit test.
class TestBirthBeforeMarriage(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/sprint1_acceptance_file.ged")
        indivs_error = validate.birth_before_marriage(indivs_df, fams_df)
        expected = [['@shmi@']]
        self.assertEqual(indivs_error[['ID']].values.tolist(), expected)


# US 03 - Birth before death
class TestBirthBeforeDeath(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/sprint1_acceptance_file.ged")
        indivs_error = validate.birth_before_death(indivs_df)
        expected = [['@shmi@']]
        self.assertEqual(indivs_error[['ID']].values.tolist(), expected)


# US 04
class TestMarriageBeforeDivorce(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/sprint1_acceptance_file.ged")
        marriage_after_divs = validate.marriage_before_divorce(indivs_df, fams_df)
        expected = [{'ID': '@shmi@', 'NAME': 'Shmi /Skywalker/', 'MARRIED': '20 MAY 1979', 'DIVORCED': '20 MAY 1977'},
                    {'ID': '@mystery@', 'NAME': 'The /Force/', 'MARRIED': '20 MAY 1979', 'DIVORCED': '20 MAY 1977'}]
        actual = [row.to_dict() for _, row in marriage_after_divs[['ID', 'NAME', 'MARRIED', 'DIVORCED']].iterrows()]
        self.assertEqual(sorted(actual, key=lambda dict: dict['ID']), sorted(expected, key=lambda dict: dict['ID']))


# US 05
class TestMarriageBeforeDeath(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/sprint1_acceptance_file.ged")
        marriage_after_death = validate.marriage_before_death(indivs_df, fams_df)
        expected = [{'ID': '@shmi@', 'NAME': 'Shmi /Skywalker/', 'MARRIED': '20 MAY 1979', 'DEATH': '20 MAY 1976'}]
        actual = [row.to_dict() for _, row in marriage_after_death[['ID', 'NAME', 'MARRIED', 'DEATH']].iterrows()]
        self.assertEqual(sorted(actual, key=lambda dict: dict['ID']), sorted(expected, key=lambda dict: dict['ID']))


# US 06
class TestDivorceBeforeDeath(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.divorce_before_death(indivs_df, fams_df)

    def test_errorneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us06_divorce_before_death.ged")
        div_after_death = validate.divorce_before_death(indivs_df, fams_df)
        expected = [{'ID': '@shmi@', 'NAME': 'Shmi /Skywalker/',
                    'DEATH': '16 MAY 1977',
                    'DIVORCED': '10 MAY 1978'}]
        actual = [row.to_dict() for _, row in div_after_death[['ID', 'NAME', 'DEATH', 'DIVORCED']].iterrows()]
        self.assertEqual(sorted(actual, key=lambda dict: dict['ID']), sorted(expected, key=lambda dict: dict['ID']))


# US 07
class TestLessThan150yearsOld(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        validate.less_than_150_years_old(indivs_df)

    def test_erroneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us07_less_than_150_years_old.ged")
        indivs_150 = validate.less_than_150_years_old(indivs_df)
        expected = {'ID': {0: '@ani@', 2: '@luke@'},
                    'NAME': {0: 'Anakin /Skywalker/', 2: 'Luke /Skywalker/'},
                    'BIRTHDAY': {0: '25 MAY 1777', 2: '26 SEP 1865'},
                    'DEATH': {0: '19 MAY 2005', 2: np.nan},
                    'AGE': {0: 227.0, 2: 153.0}}
        self.assertEqual(indivs_150[['ID', 'NAME', 'BIRTHDAY', 'DEATH', 'AGE']].to_dict(), expected)


# US 08
class TestBirthBeforeParentsMarried(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us08_birth_before_marriage.ged")
        indivs_violation = validate.birth_before_parents_married(indivs_df, fams_df)[['ID', 'NAME']]
        expected = {'ID': {9: '@owen@', 18: '@luke@'},
                    'NAME': {9: 'Owen /Lars/', 18: 'Luke /Skywalker/'}}
        self.assertEqual(indivs_violation.to_dict(), expected)

# US 09
class TestBirthAfterParentsDeath(TestCase):
    def test(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us09_birth_before_death_of_parents.ged")
        violation_mother = validate.birth_before_parents_death_mother(indivs_df, fams_df)[['ID_c', 'ID_m']]
        violation_father = validate.birth_before_parents_death_father(indivs_df, fams_df)[['ID_c', 'ID_m']]
        expected_mother = {'ID_c': {2: '@luke@', 3: '@lea@'}, 'ID_m': {2: '@padme@', 3: '@padme@'}}
        expected_father = {'ID_c': {2: '@luke@'}, 'ID_m': {2: '@ani@'}}
        self.assertEqual(violation_mother.to_dict(), expected_mother)
        self.assertEqual(violation_father.to_dict(), expected_father)

# US 12
class TestParentsTooOld(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.mother_too_old(indivs_df, fams_df)
        validate.father_too_old(indivs_df, fams_df)

    def test_erroneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us12_parents_not_too_old_fail.ged")
        indivs_error = validate.mother_too_old(indivs_df, fams_df)
        expected = [['@shmi@']]
        self.assertEqual(expected, indivs_error[['ID_idv_mother']].values.tolist())
        indivs_error = validate.father_too_old(indivs_df, fams_df)
        expected = [['@mystery@']]
        self.assertEqual(expected, indivs_error[['ID_idv_father']].values.tolist())


# US 14
class TestMultipleBirths5(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.multiple_births_5(indivs_df, fams_df)

    def test_erroneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us14_multiple_births_5_fail.ged")
        indivs_error = validate.multiple_births_5(indivs_df, fams_df)
        expected = [[7]]
        self.assertEqual(expected, indivs_error[['CHILDREN']].values.tolist())



# US 15
class TestFewerThan15Siblings(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.siblings_should_not_marry(indivs_df, fams_df)

    def test_erroneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us15_fewer_than_15_siblings.ged")
        fams_error = validate.fewer_than_15_siblings(indivs_df, fams_df)
        expected = ['@sky1@']
        actual = fams_error["ID"].values.tolist()
        self.assertEqual(expected, actual)


# US 16
class TestMaleLastName(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.siblings_should_not_marry(indivs_df, fams_df)

    def test_erroneous(self):
        indiv_df, fams_df = parseFileToDFs("../gedcom_test_files/us16_male_last_name.ged")
        fams_error = validate.same_male_last_name(indiv_df, fams_df)
        expected = ['@ani1@', '@ani2@']
        actual = fams_error["ID"].values.tolist()
        self.assertEqual(expected, actual)


# US 18
class TestSiblingsShouldNotMarry(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.siblings_should_not_marry(indivs_df, fams_df)

    def test_erroneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us18_siblings_should_not_marry.ged")
        wrong_roles = validate.siblings_should_not_marry(indivs_df, fams_df)
        expected = [{'ID_fam': '@solo@', 'ID_HUSBAND': '@luke@', 'ID_WIFE': '@lea@'}]
        actual = [row.to_dict() for _, row in wrong_roles[['ID_fam', 'ID_HUSBAND', 'ID_WIFE']].iterrows()]
        self.assertEqual(sorted(actual, key=lambda d: d['ID_fam']), sorted(expected, key=lambda d: d['ID_fam']))


# US 21
class TestCorrectGenderForRole(TestCase):
    def test_empty(self):
        indivs_df = pd.DataFrame(columns=indivs_columns)
        fams_df = pd.DataFrame(columns=fams_columns)
        validate.correct_gender_for_role(indivs_df, fams_df)

    def test_erroneous(self):
        indivs_df, fams_df = parseFileToDFs("../gedcom_test_files/us21_correct_gender_for_role.ged")
        wrong_roles = validate.correct_gender_for_role(indivs_df, fams_df)
        expected = [{'ID': '@shmi@', 'GENDER': 'F'},
                    {'ID': '@mystery@', 'GENDER': 'M'}]
        actual = [row.to_dict() for _, row in wrong_roles[['ID', 'GENDER']].iterrows()]
        self.assertEqual(sorted(actual, key=lambda dict: dict['ID']), sorted(expected, key=lambda dict: dict['ID']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
