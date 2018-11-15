#!/usr/bin/python3


import datetime

import pandas as pd
from dateutil.parser import parse as parse_date
from utils import *


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


# US 35
def list_recent_births(indivs_df: pd.DataFrame) -> pd.DataFrame:
    start_date = datetime.datetime.now() + datetime.timedelta(-30)
    indivs_df = indivs_df[~indivs_df['BIRTHDAY'].isna()]
    return indivs_df[indivs_df["BIRTHDAY"].apply(parse_date) > start_date]


# US 36
def list_recent_deaths(indivs_df: pd.DataFrame) -> pd.DataFrame:
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
