import sys
from shutils import copyfile
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
    #do something



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
        os.system('praat reemplazar-pitch-track.praat ' + fileName + ' ' + fileName[:-3] + '-mod.PitchTier ' + fileName[:-3] + '-mod.wav 50 300')
        copyfile( fileName[:-3] + '-mod.wav',fileName)

if __name__ == '__main__':
    main()
