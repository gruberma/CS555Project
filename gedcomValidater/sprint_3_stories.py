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
