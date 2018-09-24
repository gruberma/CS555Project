valid_tags = ['SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'MARR', 'HUSB', 'WIFE',
              'CHIL', 'DIV', 'HEAD', 'TRLR', 'NOTE']
special_tags_1 = ["INDI", "FAM"]
date_tag = "DATE"
name_tag = "NAME"

with open("data_1.ged", "r") as file:
    lines = file.readlines()
    file.close()

output_lines = []
for line in lines:
    level, tag, *rest = line.split()
    valid = None
    output_lines.append("--> " + line)

    if tag not in valid_tags:
        if rest and rest[0] in special_tags_1:
            valid = 'Y'
            output = "<-- {}|{}|{}|{}\n".format(level, rest[0], valid, tag)
            output_lines.append(output)
        elif tag == date_tag and level == '2':
            valid = 'Y'
            output = "<-- {}|{}|{}|{}\n".format(level, tag, valid, " ".join(rest))
            output_lines.append(output)
        elif tag == name_tag and level == '1':
            valid = 'Y'
            output = "<-- {}|{}|{}|{}\n".format(level, tag, valid, " ".join(rest))
            output_lines.append(output)
        else:
            valid = 'N'
            output = "<-- {}|{}|{}|{}\n".format(level, tag, valid, " ".join(rest))
            output_lines.append(output)
    else:
        valid = 'Y'
        output = "<-- {}|{}|{}|{}\n".format(level, tag, valid, " ".join(rest))
        output_lines.append(output)

with open("output_file.txt", "w") as file:
    file.writelines(output_lines)
