#!/usr/bin/env python3
"""GEDCOM Parser
usage: ./fileToDicts.py <gedcom filepath>"""

# Description:
# last_level_0 and last_level_1 are used to track what the last tag of that
# level was (for purposes of detecting context)
#
# cur_individual and cur_family are used to build an individual or family entry
#
# individual_list and family_list hold all individual and family entries


import sys
import re

last_level_0 = ""
last_level_1 = ""

cur_individual = {}
cur_family = {}

individual_list = []
family_list = []


def parseFile(filename: str):
    """main method"""
    # bring global variables into scope
    global cur_individual
    global cur_family
    global individual_list
    global family_list

    # reset global variables
    last_level_0 = ""
    last_level_1 = ""
    cur_individual = {}
    cur_family = {}
    individual_list = []
    family_list = []

    with open(filename) as file:
        # strips file into lines
        lines = [line.rstrip('\n') for line in file]
        # parse each line
        for line in lines:
            # tokenizes line by spaces
            line_tokens = re.sub("[^\w.*/@]", " ", line).split()
            # prints line input
            # print("-->", " ".join(str(e) for e in line_tokens))
            # checks if it is a tag that we accept (if not, then prints generic "N" message)
            if not is_level_zero_tag(line_tokens) and not is_level_one_tag(line_tokens) and not is_level_two_tag(
                    line_tokens):
                pass
                # write_it(["<-- ", line_tokens[0], "|", line_tokens[1], "|N|", " ".join(str(e) for e in line_tokens[2:]), "\n"])
        # appends current individual to individual_list
        if individual_list:
            individual_list.append(cur_individual)
        # appends current family to family_list
        if cur_family != {}:
            family_list.append(cur_family)

        for indi in individual_list:
            # need to go through each individual and, for each family of which that individual
            # is a child, check that it is in the family
            # TODO isn't this a story?
            cid = indi["CHILD"]
            for family in family_list:
                if cid == family["ID"]:
                    if not indi["ID"] in family["CHILDREN"]:
                        family["CHILDREN"].add(indi["ID"])

        return individual_list, family_list


# stupid function I wrote, not realizing that you can do something similar with regular print function.
# Too tired to change it, it works
def write_it(token_list):
    """write single line, no spaces to stdout"""
    for item in token_list:
        sys.stdout.write(item)
    print("")


# checks if tokens represent level zero tag, parsing the arguments for correctness
def is_level_zero_tag(tokens):
    global last_level_0
    """Returns bool representing whether or not it is a valid level 0 tag"""
    ret_val = False
    # if first token is not a digit or is not equal to zero, it is a poorly formatted
    # line and returns false
    if not tokens[0].isdigit() or int(tokens[0]) != 0:
        return ret_val
    switch = {
        "INDI": True,
        "FAM": True,
        "HEAD": True,
        "TRLR": True,
        "NOTE": True,
    }
    # checks if 2nd or 3rd token (index 1 or 2) is a valid tag, and then checks the corresponding arguments,
    # updating last_level_0 appropriately
    if switch.get(tokens[1], False):
        if tokens[1] == "HEAD" or tokens[1] == "TRLR":
            ret_val = parse_head_trlr(tokens)
        if tokens[1] == "NOTE":
            ret_val = parse_note(tokens)
        last_level_0 = tokens[1]
    elif len(tokens) == 3 and switch.get(tokens[2], False):
        if tokens[2] == "INDI" or tokens[2] == "FAM":
            ret_val = parse_indi_fam(tokens)
        ret_val = True
        last_level_0 = tokens[2]
    return ret_val


# checks if tokens represent level one tag, parsing the arguments for correctness
def is_level_one_tag(tokens):
    """Returns bool representing whether or not it is a valid level 1 tag"""
    global last_level_1
    ret_val = False
    # if first token is not a digit or is not equal to zero, it is a poorly formatted
    # line and returns false
    if not tokens[0].isdigit() or int(tokens[0]) != 1:
        return ret_val
    switch = {
        "NAME": True,
        "SEX": True,
        "BIRT": True,
        "DEAT": True,
        "FAMC": True,
        "FAMS": True,
        "MARR": True,
        "HUSB": True,
        "WIFE": True,
        "CHIL": True,
        "DIV": True,
    }
    # checks if 2nd or 3rd token (index 1 or 2) is a valid tag, and then checks the corresponding arguments,
    # updating last_level_1 appropriately
    #
    # if it is a valid tag, it updates the cur_individual or cur_family variables appropriately according to
    # context indicated by the last_level_0
    if switch.get(tokens[1], False):
        if tokens[1] == "NAME":
            if last_level_0 == "INDI":
                ret_val = parse_name(tokens)
                if ret_val:
                    last_level_1 = tokens[1]
            else:
                ret_val = False
        elif tokens[1] == "SEX":
            if last_level_0 == "INDI":
                ret_val = parse_sex(tokens)
                if ret_val:
                    last_level_1 = tokens[1]
            else:
                ret_val = False
        elif tokens[1] == "BIRT" or tokens[1] == "DEAT":
            if last_level_0 == "INDI":
                ret_val = parse_birt_deat_marr_div(tokens)
                if ret_val:
                    last_level_1 = tokens[1]
            else:
                ret_val = False
        elif tokens[1] == "MARR" or tokens[1] == "DIV":
            if last_level_0 == "FAM":
                ret_val = parse_birt_deat_marr_div(tokens)
                if ret_val:
                    last_level_1 = tokens[1]
            else:
                ret_val = False
        elif tokens[1] == "FAMC" or tokens[1] == "FAMS":
            if last_level_0 == "INDI":
                ret_val = parse_famc_fams_husb_wife_chil(tokens)
                if ret_val:
                    last_level_1 = tokens[1]
            else:
                ret_val = False
        elif tokens[1] == "HUSB" or tokens[1] == "WIFE" or tokens[1] == "CHIL":
            if last_level_0 == "FAM":
                ret_val = parse_famc_fams_husb_wife_chil(tokens)
                if ret_val:
                    last_level_1 = tokens[1]
            else:
                ret_val = False
    #    elif len(tokens) >= 3 and switch.get(tokens[2], False):
    #        ret_val = True
    return ret_val


# checks if tokens represent level two tag, parsing the arguments for correctness
def is_level_two_tag(tokens):
    """Returns bool representing whether or not it is a valid level 2 tag"""
    ret_val = False
    # if first token is not a digit or is not equal to zero, it is a poorly formatted
    # line and returns false
    if not tokens[0].isdigit() or int(tokens[0]) != 2:
        return ret_val
    switch = {
        "DATE": True,
    }
    # checks if 2nd token (index 1) is a valid tag, and then checks the corresponding arguments
    #
    # if it is a valid tag, it updates the cur_individual or cur_family variables appropriately according to
    # context indicated by the last_level_1
    if switch.get(tokens[1], False):
        if tokens[1] == "DATE":
            if last_level_1 == "BIRT" or last_level_1 == "DEAT" or last_level_1 == "DIV" or last_level_1 == "MARR":
                ret_val = parse_date(tokens)
    return ret_val


# checks if it is a new individual or family. If it is, stores the appropriate old individual or family and creates a new one
def parse_indi_fam(tokens):
    """checks that 'INDI' or 'FAM' was in proper format"""
    global cur_individual
    global cur_family
    global individual_list
    global family_list
    """checks that 'INDI' or 'FAM' was in proper format"""
    if len(tokens) == 3 and (tokens[2] == "INDI" or tokens[2] == "FAM"):
        # write_it(["<-- ", tokens[0], "|", tokens[2], "|Y|", tokens[1]])
        if tokens[2] == "INDI":
            # print("Individual: %s" % (cur_individual))
            if bool(cur_individual):
                individual_list.append(cur_individual)
                cur_individual = {}
            cur_individual["ID"] = tokens[1]
            cur_individual["CHILD"] = None
            cur_individual["SPOUSE"] = None
        elif tokens[2] == "FAM":
            # print("Family: %s" % (cur_family))
            if bool(cur_family):
                family_list.append(cur_family)
                cur_family = {}
            cur_family["ID"] = tokens[1]
            cur_family["CHILDREN"] = {}
        return True
    # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", "".join(str(e) for e in tokens[2:])])
    return False


def parse_head_trlr(tokens):
    """checks that 'HEAD' or 'TRLR' was in proper format"""
    if (tokens[1] == "HEAD" or tokens[1] == "TRLR") and len(tokens) == 2:
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|"])
        return True
    # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", "".join(str(e) for e in tokens[2:])])
    return False


def parse_note(tokens):
    """checks that 'NOTE' was in proper format"""
    if tokens[1] == "NOTE":
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|"])
        return True
    # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", "".join(str(e) for e in tokens[2:])])
    return False


def parse_sex(tokens):
    global cur_individual
    """checks that 'SEX' was in proper format"""
    if tokens[1] == "SEX" and len(tokens) == 3:
        if tokens[2] == "M" or tokens[2] == "F":
            cur_individual["GENDER"] = tokens[2]
            # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|", tokens[2]])
            return True
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", tokens[2]])
        return False
    else:
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", " ".join(str(e) for e in tokens[2:])])
        return False


def parse_birt_deat_marr_div(tokens):
    """checks that 'BIRT' or 'DEAT' or 'MARR' or 'DIV' was in proper format"""
    if (tokens[1] == "BIRT" or tokens[1] == "DEAT" or tokens[1] == "MARR" or tokens[1] == "DIV") and len(tokens) == 2:
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|"])
        return True
    # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", " ".join(str(e) for e in tokens[2:])])
    return False


def parse_name(tokens):
    """checks that 'NAME' was in proper format"""
    global cur_individual
    if tokens[1] == "NAME" and len(tokens) > 3:
        if tokens[len(tokens) - 1][0] == "/" and tokens[len(tokens) - 1][len(tokens[len(tokens) - 1]) - 1] == "/":
            cur_individual["NAME"] = " ".join(tokens[2:])
            # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|", " ".join(str(e) for e in tokens[2:])])
            return True
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", " ".join(str(e) for e in tokens[2:])])
        return False
    else:
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", " ".join(str(e) for e in tokens[2:])])
        return False


def parse_famc_fams_husb_wife_chil(tokens):
    """checks that 'FAMC' or 'FAMS' or 'HUSB' or 'WIFE' or 'CHIL' was in proper format"""
    global cur_family
    global cur_individual
    if (tokens[1] == "FAMC" or tokens[1] == "FAMS" or tokens[1] == "HUSB" or tokens[1] == "WIFE" or tokens[
        1] == "CHIL") and len(tokens) == 3:
        if tokens[1] == "FAMC":
            cur_individual["CHILD"] = tokens[2]
        elif tokens[1] == "FAMS":
            if cur_individual["SPOUSE"] is None:
                cur_individual["SPOUSE"] = {tokens[2]}
            else:
                cur_individual["SPOUSE"].add(tokens[2])
        elif tokens[1] == "HUSB":
            cur_family["HUSBAND NAME"] = lookup_name(tokens[2])
            cur_family["HUSBAND ID"] = tokens[2]
        elif tokens[1] == "WIFE":
            cur_family["WIFE NAME"] = lookup_name(tokens[2])
            cur_family["WIFE ID"] = tokens[2]
        elif tokens[1] == "CHIL":
            if "CHILD ID" in cur_family.keys():
                cur_family["CHILDREN"] = cur_family.get("CHILDREN").add(tokens[2])
            else:
                cur_family["CHILDREN"] = {tokens[2]}
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|", tokens[2]])
        return True
    # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", " ".join(str(e) for e in tokens[2:])])
    return False


def parse_date(tokens):
    """checks that 'DATE' was in proper format"""
    months = {"JAN": True, "FEB": True, "MAR": True, "APR": True, "MAY": True, "JUN": True, "JUL": True, "AUG": True,
              "SEP": True, "OCT": True, "NOV": True, "DEC": True}
    if len(tokens) == 5 and tokens[1] == "DATE" and tokens[2].isdigit() and tokens[2] and months.get(tokens[3], False) and tokens[4].isdigit():
        if last_level_1 == "BIRT":
            cur_individual["BIRTHDAY"] = " ".join(tokens[2:])
        elif last_level_1 == "DEAT":
            cur_individual["DEATH"] = " ".join(tokens[2:])
        elif last_level_1 == "DIV":
            cur_family["DIVORCED"] = " ".join(tokens[2:])
        elif last_level_1 == "MARR":
            cur_family["MARRIED"] = " ".join(tokens[2:])
        # write_it(["<-- ", tokens[0], "|", tokens[1], "|Y|", " ".join(str(e) for e in tokens[2:])])
        return True
    # write_it(["<-- ", tokens[0], "|", tokens[1], "|N|", " ".join(str(e) for e in tokens[2:])])
    return False


def lookup_name(pid):
    """looks up name of husband in current and past individuals"""
    global cur_individual
    global individual_list
    if pid in cur_individual.values():
        return cur_individual.get("NAME")
    for x in individual_list:
        if pid in x.values():
            return x.get("NAME")
    return "NULL_NAME"


if __name__ == "__main__":
    # input parsing
    program_name = sys.argv[0]
    arguments = sys.argv[1:]
    if len(arguments) > 1:
        print("usage:", program_name, "<gedcom filepath>")
    else:
        print(parseFile(arguments[0]))
