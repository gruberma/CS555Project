#!/usr/bin/python3


import datetime

import pandas as pd
from dateutil.parser import parse as parse_date
from utils import *
from datetime import date

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
def list_upcoming_birthday(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
    List all living people in a GEDCOM file whose birthdays occur in the next 30 days
    """
    indivs = indivs_df[indivs_df.DEATH.isna() & ~indivs_df.BIRTHDAY.isna()].copy()
    curyear = date.today().year
    indivs['DAYS_TO_BIRTHDAY'] = [None if pd.isna(birth) else
                    ((date(curyear, parse_date(birth).date().month, parse_date(birth).date().day)) - date.today()).days
                    for birth in indivs['BIRTHDAY']]
    indivs = indivs[(indivs['DAYS_TO_BIRTHDAY'] <= 30) & (indivs['DAYS_TO_BIRTHDAY'] >= 0)]
    return indivs


# US39
def list_upcoming_anniversaries(families_df: pd.DataFrame) -> pd.DataFrame:
    """
    List all living couples in a GEDCOM file whose marriage anniversaries occur in the next 30 days
    """
    fam_df = families_df[~families_df.MARRIED.isna()].copy()
    curyear = date.today().year
    fam_df['DAYS_TO_ANNIVERSARY'] = [None if pd.isna(married) else
                    ((date(curyear, parse_date(married).date().month, parse_date(married).date().day)) - date.today()).days
                    for married in fam_df['MARRIED']]
    fam_df = fam_df[(fam_df['DAYS_TO_ANNIVERSARY'] <= 30) & (fam_df['DAYS_TO_ANNIVERSARY'] >= 0)]
    print(tabulate(fam_df))
    return fam_df

#US 33 - List Orphans
def list_orphans(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    List all orphans (parents dead, current age under 18)
    :param indivs_df:
    :param families_df:
    :return:
    """
   # print("\n" + str(families_df))
    dead_people = indivs_df[~indivs_df['DEATH'].isna()] #find all dead people
  #  print("\n DEAD PEOPLE ARE: \n" + str(dead_people))
    spouse_joined = join_by_spouse(dead_people, families_df).reset_index() #find all married couples where husband and wife are both dead
    children = get_children_of_couple(spouse_joined['HUSBAND ID'], spouse_joined['WIFE ID'], families_df) #find children of dead parents
    children = children[children.AGE < 18]
  #  print(children)
    return indivs_df.merge(children)