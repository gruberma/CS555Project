from . import fileToDicts
import pandas as pd
import sys
from tabulate import tabulate
from typing import Tuple
import numpy as np
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
from datetime import date


indivs_columns = ['ID', 'NAME', 'GENDER', 'BIRTHDAY', 'AGE', 'AGE_in_days', 'ALIVE', 'DEATH', 'CHILD', 'SPOUSE']
fams_columns = ['ID', 'MARRIED', 'DIVORCED', 'HUSBAND ID', 'HUSBAND NAME', 'WIFE ID', 'WIFE NAME', 'CHILDREN']


def parseFileToDFs(filename: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    indivs, families = fileToDicts.parseFile(filename)
    indivs_df = pd.DataFrame(indivs)
    families_df = pd.DataFrame(families)

    if indivs_df.empty:
        indivs_df = pd.DataFrame(columns=indivs_columns)
    else:
        # Add missing columns
        for col in indivs_columns:
            if col not in indivs_df.columns:
                indivs_df[col] = np.nan
        # Calculate age
        indivs_df['AGE'] = [None if pd.isna(birth) else
                relativedelta(date.today() if pd.isna(death) else parse_date(death), parse_date(birth)).years
                for birth, death in zip(indivs_df['BIRTHDAY'], indivs_df['DEATH'])]
        indivs_df['AGE_in_days'] = [None if pd.isna(birth) else
                            ((date.today() if pd.isna(death) else parse_date(death).date()) - parse_date(birth).date()).days
                            for birth, death in zip(indivs_df['BIRTHDAY'], indivs_df['DEATH'])]
        # Calculate alive
        indivs_df['ALIVE'] = [pd.isna(death) or parse_date(death).date() > date.today()
                for death in indivs_df['DEATH']]
        # Reorder columns
        indivs_df = indivs_df[indivs_columns]

    if families_df.empty:
        families_df = pd.DataFrame(columns=fams_columns)
    else:
        # Add missing columns
        for col in fams_columns:
            if col not in families_df:
                families_df[col] = np.nan
        # Reorder columns
        families_df = families_df[fams_columns]

    return indivs_df, families_df
