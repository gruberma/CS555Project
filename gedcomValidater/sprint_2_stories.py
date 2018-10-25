#!/usr/bin/env python3

import pandas as pd
import gedcomParser.fileToDataframes
import sys
import datetime
from tabulate import tabulate
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
import numpy as np
from typing import Tuple
from datetime import date
from utils import *

# US 09 - Birth before death of parents
def birth_before_parents_death_mother(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are born after their mother dies
    :param indivs_df:
    :param families_df:
    :return:
    """
    indv: pd.DataFrame = indivs_df[indivs_df.CHILD.notnull()]
    fams: pd.DataFrame = families_df[families_df.CHILDREN.notnull()]
    join_by_fam_wife = indv.add_suffix('_c').merge(fams.add_suffix('_f'), left_on='CHILD_c', right_on='ID_f', suffixes=('', '_wife'))[['ID_c', 'BIRTHDAY_c', 'WIFE ID_f']]
    join_by_fam_wife = join_by_fam_wife[join_by_fam_wife.BIRTHDAY_c.notnull()]
    join_by_mother = join_by_fam_wife.merge(indivs_df[['ID', 'DEATH']].add_suffix('_m'), how='inner', left_on='WIFE ID_f', right_on='ID_m')[['ID_c', 'BIRTHDAY_c', 'ID_m', 'DEATH_m']]
    join_by_mother = join_by_mother[join_by_mother.BIRTHDAY_c.notnull() & join_by_mother.DEATH_m.notnull()]
    result = join_by_mother[join_by_mother.BIRTHDAY_c.apply(parse_date) > join_by_mother.DEATH_m.apply(parse_date)]
    return result

# US 09 - Birth before death of parents
def birth_before_parents_death_father(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are born after their father dies
    :param indivs_df:
    :param families_df:
    :return:
    """
    indv: pd.DataFrame = indivs_df[indivs_df.CHILD.notnull()]
    fams: pd.DataFrame = families_df[families_df.CHILDREN.notnull()]
    join_by_fam_husband = indv.add_suffix('_c').merge(fams.add_suffix('_f'), left_on='CHILD_c', right_on='ID_f', suffixes=('', '_husband'))[['ID_c', 'BIRTHDAY_c', 'HUSBAND ID_f']]
    join_by_fam_husband = join_by_fam_husband[join_by_fam_husband.BIRTHDAY_c.notnull()]
    join_by_father = join_by_fam_husband.merge(indivs_df[['ID', 'DEATH']].add_suffix('_m'), how='inner', left_on='HUSBAND ID_f', right_on='ID_m')[['ID_c', 'BIRTHDAY_c', 'ID_m', 'DEATH_m']]
    join_by_father = join_by_father[join_by_father.BIRTHDAY_c.notnull() & join_by_father.DEATH_m.notnull()]
    result = join_by_father[join_by_father.BIRTHDAY_c.apply(parse_date) > join_by_father.DEATH_m.apply(parse_date)]
    return result

# US 10 - Marriage after 14
def marriage_before_14(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are married before age 14
    :param indivs_df:
    :param families_df:
    :return:
    """
    indivs_fams = join_by_spouse(indivs_df, families_df)[['ID', 'NAME', 'BIRTHDAY', 'MARRIED']]
    indivs_fams_no_null = indivs_fams[indivs_fams.BIRTHDAY.notnull() & indivs_fams.MARRIED.notnull()].copy()
    indivs_fams_no_null['AGE_MARRIED'] = calc_delta_date(indivs_fams_no_null, 'BIRTHDAY', 'MARRIED')
    return indivs_fams_no_null[indivs_fams_no_null.AGE_MARRIED < 14]

# US 12 - Mother too old
def mother_too_old(indivs_df: pd.DataFrame, families_df: pd.DataFrame):
    """
    Mother should be less than 60 years older than her children than his children
    :param indivs_df:
    :param families_df:
    :return:
    """
    indv: pd.DataFrame = indivs_df[indivs_df.CHILD.notnull()]
    fams: pd.DataFrame = families_df[families_df.CHILDREN.notnull()]
    join_by_fam_id_df = indv.merge(fams, left_on='CHILD', right_on='ID', suffixes=('', '_fam'))

    mother_indv_df = join_by_fam_id_df.merge(indivs_df, left_on='WIFE ID', right_on='ID', suffixes=('', '_idv_mother'))
    mother_indv_df['DIFF_MOTHER'] = calc_delta_date(mother_indv_df, "BIRTHDAY_idv_mother", "BIRTHDAY")
    return mother_indv_df[mother_indv_df.DIFF_MOTHER >= 60]


# US 12 - Father too old
def father_too_old(indivs_df: pd.DataFrame, families_df: pd.DataFrame):
    """
    Father should be less than 80 years older than his children
    :param indivs_df:
    :param families_df:
    :return:
    """
    indv: pd.DataFrame = indivs_df[indivs_df.CHILD.notnull()]
    fams: pd.DataFrame = families_df[families_df.CHILDREN.notnull()]
    join_by_fam_id_df = indv.merge(fams, left_on='CHILD', right_on='ID', suffixes=('', '_fam'))

    father_indv_df = join_by_fam_id_df.merge(indivs_df, left_on='HUSBAND ID', right_on='ID', suffixes=('', '_idv_father'))
    father_indv_df['DIFF_FATHER'] = calc_delta_date(father_indv_df, "BIRTHDAY_idv_father", "BIRTHDAY")
    return father_indv_df[father_indv_df.DIFF_FATHER >= 80]


# US 14 - Multiple births <= 5
def multiple_births_5(indivs_df: pd.DataFrame, families_df: pd.DataFrame):
    """
    Multiple births <= 5
    :param indivs_df:
    :param families_df:
    :return:
    """
    children_df = indivs_df.merge(families_df, left_on='CHILD', right_on='ID', suffixes=('', '_fam'))
    grouped_df = children_df.groupby(['BIRTHDAY', 'CHILD']).agg({'CHILDREN': 'count'}).reset_index()
    res = grouped_df[grouped_df.CHILDREN > 5]
    return res

# US 15
def fewer_than_15_siblings(indivs_df, famalies_df):
    """
    Return all famalies where there are more then 14 children
    :param indivs_df:
    :param famalies_df:
    :return:
    """
    return famalies_df[famalies_df["CHILDREN"].map(len) > 14]


# US 16
def same_male_last_name(indivs_df, famalies_df):
    children_with_fam = join_by_child(indivs_df, famalies_df)
    children_names = children_with_fam["NAME"].map(get_surname)
    father_names = children_with_fam["HUSBAND NAME"].map(get_surname)
    return children_with_fam[children_names != father_names]

# US 18
def siblings_should_not_marry(indivs_df, families_df):
    """
    Return all siblings who are married.
    :param indivs_df:
    :param families_df:
    :return:
    """
    both_spouses = join_both_spouses_to_family(indivs_df, families_df)
    return both_spouses[both_spouses['CHILD_HUSBAND'] == both_spouses['CHILD_WIFE']]


# US 21
def correct_gender_for_role(indivs_df, families_df):
    """
    Return all individuals who take up the wrong gender role in a family the participate as a spouse
    :param indivs_df:
    :param families_df:
    :return:
    """
    indiv_fams: pd.DataFrame = join_by_spouse(indivs_df, families_df)
    return indiv_fams[
        ((indiv_fams['GENDER'] == 'F') & (indiv_fams['ID'] == indiv_fams['HUSBAND ID'])) |
        ((indiv_fams['GENDER'] == 'M') & (indiv_fams['ID'] == indiv_fams['WIFE ID']))]
