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

    # indsb -> individuals birthdates
    indsb = indivs_df[indivs_df.BIRTHDAY.notnull()]
    indsb = indsb[indsb.BIRTHDAY.apply(parse_date) > datetime.datetime.now()]
    # indsd -> individuals death dates
    indsd = indivs_df[indivs_df.DEATH.notnull()]
    indsd = indsd[indsd.DEATH.apply(parse_date)  > datetime.datetime.now()]
    # inds  -> combined individuals table
    inds = indsb.append(indsd)
    inds = inds.drop_duplicates(subset=['ID'])

    # famsm -> date of marriage
    famsm = families_df[families_df.MARRIED.notnull()]
    famsm = famsm[famsm.MARRIED.apply(parse_date) > datetime.datetime.now()]
    # famsd -> date of divorce
    famsd = families_df[families_df.DIVORCED.notnull()]
    famsd = famsd[famsd.DIVORCED.apply(parse_date)  > datetime.datetime.now()]
    # fams  -> combined families table
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

# US 03 - Birth before death
def birth_before_death(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
        :param indivs_df:
        :param families_df:
        :return:
        """
    indivs = indivs_df[~indivs_df['DEATH'].isna() & ~indivs_df['DEATH'].isna()]
    res = indivs[indivs['BIRTHDAY'].apply(parse_date) > indivs['DEATH'].apply(parse_date)]
    return res

# US 08 - Birth before marriage of parents
def birth_before_parents_married(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are born after their parents marriage
    :param indivs_df:
    :param families_df:
    :return:
    """
    result = ""
    inds = indivs_df[indivs_df.BIRTHDAY.notnull()]
    fams = families_df[families_df.MARRIED.notnull()]
    joined = join_by_child(inds, fams)
    joined = joined[joined.BIRTHDAY.apply(parse_date) > joined.MARRIED.apply(parse_date)]
    print(tabulate_df(joined))
    return (inds, fams)

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

def get_family_id_of_child(indivs_id, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find id of family of which indivs_id is a child.
    :param indivs_id:
    :param families_df:
    :return:
    """
    for famid in families_df['ID']:
        for famc in families_df[families_df['ID'] == famid]['CHILDREN']: #families_df['CHILDREN'].get(indivs_id).notnull()]:
            if indivs_id in famc:
                print("indiv_id: %s - fam_id: %s" % (indivs_id, famid))
                return famid
    return None


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
    print('Individuals who\'s birthday is before their parents marriage date')
    print(tabulate_df(birth_before_parents_married(indivs_df, families_df)[0]))
    print(tabulate_df(birth_before_parents_married(indivs_df, families_df)[1]))
    print()
    print('Individuals birth occur before marriage of an individual')
    inds = birth_before_marriage(indivs_df, families_df)
    print(tabulate_df(inds))
    print()
    print('Individuals birth should occur before death of an individual')
    inds = birth_before_death(indivs_df)
    print(tabulate_df(inds))

if __name__ == "__main__":
    # input parsing
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<gedcom filepath>")
    else:
        run_all_checks(sys.argv[1])
