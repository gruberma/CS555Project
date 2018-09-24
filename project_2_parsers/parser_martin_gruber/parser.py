#!/usr/bin/env python3
import sys

# Legal tags by level
legal_tags = {0: ['INDI', 'FAM', 'NOTE', 'HEAD', 'TRLR'],
              1: ['NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'HUSB', 'WIFE', 'CHIL', 'DIV'],
              2: ['DATE']}

def parse_line(line):
    level, *rest = line.split(' ')
    level = int(level)

    # Case 0 <id> INDI/FAM
    if level == 0 and len(rest) > 1 and rest[1] in ['INDI', 'FAM']:
        # todo How should we treat arguments after the tag here, are they legal?
        identifier, tag, *_ = rest
        args = [identifier]
    # Case <level> <tag> <arguments>
    else:
        tag, *args = rest

    return level, tag, 'Y' if tag in legal_tags[level] else 'N', " ".join(args)


def parse_file(file):
    for line in file:
        # Remove newline at the end of each line
        line = line[:-1]
        print('--> ', line)
        print('<-- ', "|".join(map(str, parse_line(line))))


if __name__ == '__main__':
    parse_file(open(sys.argv[1]))
