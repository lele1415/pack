#!/usr/bin/env python
#coding=utf-8
# Version: v1.0
# Date: 2017/09/04
# Author: chenxs

# 参数：
# --name=xxx   指定新文件夹名称
# -v         拷贝verified文件
# --ota=
#       tf -> /obj/PACKAGING/target_files_intermediates/[product]-target_files-[time]
#       tfp -> /target_files-package.zip
#       ota -> /[product]-ota-[time]

import sys
import commands
import shutil
import os
import glob
################################
# print color function
################################
def red(sText):
    return '\033[0;31m' + sText + '\033[0m'
def green(sText):
    return '\033[0;32m' + sText + '\033[0m'
def yellow(sText):
    return '\033[0;33m' + sText + '\033[0m'
def greenAndYellow(sText1, sText2):
    return green(sText1) + yellow(sText2)

################################
# set default encoding to 'utf8'
################################
reload(sys)
sys.setdefaultencoding('utf8')

################################
# get args
################################
def getArgValue(argStr):
    if '=' in argStr:
        return argStr.split('=')[1].rstrip()
    return ''

mDirName = ''
mVerifiedFlag = False
mOtaArg = ''
if len(sys.argv) > 0:
    for argStr in sys.argv:
        if '--name' in argStr:
            mDirName = getArgValue(argStr)
        elif '-v' in argStr:
            mVerifiedFlag = True
        elif '--ota' in argStr:
            mOtaArg = getArgValue(argStr)

################################
# get command output
################################
def getCommandOutput(sCommand):
    (status, output) = commands.getstatusoutput(sCommand)
    return output

################################
# check target folder
################################
path_ROM = '../ROM/'

if mDirName != '':
    path_packDir = '../ROM/' + mDirName + '/'
else:
    path_packDir = '../ROM/pack_tmp/'

if not os.path.exists(path_ROM):
    os.makedirs(path_ROM)
if os.path.exists(path_packDir):
    shutil.rmtree(path_packDir)
os.makedirs(path_packDir)

################################
# check out path exist
################################
def checkPathExists(filePath, exitFlag):
    if not os.path.exists(filePath):
        if exitFlag:
            print("File is not exist:\n" + filePath)
            sys.exit(0)
        else:
            return False
    return True

path_out_product = "out/target/product/"

checkPathExists(path_out_product, True)

################################
# get product path
################################
def getSelectValue(showStr, valueDict, valueList):
    while 1:
        valueInput = raw_input("Select a project:\n" + showStr)
        valueDict = valueDict.get(str(valueInput), "")
        if valueDict != "":
            valueSelet = valueDict
            break
        if valueInput in valueList:
            valueSelet = valueInput
            break
    return valueSelet

def getAndSelectMultiFolder(folderlist):
    folderNameDict = {}
    folderNameStr = ""
    i = 0
    for folderName in folderlist:
        i = i + 1
        folderNameDict[str(i)] = folderName
        folderNameStr = folderNameStr + str(i) + ". " + folderName + "\n"
    return getSelectValue(folderNameStr, folderNameDict, folderlist)

mProductsList = os.listdir(path_out_product)
for path in mProductsList:
    if not os.path.isdir(path):
        mProductsList.remove(path)

if len(mProductsList) > 1:
    mProduct = getAndSelectMultiFolder(mProductsList)
elif len(mProductsList) == 1 :
    mProduct = mProductsList[0]
else:
    print("out/target/product/为空目录")
    sys.exit(0)

path_out_root = "out/target/product/" + mProduct + "/"

################################
# check DB files path
################################
path_AP_list = [path_out_root + 'obj/CGEN/', path_out_root + 'obj/CODEGEN/cgen/']
path_BP_list = [path_out_root + 'system/etc/mddb/', path_out_root + 'system/vendor/etc/mddb/']
APFile = ''
BPFile = ''

def findDirInList(dirList):
    for d in dirList:
        if os.path.exists(d):
            return d
    return ''

def findFileInDir(dirPath, sKey, multiFiles):
    if os.path.exists(dirPath):
        filesList = os.listdir(dirPath)
        if len(filesList) > 0:
            if multiFiles:
                getedFilesList = []
                for file in filesList:
                    if sKey in file:
                        getedFilesList.append(file)
                return getedFilesList
            else:
                for file in filesList:
                    if sKey in file:
                        return file
    return ''

path_AP_root = findDirInList(path_AP_list)
APFile = findFileInDir(path_AP_root, '_ENUM', False).rstrip('_ENUM')
if APFile == '':
    print('未找到AP文件')

path_BP_root = findDirInList(path_BP_list)
BPFiles = findFileInDir(path_BP_root, 'BPLGU', True)

##################################################
# get file names for copy in *_Android_scatter.txt
##################################################
path_scatter = glob.glob(r"out/target/product/" + mProduct + "/*_Android_scatter.txt")[0]

packFilesList = [path_scatter.lstrip(path_out_root)]
fp = open(path_scatter,'r')
for line in fp.readlines():
    if 'file_name' in line:
        if not 'NONE' in line:
            fileName = line.split(':')[1].strip()
            if not fileName in packFilesList:
                packFilesList.append(fileName)
if not len(packFilesList) > 0:
    print('未找到文件')
    sys.exit(0)
fp.close()

################################
# get verified files
################################
if mVerifiedFlag:
    mVerifiedFilesList = []
    outFilesList = os.listdir(path_out_root)
    for fileName in outFilesList:
        if '-verified' in fileName:
            mVerifiedFilesList.append(fileName)

################################
# get OTA file
################################
if mOtaArg != '':
    mOtaFile = ''
    mOtaPath = ''

    if mOtaArg == 'tf':
        mOtaPath = 'obj/PACKAGING/target_files_intermediates/'
        tfFilesList = os.listdir(path_out_root + mOtaPath)
        filesList = []
        for fileName in tfFilesList:
            if ('-target_files-' in fileName) and (fileName.endswith('.zip')):
                filesList.append(fileName)
        filesList.sort()
        mOtaFile = filesList[len(filesList) - 1]

    elif mOtaArg == 'tfp':
        mOtaFile = 'target_files-package.zip'

    elif mOtaArg == 'ota':
        outFilesList = os.listdir(path_out_root)
        for fileName in outFilesList:
            if ('-ota-' in fileName) and (fileName.endswith('.zip')):
                mOtaFile = fileName

################################
# get and copy DB files
################################
if APFile != '' or len(BPFiles) > 0:
    path_DB = path_packDir + 'DB/'
    os.makedirs(path_DB)
    print(red('########## DB files ##########'))
    if APFile != '':
        shutil.copyfile(path_AP_root + APFile, path_DB + APFile)
        print(greenAndYellow('copy ', path_DB + APFile))
    if len(BPFiles) > 0:
        for BPFile in BPFiles:
            shutil.copyfile(path_BP_root + BPFile, path_DB + BPFile)
            print(greenAndYellow('copy ', path_DB + BPFile))

################################
# copy firmware files
################################
print(red('########## Firmware files ##########'))
for packFile in packFilesList:
    shutil.copyfile(path_out_root + packFile, path_packDir + packFile)
    print(greenAndYellow('copy ', path_packDir + packFile))

################################
# copy verified files
################################
if mVerifiedFlag:
    print(red('########## Verified files ##########'))
    for verifiedFile in mVerifiedFilesList:
        shutil.copyfile(path_out_root + verifiedFile, path_packDir + verifiedFile)
        print(greenAndYellow('copy ', path_packDir + verifiedFile))

################################
# copy ota file
################################
if mOtaFile != '':
    path_OTA = path_packDir + 'OTA/'
    os.makedirs(path_OTA)
    print(red('########## OTA file ##########'))
    shutil.copyfile(path_out_root + mOtaPath + mOtaFile, path_OTA + mOtaFile)
    print(greenAndYellow('copy ', path_OTA + mOtaFile))

print(red('########## End ##########'))
