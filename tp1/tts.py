import os
import sys
import math
from shutil import copyfile

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



def obtainDiphones(aString):
    '''gets diphones from an input strings
    '''
    aList = []
    dummyString = '-' + aString + '-'
    for i in range(0, len(dummyString)-1):
        aList.append(dummyString[i] + dummyString[i+1])

    return aList


def buildWavFiles(aListOfDiphones, aWavDirectory):
    '''Copy and rename the necesary wav files to tempWavs
    '''
    files = [ a + '.wav' for a in aListOfDiphones]
    i = 0
    diphones = []
    for f in files:
        copyfile(aWavDirectory + f, 'tempWavs/diphone' + str(i) + '.wav')
        diphones.append('tempWavs/diphone' + str(i) + '.wav')
        i += 1
    return diphones

def buildPraatScrip(listOfWavFiles, aPraatFile, anOutputFile):
    '''write and executes a praat script that'll concatenate the wav files specified on listOfWavFiles on outputFile
    '''
    with open(aPraatFile, 'w') as f:
        for aFile in listOfWavFiles:
            f.write('Read from file... /home/ph-02/Documentos/tps_habla/tp1/' + aFile + '\n')
        f.write('select Sound diphone0'+ '\n')
        for i in range(1,len(listOfWavFiles)):
            f.write('plus Sound diphone' + str(i) + '\n')

        f.write('Concatenate recoverably\n')
        f.write('select Sound chain\n')
        f.write('Save as WAV file... /home/ph-02/Documentos/tps_habla/tp1/' + anOutputFile)



def transformarEnPregunta(fileName):

    originalPitchTier = fileName + '.PitchTier'
    newPitchTier = fileName + '-mod.PitchTier'
    xmin, xmax, points = parsePitchTier(originalPitchTier)
    #do something with points
    print points
    percent90 = math.floor(len(points)*0.8)
    newPoints = points[:int(percent90)]
    _ , newVal = points[int(percent90)]
    for i in range(int(percent90)+1, len(points)):
        num, value = points[i]
        newPoints.append([num,newVal])
        newVal += 10

    builPitchTier(newPitchTier, xmin, xmax, newPoints)


def main():

    prosodia = False
    a = sys.argv[1]
    if a[-1:] == '?':
        prosodia = True
        a = a[:-1]

    fileName = sys.argv[2]
    listOfDiphones = obtainDiphones(a)
    diphones = buildWavFiles(listOfDiphones, 'difonos/')
    buildPraatScrip(diphones, 'concatenate.praat', fileName)

    if prosodia:
        os.system('praat extraer-pitch-track.praat ' + fileName + ' ' + fileName[:-4] + '.PitchTier 50 300')
        transformarEnPregunta(fileName[:-4])
        os.system('praat reemplazar-pitch-track.praat ' + fileName + ' ' + fileName[:-4] + '-mod.PitchTier ' + fileName[:-4] + '-mod.wav 50 300')
        copyfile( fileName[:-4] + '-mod.wav',fileName)

if __name__ == '__main__':
    main()
