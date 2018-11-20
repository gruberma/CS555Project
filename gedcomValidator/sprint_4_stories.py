#!/usr/bin/python3


import datetime

import pandas as pd
from dateutil.parser import parse as parse_date
from utils import *
from datetime import date
from typing import List, Set, Tuple
import itertools as it
from dateutil.relativedelta import relativedelta
import numpy as np

# US 42 - Reject illegitimate dates

# US 32
def multipleBirths(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return all individuals who were born to the same family on the same day
    :param indivs_df:
    :return:
    """
    birth_child_count = indivs_df.groupby(['BIRTHDAY', 'CHILD']).count()
    birth_child_multi = birth_child_count[birth_child_count['ID'] > 1]
    return indivs_df.merge(birth_child_multi.reset_index()[['BIRTHDAY', 'CHILD']])


# US 33 - List Orphans
def list_orphans(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    List all orphans (parents dead, current age under 18)
    :param indivs_df:
    :param families_df:
    :return:
    """
    both = join_both_spouses_to_family(indivs_df, families_df)
    both_dead = both[~both['ALIVE_HUSBAND'].isna() & ~both['ALIVE_WIFE'].isna()]
    orphans = reduce(op.or_, both_dead['CHILDREN'], set())
    return orphans


# US 35
def list_recent_births(indivs_df: pd.DataFrame) -> pd.DataFrame:
    start_date = datetime.datetime.now() + datetime.timedelta(-30)
    indivs_df = indivs_df[~indivs_df['BIRTHDAY'].isna()]
    return indivs_df[indivs_df["BIRTHDAY"].apply(parse_date) > start_date]


# US 36
def list_recent_deaths(indivs_df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + str(indivs_df))
    start_date = datetime.datetime.now() + datetime.timedelta(-30)
    indivs_df = indivs_df[~indivs_df['DEATH'].isna()]
    return indivs_df[indivs_df["DEATH"].apply(parse_date) > start_date]


# US 37
def list_recent_survivors(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns the recent_deaths data-frame with two new columns: one for all living spouse of the decedent and one for
    all living descendants for the decedent :param indivs_df: :param families_df: :return:
    """
    recent_deaths = list_recent_deaths(indivs_df)
    recent_deaths['living spouses'] = [
        {s for s in get_spouses(dead, families_df) if all(indivs_df[indivs_df['ID'] == s]['ALIVE'])}
        for dead in recent_deaths['ID']]
    recent_deaths['living descendants'] = [
        {d for d in get_descendants(dead, families_df) if all(indivs_df[indivs_df['ID'] == d]['ALIVE'])}
        for dead in recent_deaths['ID']]
    return recent_deaths


# US 38
def list_upcoming_birthday(indivs_df: pd.DataFrame, test_today = None) -> pd.DataFrame:
    """
    List all living people in a GEDCOM file whose birthdays occur in the next 30 days
    """
    if test_today:
        today_date = test_today
    else:
        today_date = date.today()

    indivs = indivs_df[indivs_df.DEATH.isna() & ~indivs_df.BIRTHDAY.isna()].copy()
    curyear = today_date.year
    indivs['DAYS_TO_BIRTHDAY'] = [None if pd.isna(birth) else
                    ((date(curyear, parse_date(birth).date().month, parse_date(birth).date().day)) - today_date).days
                    for birth in indivs['BIRTHDAY']]
    indivs = indivs[(indivs['DAYS_TO_BIRTHDAY'] <= 30) & (indivs['DAYS_TO_BIRTHDAY'] >= 0)]
    return indivs


# US39
def list_upcoming_anniversaries(families_df: pd.DataFrame, test_today = None) -> pd.DataFrame:
    """
    List all living couples in a GEDCOM file whose marriage anniversaries occur in the next 30 days
    """
    if test_today:
        today_date = test_today
    else:
        today_date = date.today()

    fam_df = families_df[~families_df.MARRIED.isna()].copy()
    curyear = today_date.year
    fam_df['DAYS_TO_ANNIVERSARY'] = [None if pd.isna(married) else
                    ((date(curyear, parse_date(married).date().month, parse_date(married).date().day)) - today_date).days
                    for married in fam_df['MARRIED']]
    fam_df = fam_df[(fam_df['DAYS_TO_ANNIVERSARY'] <= 30) & (fam_df['DAYS_TO_ANNIVERSARY'] >= 0)]
    return fam_df


# US13
def siblings_spacing(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> List[Tuple[str, str, int]]:
    """
     more than 8 months apart or less than 2 days apart
    :return: 
    """
    def getBirthday(indiv_id):
        matches = indivs_df[indivs_df['ID'] == indiv_id]
        if matches is not None:
            return parse_date(matches['BIRTHDAY'].values[0])

    children: List[Set[str]] = families_df['CHILDREN']
    child_pairs: List[List[Tuple[str, str]]] = [list(it.combinations(siblings, 2)) for siblings in children]
    strange_children: List[Tuple[str, str, int]] = \
        {(c1, c2, np.abs(relativedelta(getBirthday(c1), getBirthday(c2)).days))
            for family_pairs in child_pairs for c1, c2 in family_pairs
            if (np.abs(relativedelta(getBirthday(c1), getBirthday(c2)).days) > 2) and
               (np.abs(relativedelta(getBirthday(c1), getBirthday(c2)).months) < 8)}
    return strange_children

