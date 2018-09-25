# CS-555 Project 2
# Chengzhi Yang - 10441351
# Python 3.7

from sys import argv

SUPPORTED_TAGS = ['INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM',
                  'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE', 'HEAD', 'TRLR', 'NOTE']

filePath = None
if len(argv) > 1:
    filePath = argv[1]
if filePath == None:
    filePath = "made_up_family_Chengzhi_Yang.ged"

lines = None
with open(filePath) as f:
    lines = f.read().splitlines()

if lines:
    for line in lines:
        print('-->', line)
        params = line.split(' ')
        isSupport = 'N'
        if len(params) > 2 and (params[2] == 'INDI' or params[2] == 'FAM'):
            if params[2] in SUPPORTED_TAGS:
                isSupport = 'Y'
            restInfo = ' '.join(params[3:])
            if len(restInfo) > 0:
                restInfo = '|' + restInfo
            print('<--', params[0] + '|' + params[2] + '|' + isSupport + '|' + params[1] + restInfo)
        else:
            if params[1] in SUPPORTED_TAGS:
                isSupport = 'Y'
            restInfo = ' '.join(params[2:])
            if len(restInfo) > 0:
                restInfo = '|' + restInfo
            print('<--', params[0] + '|' + params[1] + '|' + isSupport + restInfo)