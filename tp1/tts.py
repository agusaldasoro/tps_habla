import os
import sys
import math
from shutil import copyfile
from shutil import rmtree

def main():
    phrase = sys.argv[1]
    fileName = sys.argv[2]
    createFolder(fileName)

    prosodia = False
    if phrase[-1:] == '?':
        prosodia = True
        phrase = phrase[:-1]

    listOfDiphones = obtainDiphones(phrase)
    diphones = buildWavFiles(listOfDiphones, 'diphones/')
    buildPraatScript(diphones, 'concatenate.praat', fileName)
    os.system('praat concatenate.praat')

    if prosodia:
        completePath = os.getcwd() + fileName[:-4]
        # Extract Pitch Track
        os.system('praat extract-pitch-track.praat ' + completePath + '.wav ' + completePath + '.PitchTier 50 300')
        # Create new Pitch Track
        convertIntoQuestion(completePath)
        # Replace with New Pitch Track
        os.system('praat replace-pitch-track.praat ' + completePath + '.wav ' + completePath + '-mod.PitchTier ' + completePath + '-mod.wav 50 500')
        copyfile(completePath + '-mod.wav', completePath + '.wav')
        os.remove(completePath + '-mod.wav')

    garbageCollector()


# gets diphones from an input string
def obtainDiphones(aString):
    aList = []
    aString = '-' + aString + '-'
    for i in range(0, len(aString)-1):
        aList.append(aString[i] + aString[i+1])

    return aList


# Copy and rename the necesary wav files to tempWavs
def buildWavFiles(aListOfDiphones, aWavDirectory):
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


# writes script in aPraatFile that'll concatenate the wav files,
# specified on listOfWavFiles and save it on anOutputFile
def buildPraatScript(listOfWavFiles, aPraatFile, anOutputFile):
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


# Creates the Destination Folder if necesary
def createFolder(fileName):
    separatePath = fileName.split("/")
    if len(separatePath) <= 2:
        return

    fileNameFolder = "/".join(separatePath[:-1][1:]) + "/"
    if not os.path.exists(fileNameFolder):
        os.makedirs(fileNameFolder)


# Creates a new PitchTier file to modify prosodia
def convertIntoQuestion(fileName):
    originalPitchTier = fileName + '.PitchTier'
    newPitchTier = fileName + '-mod.PitchTier'
    xmin, xmax, points = parsePitchTier(originalPitchTier)

    # Modify the last 20% of points
    percent = math.floor(len(points) * 0.8)
    newPoints = points[:int(percent)]

    _ , newVal = points[int(percent)]
    for i in range(int(percent) + 1, len(points)):
        num, value = points[i]
        newVal += 20
        newPoints.append([num,newVal])

    buildPitchTier(newPitchTier, xmin, xmax, newPoints)


# Parses the Pitch Tier to obtain the data
def parsePitchTier(aPitchTier):
    with open(aPitchTier, 'r') as f:
        f.readline()
        f.readline()
        f.readline()
        _, _, xmin = f.readline().split()
        _, _, xmax = f.readline().split()
        _, _, _, amountOfPoints = f.readline().split()
        points = []
        for i in range(0, int(amountOfPoints)):
            f.readline()
            _, _, number = f.readline().split()
            _, _, value = f.readline().split()
            points.append([float(number),float(value)])

    return xmin, xmax, points


# Builds a new Pitch Tier modifying the original
def buildPitchTier(aPitchTier, xmin, xmax, points):
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


# Deletes the temp files
def garbageCollector():
    rmtree('tempWavs/')
    os.remove('concatenate.praat')


if __name__ == '__main__':
    main()
