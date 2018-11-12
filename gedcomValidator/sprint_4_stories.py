#!/usr/bin/python3


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

# US 42 - Reject illegitimate dates
def reject_illegitimate_dates(indivs_df: pd.DataFrame, families_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return a tuple of four DataFrames, the first two of which will hold the entries with illegitimate dates from the indivs_df table (birthday then death), the second two of which will hold the entries with illegitimate dates from the families_df table (marriage then divorce)
    :param indivs_df:
    :param families_df:
    :return:
    """

    # get indivs w/ non-null birthdays with illegitimate dates
    for index, (id, birth) in indivs_df[['ID', 'BIRTHDAY']].iterrows():
        print("IMPLEMENT ME! sprint_4_stories.py reject_illegitimate_dates")
        #print("index: {} - id: {} - birth: {}".format(index, id, birth))
        #print("valid: {}".format(date_is_legitimate(birth)))
    return False
