#!/usr/bin/env python3


import pandas as pd
import gedcomParser.fileToDataframes
import sys
import datetime
from tabulate import tabulate
from dateutil.parser import parse as parse_date


# US 01 - Dates before current date
def dates_before_current_date(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all dates in file that are after current date
    :param indivs_df:
    :param families_df:
    :return:
    """
    indsb = indivs_df[indivs_df.BIRTHDAY.notnull()]
    indsb = indsb[indsb.BIRTHDAY.apply(parse_date) > datetime.datetime.now()]
    indsd = indivs_df[indivs_df.DEATH.notnull()]
    indsd = indsd[indsd.DEATH.apply(parse_date)  > datetime.datetime.now()]
    inds = indsb.append(indsd)
    inds = inds.drop_duplicates(subset=['ID'])

    famsm = families_df[families_df.MARRIED.notnull()]
    famsm = famsm[famsm.MARRIED.apply(parse_date) > datetime.datetime.now()]
    famsd = families_df[families_df.DIVORCED.notnull()]
    famsd = famsd[famsd.DIVORCED.apply(parse_date)  > datetime.datetime.now()]
    fams = famsm.append(famsd)
    fams = fams.drop_duplicates(subset=['ID'])
    return (inds, fams)


# US 02 - Birth before marriage
def birth_before_marriage(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    :param indivs_df:
    :param families_df:
    :return:
    """
    merged_data = join_by_spouse(indivs_df, families_df)
    all_married = merged_data[~merged_data['MARRIED'].isna() & ~merged_data['BIRTHDAY'].isna()]
    res = all_married[all_married['MARRIED'].apply(parse_date) < all_married['BIRTHDAY'].apply(parse_date)]
    return res


# US 08 - Birth before marriage of parents
def birth_before_parents_married(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are born after their parents marriage
    :param indivs_df:
    :param families_df:
    :return:
    """
    pass


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


def join_by_spouse(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to join an individual to all families we participates in as a spouse.
    :param indivs_df: Individuals dataframe
    :param families_df: Families dataframe
    :return: Table listing all individuals together with the families they are a spouse in.
             Individuals from indivs_df might occur multiple times if they participate in multiple families.
             They will not occur if they do not participate in any family.
    """
    males: pd.DataFrame = indivs_df.merge(families_df, left_on='ID', right_on='HUSBAND ID', suffixes=('', '_fam'))
    females: pd.DataFrame = indivs_df.merge(families_df, left_on='ID', right_on='WIFE ID', suffixes=('', '_fam'))
    return males.append(females)


def tabulate_df(df: pd.DataFrame) -> str:
    """
    Helper function to format a dataframe
    :param df: dataframe
    :return: string table
    """
    return tabulate(df, headers='keys', tablefmt='psql')


def run_all_checks(filename: str):
    indivs_df, families_df = gedcomParser.fileToDataframes.parseFileToDFs(filename)

    print('Individuals who are more than 150 years old:')
    print(tabulate_df(less_than_150_years_old(indivs_df)[['ID', 'NAME', 'BIRTHDAY', 'DEATH', 'AGE']]))
    print()
    print('Individuals who got divorced after their death')
    print(tabulate_df(divorce_before_death(indivs_df, families_df)[['ID', 'NAME', 'DEATH', 'DIVORCED']]))
    print()
    print('Individuals or families containing date records that are before today')
    inds, fams = dates_before_current_date(indivs_df, families_df)
    print(tabulate_df(inds))
    print(tabulate_df(fams))
    print()
    print('Individuals birth occur before marriage of an individual')
    inds = birth_before_marriage(indivs_df, families_df)
    print(tabulate_df(inds))

if __name__ == "__main__":
    # input parsing
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<gedcom filepath>")
    else:
        run_all_checks(sys.argv[1])
