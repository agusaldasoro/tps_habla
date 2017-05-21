import sys
from shutils import copyfile

def parsePitchTier(aPitchTier):

    with open(aPitchTier, 'r') as f:
        f.readline()
        f.readline()
        f.readline()
        _, _ , xmin = f.readline().split()
        _, _ , xmax = f.readline().split()
        _,_,_, amntOfPoints = f.readline().split()
        points = []
        for i in range(0,amntOfPoints):
            f.readline()
            _,_, number = f.readline().split()
            _,_, value = f.readline().split()
            points.append(zip(number,value))

    return xmin, xmax, points

def builPitchTier(aPitchTier, xmin, xmax,points):

    with open(aPitchTier, 'w') as f:
        f.write('File type = "ooTextFile"\n')
        f.write('Object class = "PitchTier"\n')
        f.write('\n')
        f.write('xmin = ' + xmin)
        f.write('xmax = ' + xmin)
        f.write('points: size = ' + len(points))
        for i in range(0, len(points)):
            num, val = points[i]
            f.write('points [' + str(i+1) + ']:\n')
            f.write('\tnumber = ' + str(num) +'\n')
            f.write('\tvalue = ' + str(val) +'\n')



def obtainDiphones(aString):
    '''gets diphones from an input strings
    '''
    aList = []
    dummyString = '-' + aString + '-'
    for i in range(0, len(dummyString)-1):
        aList.append(dummyString[i], dummyString[i+1])
    
    return aList


def buildWavFiles(aListOfDiphones, aWavDirectory):
    '''Copy and rename the necesary wav files to tempWavs
    '''
    files = [ a + '.wav' for a in aListOfDiphones]
    i = 0
    diphones = []
    for f in files:
        copyfile(aWavDirectory + f, 'tempWavs/diphone' + str(i) + '.wav')
        i += 1
        diphones.append('tempWavs/diphone' + str(i) + '.wav')
    return diphones

def buildPraatScrip(listOfWavFiles, aPraatFile, anOutputFile):
    '''write and executes a praat script that'll concatenate the wav files specified on listOfWavFiles on outputFile
    '''
    pass


def transformarEnPregunta(fileName):

    originalPitchTier = fileName + '.PitchTier'
    newPitchTier = fileName + '-mod.newPitchTier'
    xmin, xmax, points = parsePitchTier(originalPitchTier)
    #do something with points
    
    builPitchTier(newPitchTier, xmin, xmax, points)


def main():
    
    prosodia = False
    a = sys.argv[1]
    if a[:-1] == '?':
        prosodia = True
        a = a[-1:]
    fileName = sys.argv[2]
    listOfDiphones = obtainDiphones(a)
    diphones = buildWavFiles(listOfDiphones, 'sounds')
    buildPraatScrip(diphones, 'concatenate.praat', fileName)

    if prosodia:
        os.system('praat praat_examples/extraer-pitch-track.praat ' + fileName + ' ' + fileName[:-3] + '.PitchTier 50 300')
        transformarEnPregunta(fileName)
        os.system('praat praat_examples/reemplazar-pitch-track.praat ' + fileName + ' ' + fileName[:-3] + '-mod.PitchTier ' + fileName[:-3] + '-mod.wav 50 300')
        copyfile( fileName[:-3] + '-mod.wav',fileName)

if __name__ == '__main__':
    main()
