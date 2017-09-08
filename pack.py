#!/usr/bin/env python
#coding=utf-8
# Version: v1.0
# Date: 2017/09/07
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

PATH_ROM = '../ROM/'
PATH_OUT_PRODUCT = "out/target/product/"

mTargetFolerName = 'pack_tmp'
mTargetFolderPath = ''
mCopyVerified = False
mCopyOTA = False
mArgOTA = ''

mOutRootPath = ''
mAPFilePath = ''
mAPFileName = ''
mBPFilesPath = ''
mBPFilesName = []
mFirmwareFilesList = []
mVerifiedFilesList = []
mOtaFile = ''
mOtaPath = ''
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
def setEncodingToUTF8():
    reload(sys)
    sys.setdefaultencoding('utf8')

################################
# get args
################################
def getArgValue(argStr):
    if '=' in argStr:
        return argStr.split('=')[1].rstrip()
    return ''

def getAllArgs():
    global mTargetFolerName
    global mCopyVerified
    global mCopyOTA
    global mArgOTA
    if len(sys.argv) > 0:
        for argStr in sys.argv:
            if '--name' in argStr:
                mTargetFolerName = getArgValue(argStr)
            elif '-v' in argStr:
                mCopyVerified = True
            elif '--ota' in argStr:
                mArgOTA = getArgValue(argStr)
                mCopyOTA = True

################################
# get command output
################################
def getCommandOutput(sCommand):
    (status, output) = commands.getstatusoutput(sCommand)
    return output

################################
# check is wifi platform
################################
def isWifiPlatform():
    codePath = getCommandOutput('pwd')
    if ("8127" in codePath) or ("8163" in codePath) or ("8167" in codePath):
        return True
    else:
        return False

################################
# check ROM path
################################
def checkRomPath():
    if not os.path.exists(PATH_ROM):
        os.makedirs(PATH_ROM)

################################
# check target folder path
################################
def checkTargetFolderPath(targetFolderPath):
    if os.path.exists(targetFolderPath):
        shutil.rmtree(targetFolderPath)
    os.makedirs(targetFolderPath)

################################
# get product path
################################
def getSelectValue(showStr, valueDict, valueList):
    while 1:
        valueInput = raw_input("Select:\n" + showStr)
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

def getOutRootPath():
    global mOutRootPath
    foldersList = os.listdir(PATH_OUT_PRODUCT)

    for path in foldersList:
        if not os.path.isdir(PATH_OUT_PRODUCT + path):
            foldersList.remove(path)

    if len(foldersList) > 1:
        mProduct = getAndSelectMultiFolder(foldersList)
    elif len(foldersList) == 1 :
        mProduct = foldersList[0]
    else:
        print("out/target/product/为空目录")
        sys.exit(0)
    
    mOutRootPath = "out/target/product/" + mProduct + "/"

################################
# get DB files path
################################
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

def getAPFile():
    global mAPFilePath
    global mAPFileName
    AP_PathList = [mOutRootPath + 'obj/CGEN/', mOutRootPath + 'obj/CODEGEN/cgen/']
    mAPFilePath = findDirInList(AP_PathList)
    if mAPFilePath != '':
        mAPFileName = findFileInDir(mAPFilePath, '_ENUM', False).rstrip('_ENUM')
        if mAPFileName != '':
            return
    print(red('未找到AP文件'))

def getBPFiles():
    global mBPFilesPath
    global mBPFilesName
    BP_PathList = [mOutRootPath + 'system/etc/mddb/', mOutRootPath + 'system/vendor/etc/mddb/']
    mBPFilesPath = findDirInList(BP_PathList)
    if mBPFilesPath != '':
        mBPFilesName = findFileInDir(mBPFilesPath, 'BPLGU', True)
        if len(mBPFilesName) > 0:
            return
    print(red('未找到BP文件'))

##################################################
# get file names for copy in *_Android_scatter.txt
##################################################
def getScatterFile():
    return glob.glob(r'' + mOutRootPath + "/*_Android_scatter.txt")

def getOtherFirmwareFiles(scatterFileList):
    global mFirmwareFilesList
    if len(scatterFileList) > 1:
        scatterFilePath = getAndSelectMultiFolder(scatterFileList)
    else:
        scatterFilePath = scatterFileList[0]

    scatterFileName = scatterFilePath.lstrip(mOutRootPath)
    mFirmwareFilesList = [scatterFileName]

    fp = open(scatterFilePath,'r')
    for line in fp.readlines():
        if 'file_name' in line:
            if not 'NONE' in line:
                fileName = line.split(':')[1].strip()
                if not fileName in mFirmwareFilesList:
                    mFirmwareFilesList.append(fileName)
    fp.close()
    
    
def getFirmwareFiles():
    scatterFileList = getScatterFile()
    if len(scatterFileList) > 0:
        getOtherFirmwareFiles(scatterFileList)
    else:
        print('未找到文件')
        sys.exit(0)

################################
# get verified files
################################
def getVerifiedFiles():
    global mVerifiedFilesList
    outFilesList = os.listdir(mOutRootPath)
    for fileName in outFilesList:
        if '-verified' in fileName:
            mVerifiedFilesList.append(fileName)

################################
# get OTA file
################################
def getOtaFile():
    global mCopyOTA
    global mOtaFile
    global mOtaPath
    if mArgOTA == 'tf':
        mOtaPath = 'obj/PACKAGING/target_files_intermediates/'
        tfFilesList = os.listdir(mOutRootPath + mOtaPath)
        filesList = []
        for fileName in tfFilesList:
            if ('-target_files-' in fileName) and (fileName.endswith('.zip')):
                filesList.append(fileName)
        if len(filesList) > 0:
            if len(filesList) > 1:
                filesList.sort()
            mOtaFile = filesList[len(filesList) - 1]
        else:
            mCopyOTA = False

    elif mArgOTA == 'tfp':
        mOtaFile = 'target_files-package.zip'
        if not os.path.exists(mOutRootPath + mOtaFile):
            mCopyOTA = False

    elif mArgOTA == 'ota':
        outFilesList = os.listdir(mOutRootPath)
        for fileName in outFilesList:
            if ('-ota-' in fileName) and (fileName.endswith('.zip')):
                mOtaFile = fileName
        if mOtaFile == '':
            mCopyOTA = False
    else:
        mCopyOTA = False

################################
# get and copy DB files
################################
def copyAPFile(targetPath_DB):
        shutil.copyfile(mAPFilePath + mAPFileName, targetPath_DB + mAPFileName)
        print(greenAndYellow('copy ', targetPath_DB + mAPFileName))
    
def copyBPFile(targetPath_DB):
    for BPFile in mBPFilesName:
        shutil.copyfile(mBPFilesPath + BPFile, targetPath_DB + BPFile)
        print(greenAndYellow('copy ', targetPath_DB + BPFile))

def copyDBFile():
    targetPath_DB = mTargetFolderPath + 'DB/'
    os.makedirs(targetPath_DB)

    if mAPFileName != '':
        copyAPFile(targetPath_DB)

    if len(mBPFilesName) > 0:
        copyBPFile(targetPath_DB)

################################
# copy firmware files
################################
def copyFirmwareFiles():
    for packFile in mFirmwareFilesList:
        shutil.copyfile(mOutRootPath + packFile, mTargetFolderPath + packFile)
        print(greenAndYellow('copy ', mTargetFolderPath + packFile))

################################
# copy verified files
################################
def copyVerifiedFiles():
    for verifiedFile in mVerifiedFilesList:
        shutil.copyfile(mOutRootPath + verifiedFile, mTargetFolderPath + verifiedFile)
        print(greenAndYellow('copy ', mTargetFolderPath + verifiedFile))

################################
# copy ota file
################################
def copyOtaFile():
    path_OTA = mTargetFolderPath + 'OTA/'
    os.makedirs(path_OTA)
    shutil.copyfile(mOutRootPath + mOtaPath + mOtaFile, path_OTA + mOtaFile)
    print(greenAndYellow('copy ', path_OTA + mOtaFile))

def main():
    setEncodingToUTF8()
    getAllArgs()

    # check target path
    global mTargetFolderPath
    mTargetFolderPath = PATH_ROM + mTargetFolerName + '/'
    checkRomPath()
    checkTargetFolderPath(mTargetFolderPath)

    if not os.path.exists(PATH_OUT_PRODUCT):
        print('路径不存在: ' + PATH_OUT_PRODUCT)
        sys.exit(0)

    # get files
    getOutRootPath()

    getAPFile()

    if not isWifiPlatform():
        getBPFiles()

    getFirmwareFiles()

    if mCopyVerified:
        getVerifiedFiles()

    if mCopyOTA:
        getOtaFile()

    # start copy
    print(red('########## DB files ##########'))
    copyDBFile()

    print(red('########## Firmware files ##########'))
    copyFirmwareFiles()

    if mCopyVerified:
        print(red('########## Verified files ##########'))
        copyVerifiedFiles()

    if mCopyOTA:
        print(red('########## OTA file ##########'))
        copyOtaFile()

    print(red('########## End ##########'))

if __name__ == "__main__":
    main()
