#!/usr/bin/env python3

import operator as op
from functools import reduce
from typing import Set

import numpy as np
import pandas as pd
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
from tabulate import tabulate


def calc_delta_date(df: pd.DataFrame, date1_name, date2_name):
    """
    Calculate delta date of two dates.
    :param df:
    :param date1_name:
    :param date2_name:
    :return:
    """
    return [np.nan if date1 is np.nan or date2 is np.nan else
            relativedelta(parse_date(date2), parse_date(date1)).years
            for date1, date2 in zip(df[date1_name], df[date2_name])]


def get_surname(full_name):
    """
    Helper function to get the surname of a string like: FirstName /LastName/
    :param full_name:
    :return:
    """
    import re
    surname = re.search('/(.*)/', full_name).group(1)
    return surname


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
    # males and females have the same index so when we combine them we have to reset the index
    return males.append(females, ignore_index=True)


def join_both_spouses_to_family(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to join both spouses to the family the participate in as HUSBAND and WIFE.
    :param indivs_df: Individuals dataframe
    :param families_df: Families dataframe
    :return: Table listing all individuals together with the families they are a spouse in.
             Individuals from indivs_df might occur multiple times if they participate in multiple families.
             They will not occur if they do not participate in any family.
    """
    orig_colums = indivs_df.columns
    indivs_df.columns = [c + "_HUSBAND" for c in orig_colums]
    husbands: pd.DataFrame = indivs_df.merge(families_df, left_on='ID_HUSBAND', right_on='HUSBAND ID',
                                             suffixes=('', '_fam'))
    indivs_df.columns = [c + "_WIFE" for c in orig_colums]
    both_spouses: pd.DataFrame = indivs_df.merge(husbands, left_on='ID_WIFE', right_on='WIFE ID', suffixes=('', '_fam'))
    both_spouses.rename(columns={'ID': 'ID_fam'}, inplace=True)
    indivs_df.columns = orig_colums
    return both_spouses


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
    Helper function to format a data-frame
    :param df: data-frame
    :return: string table
    """
    return tabulate(df, headers='keys', tablefmt='psql')


def get_descendants(individual_id, fams_df) -> Set[str]:
    """
    Given an individual, return all his/her descendants
    :param individual_id: id of an individual
    :param fams_df: families data-frame holding the family-tree
    :return: set of individual-ids of all descendants
    """
    children = get_children(individual_id, fams_df)
    return children | reduce(op.or_, [get_descendants(c, fams_df) for c in children], set())


def get_children(individual_id, fams_df) -> Set[str]:
    """
    Given an individual, return all his/her children
    :param individual_id: id of an individual
    :param fams_df: families data-frame holding the family-tree
    :return: set of individual-ids of all children
    """
    families = fams_df[(fams_df['HUSBAND ID'] == individual_id) | (fams_df['WIFE ID'] == individual_id)]
    children = reduce(op.or_, families['CHILDREN'], set())
    return children


def get_spouses(individual_id, fams_df) -> Set[str]:
    """
    Given an individual, return all his/her (ex)spouses
    :param individual_id: id of an individual
    :param fams_df: families data-frame holding the family-tree
    :return: set of individual-ids of all (ex)spouses
    """
    return set(fams_df[fams_df['HUSBAND ID'] == individual_id]['WIFE ID']) \
        | set(fams_df[fams_df['WIFE ID'] == individual_id]['HUSBAND ID'])
