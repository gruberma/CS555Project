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
