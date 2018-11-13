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
