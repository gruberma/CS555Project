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
from sprint_1_stories import *
from sprint_2_stories import *
from sprint_3_stories import *
from sprint_4_stories import *

def run_all_checks(filename: str):
    indivs_df, families_df = gedcomParser.fileToDataframes.parseFileToDFs(filename)

    print("\nIndividuals:")
    print(tabulate_df(indivs_df))
    print()
    print("Families:")
    print(tabulate_df(order_siblings_by_age(indivs_df, families_df)))
    print()

    print("\n+---------------------------------------------+")
    print("|NOTE: US 41 and US 42 print above the tables!|")
    print("+---------------------------------------------+\n")
    ## Sprint 1
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
    if not merge.empty:
        for index, (indiv_id, marr) in merge[['ID', 'MARRIED']].iterrows():
            print("ERROR: INDIVIDUAL: US08: {}: Individual's birthday is before parents' marriage date -  {}".format(indiv_id, marr))

    ## Sprint 2
    # US 09
    mom = birth_before_parents_death_mother(indivs_df, families_df)
    dad = birth_before_parents_death_father(indivs_df, families_df)
    for index, (indiv_id, birth, mother_id, death) in mom.iterrows():
        print("ERROR: INDIVIDUAL: US09: {}: Individual's birthday is after mother's death date - {} Mother: {} - {}".format(indiv_id, birth, mother_id, death))
    for index, (indiv_id, birth, father_id, death) in dad.iterrows():
        print("ERROR: INDIVIDUAL: US09: {}: Individual's birthday is after father's death date - {} Father: {} - {}".format(indiv_id, birth, father_id, death))

    # US 10
    for index, (indiv_id, age) in marriage_before_14(indivs_df, families_df)[['ID', 'AGE_MARRIED']].iterrows():
        print("ERROR: INDIVIDUAL: US10: {}: Individual married before the age of 14 - Age at marriage: {}".format(indiv_id, age))

    # US 12
    for index, (indiv_id, mother_id, diff_age) in mother_too_old(indivs_df, families_df)[['ID', 'ID_idv_mother', 'DIFF_MOTHER']].iterrows():
        print("ERROR: INDIVIDUAL: US12: {}'s mother {} is too old. Older then individual {} years.".format(indiv_id, mother_id, diff_age))
    for index, (indiv_id, father_id, diff_age) in father_too_old(indivs_df, families_df)[['ID', 'ID_idv_father', 'DIFF_FATHER']].iterrows():
        print("ERROR: INDIVIDUAL: US12: {}'s father {} is too old. Older then individual {} years.".format(indiv_id, father_id, diff_age))

    # US 14
    for index, (fams_id, birthday, nums) in multiple_births_5(indivs_df, families_df)[['CHILD', 'BIRTHDAY', 'CHILDREN']].iterrows():
        print("ERROR: FAMILY: US14: {} have {} birth which more than 5 birth in same day: {}.".format(fams_id, nums, birthday))

    # US 15
    for family_id in fewer_than_15_siblings(indivs_df, families_df)["ID"]:
        print("ERROR: FAMILY: US15: In family {} there are more then 14 children.".format(family_id))

    # US 16
    for index, (child_id, child_name, father_name) in same_male_last_name(indivs_df, families_df)[["ID", "NAME", "HUSBAND NAME"]].iterrows():
        print("ERROR: INDIVIDUAL: US16: {} name is: {}. Fathers name is: {}".format(child_id, child_name, father_name))

    # US 18
    for index, (id_fam, id_husb, id_wife) in siblings_should_not_marry(indivs_df, families_df)[['ID_fam', 'ID_HUSBAND', 'ID_WIFE']].iterrows():
        print("ERROR: INDIVIDUAL: US18: {} and {} are siblings but they are married in family {}".format(id_husb, id_wife, id_fam))

    # US 21
    for index, (id, id_fam) in correct_gender_for_role(indivs_df, families_df)[['ID', 'ID_fam']].iterrows():
        print("ERROR: INDIVIDUAL: US21: {} has the wrong gender role in family {}".format(id, id_fam))


    ## Sprint 3
    # US 22
    for index, series in unique_ids(indivs_df, families_df)[['ID']].iterrows():
        print("ERROR: INDIVIDUAL/FAMILY: US22: ID {} already exists".format(series["ID"]))

    # US 23
    for index, (name, birthday) in list_unique_name_birthday(indivs_df)[['NAME', 'BIRTHDAY']].iterrows():
        print("ERROR: INDIVIDUAL: US23: Name: {} and Birthday: {} already exists".format(name, birthday))

    # US 25
    for index, (id, name, birthday) in unique_first_names_in_families(indivs_df, families_df)[['ID', 'NAME', 'BIRTHDAY']].iterrows():
        print("ERROR: INDIVIDUAL: US25: Individual with ID {} has same name ({}) and birthday ({}) as other individual in the family".format(id, name, birthday))

    # US 29
    for index, (id, birth, death) in list_deceased(indivs_df)[['ID', 'BIRTHDAY', 'DEATH']].iterrows():
        print("NOTICE: INDIVIDUAL: US29: {} is dead. BIRTHDAY: {} - DEATH DATE: {}".format(id, birth, death))

    # US 30
    for index, (id, name) in list_living_married(indivs_df)[['ID', 'NAME']].iterrows():
        print("NOTICE: INDIVIDUAL: US30: Individual with ID: {} Name: {} are living and married".format(id, name))

    # US 31
    for index, (id, age) in list_living_single_older_than_30(indivs_df)[['ID', 'AGE']].iterrows():
        print("NOTICE: INDIVIDUAL: US31: {} has never been married and is older than 30 with an age of {}".format(id, age))


    ## Sprint 4

    # US 32
    for index, (id, birth, child) in multipleBirths(indivs_df)[['ID', 'BIRTHDAY', 'CHILD']].iterrows():
        print("NOTICE: INDIVIDUAL: US32: {} is one of multiple children born to the {} family on {}".format(id, child, birth))

    # US 42 && 41
    # !!! Stories implemented in fileToDicts.py via methods date_is_legitimate() and finish_date(), along with some editing of parse_date() !!!

    # US 35
    for index, (id, name) in list_recent_births(indivs_df)[['ID', 'NAME']].iterrows():
        print("NOTICE: INDIVIDUAL: US35: {} was born in the last 30 days".format(name))

    # US 36
    for index, (id, name) in list_recent_deaths(indivs_df)[['ID', 'NAME']].iterrows():
        print("NOTICE: INDIVIDUAL: US36: {} died in the last 30 days".format(name))

    # US 37
    for index, (id, spouses, desc) \
            in list_recent_survivors(indivs_df, families_df)[['ID', 'living spouses', 'living descendants']].iterrows():
        print("NOTICE: INDIVIDUAL: US37: {} died in the last 30 days. He/She leaves behind his/her spouse(s) {} and "
              "his/her descendant {}".format(id, spouses, desc))

    # US 38
    for index, (id, name, days_to_birthday) in list_upcoming_birthday(indivs_df)[['ID', 'NAME', 'DAYS_TO_BIRTHDAY']].iterrows():
        print("NOTICE: INDIVIDUAL: US38: {} {}'s birthdays occur in the next 30 days ({} days) ".format(id, name, days_to_birthday))

    # US 39
    for index, (hus_name, wife_name, DAYS_TO_ANNIVERSARY) in list_upcoming_anniversaries(families_df)[['HUSBAND NAME', 'WIFE NAME', 'DAYS_TO_ANNIVERSARY']].iterrows():
        print("NOTICE: INDIVIDUAL: US39: Couple {} {}'s anniversary occur in the next 30 days ({} days) ".format(hus_name, wife_name, DAYS_TO_ANNIVERSARY))

    # US 33
    for id in list_orphans(indivs_df, families_df):
        print("NOTICE: INDIVIDUAL: US33: Individual with id {} is an orphan ".format(id))

    # US 13
    for (sib_id1, sib_id2, days) in siblings_spacing(indivs_df, families_df):
        print("NOTICE: INDIVIDUAL: US13: Siblings with ids {} and {} were born {} days apart, violating sibling spacing".format(sib_id1, sib_id2, days))


if __name__ == "__main__":
    # input parsing
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<gedcom filepath>")
    else:
        run_all_checks(sys.argv[1])
