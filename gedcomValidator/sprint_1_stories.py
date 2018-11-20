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


# US 01 - Dates before current date
def dates_before_current_date(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Detect all dates in file that are after current date
    :param indivs_df:
    :param families_df:
    :return:
    """

    # extract rows with bad dates from individuals
    inds_birthday_no_null = indivs_df[indivs_df.BIRTHDAY.notnull()]
    inds_birthday_violations = inds_birthday_no_null[inds_birthday_no_null.BIRTHDAY.apply(parse_date) > datetime.datetime.now()]
    inds_death_no_null = indivs_df[indivs_df.DEATH.notnull()]
    inds_death_violations = inds_death_no_null[inds_death_no_null.DEATH.apply(parse_date) > datetime.datetime.now()]

    # extract rows with bad dates from families
    fams_marriage_no_null = families_df[families_df.MARRIED.notnull()]
    fams_marriage_violations = fams_marriage_no_null[fams_marriage_no_null.MARRIED.apply(parse_date) > datetime.datetime.now()]
    fams_divorce_no_null = families_df[families_df.DIVORCED.notnull()]
    fams_divorce_violations = fams_divorce_no_null[fams_divorce_no_null.DIVORCED.apply(parse_date) > datetime.datetime.now()]

    return (inds_birthday_violations, inds_death_violations, fams_marriage_violations, fams_divorce_violations)


# US 02 - Birth before marriage
def birth_before_marriage(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all Birth dates which are before marriage
    :param indivs_df: Individual data frame
    :param families_df: Family data frame
    :return: All indivis which Birth date is before marriage
    """
    merged_data = join_by_spouse(indivs_df, families_df)
    all_married = merged_data[~merged_data['MARRIED'].isna() & ~merged_data['BIRTHDAY'].isna()]
    res = all_married[all_married['MARRIED'].apply(parse_date) < all_married['BIRTHDAY'].apply(parse_date)]
    return res


# US 03 - Birth before death
def birth_before_death(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all Birth dates which are before death
    :param indivs_df: Individual data frame
    :return: All indivis which Birth date is before death
    """
    indivs = indivs_df[~indivs_df['BIRTHDAY'].isna() & ~indivs_df['DEATH'].isna()]
    res = indivs[indivs['BIRTHDAY'].apply(parse_date) > indivs['DEATH'].apply(parse_date)]
    return res


# US 04
def marriage_before_divorce(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects all individuals where their marriage occured after divorce.
    divorce is before the marriage.
    :param indivs_df:
    :param famalies_df:
    :return:
    """
    indiv_fams: pd.DataFrame = join_by_spouse(indivs_df, families_df)
    # Only consider married, divorced individuals ...
    indiv_fams = indiv_fams[~indiv_fams['MARRIED'].isna() & ~indiv_fams['DIVORCED'].isna()]
    # ... who got married after the divorce
    return indiv_fams[
        indiv_fams['MARRIED'].apply(parse_date) > indiv_fams['DIVORCED'].apply(parse_date)]


# US 05
def marriage_before_death(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects all individuals that were married after their death
    :param indivs_df:
    :param families_df:
    :return:
    """
    indiv_fams: pd.DataFrame = join_by_spouse(indivs_df, families_df)
    # Only consider married, death individuals ...
    indiv_fams = indiv_fams[~indiv_fams['MARRIED'].isna() & ~indiv_fams['DEATH'].isna()]
    # ... who got married after the death
    return indiv_fams[
        indiv_fams['MARRIED'].apply(parse_date) > indiv_fams['DEATH'].apply(parse_date)]


# US 06
def divorce_before_death(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who got divorced after their death.
    :param indivs_df:
    :param families_df:
    :return:
    """
    indiv_fams: pd.DataFrame = join_by_spouse(indivs_df, families_df)
    # Only consider dead, divorced individuals ...
    indiv_fams = indiv_fams[~indiv_fams['DEATH'].isna() & ~indiv_fams['DIVORCED'].isna()]
    # ... who got divorced after their death
    return indiv_fams[indiv_fams['DEATH'].apply(parse_date) < indiv_fams['DIVORCED'].apply(parse_date)]


# US 07
def less_than_150_years_old(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are older than 150 years.
    :param indivs_df:
    :return:
    """
    return indivs_df[indivs_df['AGE'] > 150]


# US 08 - Birth before marriage of parents
def birth_before_parents_married(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are born after their parents marriage
    :param indivs_df:
    :param families_df:
    :return:
    """
    inds = indivs_df[indivs_df.BIRTHDAY.notnull()]
    fams = families_df[families_df.MARRIED.notnull()]
    joined = join_by_child(inds, fams)

    if joined.empty:
        return joined
    joined = joined[joined.BIRTHDAY.notnull() & joined.MARRIED.notnull()]
    if joined.empty:
        return joined
    joined = joined[joined.BIRTHDAY.apply(parse_date) < joined.MARRIED.apply(parse_date)]
    return joined

