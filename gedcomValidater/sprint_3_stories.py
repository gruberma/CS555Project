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

# US 22
def unique_ids(indivs_df: pd.DataFrame, fams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals/families where the ID is duplicated
    :param indivs_df:
    :return:
    """
    indivs_duplicate = indivs_df[indivs_df.duplicated(['ID'])]
    fams_duplicate = fams_df[fams_df.duplicated(['ID'])]
    result = pd.concat([indivs_duplicate[["ID"]], fams_duplicate[["ID"]]])
    return result


# US 25
def unique_first_names_in_families(indivs_df: pd.DataFrame, fam_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals where the first name and the birth date is the same inside of a family.
    :param indivs_df:
    :return:
    """
    children_with_fam = join_by_child(indivs_df, fam_df)
    if not children_with_fam.empty:
        return children_with_fam[children_with_fam.duplicated(['NAME', 'BIRTHDAY', 'ID_fam'])]
    else:
        return children_with_fam

# US 28
def order_siblings_by_age(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return families_df with siblings-list ordered by decreasing age
    :param indivs_df:
    :param families_df:
    :return:
    """
    new_children = []
    for cs in families_df['CHILDREN']:
        child_age = [(c, indivs_df[indivs_df['ID'] == c].reset_index()['AGE_in_days'][0]) for c in cs]
        child_age = [(c, a) for c, a in child_age if pd.isna(a)]\
                    + sorted([(c, a) for c, a in child_age if not pd.isna(a)], key=lambda ca: ca[1], reverse=True)
        new_children.append([(c, a) for c, a in child_age])
    fams_df_copy = families_df.copy()
    fams_df_copy['CHILDREN'] = new_children
    return fams_df_copy


# US 29
def list_deceased(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
    List all deceased individuals
    :param indivs_df:
    :return:
    """
    indivs = indivs_df[indivs_df.DEATH.notnull()]
    indivs = indivs[indivs.DEATH.apply(parse_date) <= datetime.datetime.now()]
    return indivs

# US 31
def list_living_single_older_than_30(indivs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all individuals who are over the age of 30 and have never been married
    :param indivs_df:
    :return:
    """
    indivs = indivs_df[indivs_df.AGE.notnull()]
    indivs = indivs[indivs.SPOUSE.isnull() & indivs.DEATH.isnull()]
    indivs = indivs[indivs.AGE > 30]
    return indivs
