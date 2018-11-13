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
