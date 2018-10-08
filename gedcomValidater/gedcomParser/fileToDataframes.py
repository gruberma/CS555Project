#!/usr/bin/env python3

from . import fileToDicts
import pandas as pd
import sys
from tabulate import tabulate
from typing import Tuple
import numpy as np
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
from datetime import date


def parseFileToDFs(filename: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    indivs, families = fileToDicts.parseFile(filename)
    indivs_df = pd.DataFrame(indivs)
    families_df = pd.DataFrame(families)

    indivs_columns = ['ID', 'NAME', 'GENDER', 'BIRTHDAY', 'AGE', 'ALIVE', 'DEATH', 'CHILD', 'SPOUSE']
    fams_columns = ['ID', 'MARRIED', 'DIVORCED', 'HUSBAND ID', 'HUSBAND NAME', 'WIFE ID', 'WIFE NAME', 'CHILDREN']

    if indivs_df.empty:
        indivs_df = pd.DataFrame(columns=indivs_columns)
    else:
        # Calculate age
        indivs_df['AGE'] = [np.nan if birth is np.nan else
                relativedelta(parse_date(death) if death is not np.nan else date.today(), parse_date(birth)).years
                for birth, death in zip(indivs_df['BIRTHDAY'], indivs_df['DEATH'])]
        # Calculate alive
        indivs_df['ALIVE'] = [birth is not np.nan and death is not np.nan
                for birth, death in zip(indivs_df['BIRTHDAY'], indivs_df['DEATH'])]
        # Reorder columns
        indivs_df = indivs_df[indivs_columns]

    if families_df.empty:
        families_df = pd.DataFrame(columns=fams_columns)
    else:
        # Reorder columns
        families_df = families_df[fams_columns]

    return indivs_df, families_df


def printTables(filename: str):
    indivs_df, families_df = parseFileToDFs(filename)
    print('Individuals')
    print(tabulate(indivs_df, headers='keys', tablefmt='psql'))
    print('Families')
    print(tabulate(families_df, headers='keys', tablefmt='psql'))


if __name__ == "__main__":
    # input parsing
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<gedcom filepath>")
    else:
        printTables(sys.argv[1])
