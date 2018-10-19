#!/usr/bin/env python3


import pandas as pd
import gedcomParser.fileToDataframes
import sys
import datetime
from tabulate import tabulate
from dateutil.parser import parse as parse_date
from typing import Tuple


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
    result = ""
    inds = indivs_df[indivs_df.BIRTHDAY.notnull()]
    fams = families_df[families_df.MARRIED.notnull()]
    joined = join_by_child(inds, fams)
    joined = joined[joined.BIRTHDAY.notnull() & joined.MARRIED.notnull()]
    joined = joined[joined.BIRTHDAY.apply(parse_date) < joined.MARRIED.apply(parse_date)]
    return joined


# US 21
def correct_gender_for_role(indivs_df, families_df):
    indiv_fams: pd.DataFrame = join_by_spouse(indivs_df, families_df)
    return indiv_fams[
        ((indiv_fams['GENDER'] == 'F') & (indiv_fams['ID'] == indiv_fams['HUSBAND ID'])) |
        ((indiv_fams['GENDER'] == 'M') & (indiv_fams['ID'] == indiv_fams['WIFE ID']))]



def get_family_id_of_child(indivs_id, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find id of family of which indivs_id is a child.
    :param indivs_id:
    :param families_df:
    :return:
    """
    for famid in families_df['ID']:
        for famc in families_df[families_df['ID'] == famid][
            'CHILDREN']:  # families_df['CHILDREN'].get(indivs_id).notnull()]:
            if indivs_id in famc:
                print("indiv_id: %s - fam_id: %s" % (indivs_id, famid))
                return famid
    return None


def join_by_spouse(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to join an individual to all families he participates in as a spouse.
    :param indivs_df: Individuals dataframe
    :param families_df: Families dataframe
    :return: Table listing all individuals together with the families they are a spouse in.
             Individuals from indivs_df might occur multiple times if they participate in multiple families.
             They will not occur if they do not participate in any family.
    """
    males: pd.DataFrame = indivs_df.merge(families_df, left_on='ID', right_on='HUSBAND ID', suffixes=('', '_fam'))
    females: pd.DataFrame = indivs_df.merge(families_df, left_on='ID', right_on='WIFE ID', suffixes=('', '_fam'))
    return males.append(females)


def join_by_child(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to join an individual to all families he participates in as a child.
    :param indivs_df:
    :param families_df:
    :return:
    """
    # Clone arguments
    indivs_df_temp: pd.DataFrame = indivs_df.copy()
    families_df_temp: pd.DataFrame = families_df.copy()
    # Calculate cartesian product
    indivs_df_temp['key'] = 0
    families_df_temp['key'] = 0
    product: pd.DataFrame = indivs_df_temp.merge(families_df_temp, on='key', suffixes=('', '_fam'))
    # Remove helping column key
    product = product[product.columns.drop('key')]
    # Filter
    return product[[Id in children for Id, children in zip(product['ID'], product['CHILDREN'])]]


def tabulate_df(df: pd.DataFrame) -> str:
    """
    Helper function to format a dataframe
    :param df: dataframe
    :return: string table
    """
    return tabulate(df, headers='keys', tablefmt='psql')


def run_all_checks(filename: str):
    indivs_df, families_df = gedcomParser.fileToDataframes.parseFileToDFs(filename)

    print("Individuals:")
    print(tabulate_df(indivs_df))
    print()
    print("Families:")
    print(tabulate_df(families_df))
    print()

    # US 01
    inds_birth, inds_death, fams_marriage, fams_divorce = dates_before_current_date(indivs_df, families_df)
    for index, (indiv_id, birth) in inds_birth[['ID', 'BIRTHDAY']].iterrows():
            print("ERROR: INDIVIDUAL: US01: {}: Dates before current date - Birth {}".format(indiv_id, birth))
    for index, (indiv_id, death) in inds_death[['ID', 'DEATH']].iterrows():
            print("ERROR: INDIVIDUAL: US01: {}: Dates before current date - Death {}".format(indiv_id, death))
    for index, (family_id, married) in fams_marriage[['ID', 'MARRIED']].iterrows():
            print("ERROR: FAMILIES: US01: {}: Dates before current date - Married {}".format(family_id, married))
    for index, (family_id, divorce) in fams_divorce[['ID', 'DIVORCED']].iterrows():
            print("ERROR: FAMILIES: US01: {}: Dates before current date - Divorced {}".format(family_id, divorce))

    # US 02
    for index, (indiv_id, birth, marriage) in birth_before_marriage(indivs_df, families_df)[['ID', 'BIRTHDAY', 'MARRIED']].iterrows():
        print("ERROR: INDIVIDUAL: US02: {}: Birth should occur before marriage - Birthday {}: MARRIED {}".format(indiv_id, birth, marriage))

    # US 03
    for index, (indiv_id, birth, death) in birth_before_death(indivs_df)[['ID', 'BIRTHDAY', 'DEATH']].iterrows():
        print("ERROR: INDIVIDUAL: US03: {}: Birth should occur before death - Birthday {}: Death {}".format(indiv_id, birth, death))

    # US 04
    for index, (indiv_id, marriage, divorce) in marriage_before_divorce(indivs_df, families_df)[['ID', 'MARRIED', 'DIVORCED']].iterrows():
        print("ERROR: INDIVIDUAL: US04: {}: Marriage after divorce - Marriage {}: Divorce {}".format(indiv_id, marriage, divorce))

    # US 05
    for index, (indiv_id, marriage, death) in marriage_before_death(indivs_df, families_df)[['ID', 'MARRIED', 'DEATH']].iterrows():
        print("ERROR: INDIVIDUAL: US05: {}: Marriage after death - Marriage {}: Death {}".format(indiv_id, marriage, death))

    # US 06
    for index, (indiv_id, divorce, death) in divorce_before_death(indivs_df, families_df)[['ID', 'DIVORCED', 'DEATH']].iterrows():
        print("ERROR: INDIVIDUAL: US06: {}: Divorced after death - Divorce {}: Death {}".format(indiv_id, divorce, death))

    # US 07
    for index, (indiv_id, birth, death) in less_than_150_years_old(indivs_df)[['ID', 'BIRTHDAY', 'DEATH']].iterrows():
        print("ERROR: INDIVIDUAL: US07: {}: More than 150 years old - Birth {}: Death {}".format(indiv_id, birth, death))

    # US 08
    merge = birth_before_parents_married(indivs_df, families_df)
    for index, (indiv_id, marr) in merge[['ID', 'MARRIED']].iterrows():
        print("ERROR: INDIVIDUAL: US08: {}: Individual's birthday is before parents' marriage date -  {}".format(indiv_id, marr))


if __name__ == "__main__":
    # input parsing
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<gedcom filepath>")
    else:
        run_all_checks(sys.argv[1])


