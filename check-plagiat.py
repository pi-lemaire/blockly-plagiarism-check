
import glob, os, sys
import io
from path import Path
from lxml import etree, objectify
from chardet.universaldetector import UniversalDetector



#analyzeDir = "S1-Eval2/exercice 2"
analyzeDir = sys.argv[1]
prefixSubject = "1J05"



studentNames = []
teacherNames = []
variableNames = []
errorsNames = []
errorTypes = []


# file encoding detector
detector = UniversalDetector()


# record the number of files analyzed in case there was some mistake somewhere
nbFilesAnalyzed = 0


for f in Path(analyzeDir).walkfiles():
    if not (f.ext==".txt" or f.ext==".TXT"):
        continue
    #print(f.basename())
    #print(f.abspath())

    # trying to retrieve the student name and the teacher name
    currTeacherName = ""
    currStudentName = os.path.basename(os.path.normpath(f.dirname()))
    if currStudentName[0:len(prefixSubject)]==prefixSubject:
        # the parent folder is actually the name for the deposit space, so we grab the teacher name from there
        strElems = currStudentName.split("-")
        currTeacherName = strElems[2] + " " + strElems[3]
        
        # the student name is included in the file name
        currStudentName = f.basename()
    else:
        # grabbing the teacher name from the parent folder
        parentFolder = os.path.basename(os.path.normpath(f.dirname().dirname()))
        strElems = parentFolder.split("-")
        currTeacherName = strElems[2] + " " + strElems[3]
    
    
    currStudentName = currStudentName[0:currStudentName.find('_')]
    
    displayName = currStudentName + " (" + currTeacherName + ")"
    print(displayName)
    
    fileUrl = f.abspath()
    nbFilesAnalyzed += 1
    
    #continue
    
    # apparently, we need to how the file was encoded...
    detector.reset()
    # Open the file as binary data
    with open(fileUrl, 'rb') as fb:
        for line in fb.readlines():
            detector.feed(line)
            if detector.done: break
    detector.close()
    fileEncoding = detector.result['encoding']
    
    
    if fileEncoding==None:
        print("######## ERREUR : encodage non detecte")
        errorsNames.append(displayName)
        errorTypes.append('encodage non detecte')
        continue
    #print(fileEncoding)

    # since in some case we have some mess in the files before the actual
    # xml code starts, we load the whole file into a string, starting from
    # the first line where we meet a '<xml' tag at first position
    fullFileString = ""
    #rtfFileCase = False
    firstRealLine=False
    correctEndToTheFile=False
    idLine = 0
    
    try:
        with io.open(fileUrl, encoding=fileEncoding) as ft:
            for line in ft:
                #if line.find('{\\rtf')!=-1:
                #    # the file is actually a rtf file, we need to remove the \ characters at the end of every line
                #    rtfFileCase = True
                    
                if firstRealLine==False:
                    if line.find('<xml')!=-1:
                        firstRealLine=True
                        # prevent the file from adding stuff that may have been pasted before the actual xml code on the first line
                        line = line[line.find('<xml'):len(line)]
                if firstRealLine==True:
                    #if rtfFileCase:
                    fullFileString += line[line.find('<'):line.rfind('>')+1]
                    #else:
                    #    fullFileString += line
                    
                    if line.find('</xml')!=-1:
                        correctEndToTheFile=True
                        break
                
                idLine = idLine + 1
    except:
        print("######## ERREUR : lecture du fichier texte impossible")
        errorsNames.append(displayName)
        errorTypes.append('lecture du fichier texte impossible')
        continue
    
    
    
    if (firstRealLine==False or correctEndToTheFile==False):
        print("######## ERREUR : pas de tag xml en debut ou en fin de fichier")
        errorsNames.append(displayName)
        errorTypes.append('pas de tag xml en debut ou en fin de fichier')
        continue
    #print(fullFileString)
    
    
    #### NOW LOAD THE STRING
    try:
        root = etree.fromstring(fullFileString)
    except:
        print("######## ERREUR : echec du decodage XML")
        errorsNames.append(displayName)
        errorTypes.append('echec du decodage XML')
        continue

    #### first we remove the namespace, which is really annoying
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'): continue  # (1)
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    
    objectify.deannotate(root, cleanup_namespaces=True)
    
    
    currVarNames = []
    #### now retrieve the variables ids
    for var in root.xpath("variables/variable"):
        #print(var.get("id"))
        currVarNames.append(var.get("id"))
    
    #print(currVarNames)
    
    # record what we've extracted. I used 3 separate lists, this is poor coding, whatever..
    studentNames.append(currStudentName)
    teacherNames.append(currTeacherName)
    variableNames.append(currVarNames)




print("==============")
print("NOMBRE TOTAL DE FICHIERS ANALYSES :")
print(nbFilesAnalyzed)


print("==============")
print("IMPOSSIBLE DE TRAITER LES FICHIERS SUIVANTS :")
for i in range(0,len(errorsNames)):
    print("* " + errorsNames[i] + " : " + errorTypes[i])


print("==============")
print("==============")
print("ANALYSE DU PLAGIAT A PARTIR DES NOMS DE VARIABLES")


# simply try all correspondances one by one
for i in range(0,len(studentNames)):
    for j in range(i+1,len(studentNames)):
        matchingVars = []
        for varI in variableNames[i]:
            for varJ in variableNames[j]:
                if varI==varJ:
                    matchingVars.append(varI)
        if len(matchingVars)>0:
            if not (studentNames[j] == studentNames[i]):
                printVar = "correspondance trouvee ! "
                printVar += studentNames[i] + " (" + teacherNames[i] + ") - " + studentNames[j] + " (" + teacherNames[i] + ")"
                printVar += " pour les noms de variables : "
                print("-------------")
                print(printVar)
                print(matchingVars)
                print("-------------")
