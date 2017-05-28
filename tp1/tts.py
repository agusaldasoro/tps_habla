import os
import sys
import math
from shutil import copyfile
from shutil import rmtree

def main():
    phrase = sys.argv[1]
    fileName = sys.argv[2]

    prosodia = False
    if phrase[-1:] == '?':
        prosodia = True
        phrase = phrase[:-1]

    listOfDiphones = obtainDiphones(phrase)
    diphones = buildWavFiles(listOfDiphones, 'diphones/')

    buildPraatScrip(diphones, 'concatenate.praat', fileName)
    # if not os.path.exists(fileName):
    #     os.makedirs(fileName)
    os.system('praat concatenate.praat')

    if prosodia:
        print('praat extract-pitch-track.praat ' + fileName + ' ' + fileName[:-4] + '.PitchTier 50 300')
        os.system('praat extract-pitch-track.praat ' + fileName + ' ' + fileName[:-4] + '.PitchTier 50 300')
        # convertIntoQuestion(fileName[:-4])
        # os.system('praat reemplazar-pitch-track.praat ' + fileName + ' ' + fileName[:-4] + '-mod.PitchTier ' + fileName[:-4] + '-mod.wav 50 500')
        # copyfile( fileName[:-4] + '-mod.wav',fileName)

    garbageCollector()


def obtainDiphones(aString):
    '''gets diphones from an input strings'''
    aList = []
    aString = '-' + aString + '-'
    for i in range(0, len(aString)-1):
        aList.append(aString[i] + aString[i+1])

    return aList


def buildWavFiles(aListOfDiphones, aWavDirectory):
    '''Copy and rename the necesary wav files to tempWavs'''
    if not os.path.exists('tempWavs/'):
        os.makedirs('tempWavs/')

    files = [ a + '.wav' for a in aListOfDiphones ]
    i = 0
    diphones = []

    for aFile in files:
        copyfile(aWavDirectory + aFile, 'tempWavs/diphone' + str(i) + '.wav')
        diphones.append('tempWavs/diphone' + str(i) + '.wav')
        i += 1

    return diphones


def buildPraatScrip(listOfWavFiles, aPraatFile, anOutputFile):
    '''write and executes a praat script that'll concatenate the wav files
       specified on listOfWavFiles on outputFile'''

    with open(aPraatFile, 'w') as f:
        currentDir = os.getcwd()
        for aFile in listOfWavFiles:
            f.write('Read from file... ' + currentDir + '/' + aFile + '\n')

        f.write('select Sound diphone0'+ '\n')
        for i in range(1,len(listOfWavFiles)):
            f.write('plus Sound diphone' + str(i) + '\n')

        f.write('Concatenate recoverably\n')
        f.write('select Sound chain\n')
        f.write('Save as WAV file... ' + currentDir + anOutputFile)



def parsePitchTier(aPitchTier):

    with open(aPitchTier, 'r') as f:
        f.readline()
        f.readline()
        f.readline()
        _, _, xmin = f.readline().split()
        _, _, xmax = f.readline().split()
        amntOfPoints = f.readline().split()[3]
        points = []
        for i in range(0,int(amntOfPoints)):
            f.readline()
            _,_, number = f.readline().split()
            _,_, value = f.readline().split()
            points.append([float(number),float(value)])

    return xmin, xmax, points

def builPitchTier(aPitchTier, xmin, xmax,points):

    if not os.path.exists(aPitchTier):
        os.makedirs(aPitchTier)

    with open(aPitchTier, 'w') as f:
        f.write('File type = "ooTextFile"\n')
        f.write('Object class = "PitchTier"\n')
        f.write('\n')
        f.write('xmin = ' + xmin +'\n')
        f.write('xmax = ' + xmax+'\n')
        f.write('points: size = ' + str(len(points))+'\n')
        for i in range(0, len(points)):
            num, val = points[i]
            f.write('points [' + str(i+1) + ']:\n')
            f.write('    number = ' + str(num) +'\n')
            f.write('    value = ' + str(val) +'\n')







def convertIntoQuestion(fileName):

    originalPitchTier = fileName + '.PitchTier'
    newPitchTier = fileName + '-mod.PitchTier'
    xmin, xmax, points = parsePitchTier(originalPitchTier)
    #do something with points
    percent = math.floor(len(points)*0.8)
    newPoints = points[:int(percent)]
    _ , newVal = points[int(percent)]
    for i in range(int(percent)+1, len(points)):
        num, value = points[i]
        newVal += 20
        newPoints.append([num,newVal])

    builPitchTier(newPitchTier, xmin, xmax, newPoints)

def garbageCollector():
    rmtree('tempWavs/')



if __name__ == '__main__':
    main()
