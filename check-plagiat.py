
import glob, os
import io
from path import Path
from lxml import etree, objectify
from chardet.universaldetector import UniversalDetector


analyzeDir = "test_folder"

studentNames = []
variableNames = []
errorsNames = []
errorTypes = []


# file encoding detector
detector = UniversalDetector()


nbFilesAnalyzed = 0


for f in Path(analyzeDir).walkfiles():
    if not (f.ext==".txt" or f.ext==".TXT"):
        continue
    #print(f.basename())
    #print(f.abspath())
    #
    currStudentName=os.path.basename(os.path.normpath(f.dirname()))
    currStudentName = currStudentName[0:currStudentName.find('_')]
    print(currStudentName)
    fileUrl = f.abspath()
    nbFilesAnalyzed += 1
    #
    #
    #
    # apparently, we need to how the file was encoded...
    detector.reset()
    # Open the file as binary data
    with open(fileUrl, 'rb') as fb:
        for line in fb.readlines():
            detector.feed(line)
            if detector.done: break
    detector.close()
    fileEncoding = detector.result['encoding']
    #
    #
    if fileEncoding==None:
        print("######## ERREUR : encodage non detecte")
        errorsNames.append(currStudentName)
        errorTypes.append('encodage non detecte')
        continue
    #print(fileEncoding)
    #
    # since in some case we have some mess in the files before the actual
    # xml code starts, we load the whole file into a string, starting from
    # the first line where we meet a '<' character at first position
    fullFileString = ""
    firstRealLine=False
    correctEndToTheFile=False
    try:
        with io.open(fileUrl, encoding=fileEncoding) as ft:
            for line in ft:
                if firstRealLine==False:
                    if line.find('<xml')!=-1:
                        firstRealLine=True
                if firstRealLine==True:
                    fullFileString+=line
                    if line.find('</xml')!=-1:
                        correctEndToTheFile=True
                        break
    except:
        print("######## ERREUR : lecture du fichier texte impossible")
        errorsNames.append(currStudentName)
        errorTypes.append('lecture du fichier texte impossible')
        continue
    #
    if (firstRealLine==False or correctEndToTheFile==False):
        print("######## ERREUR : pas de tag xml en debut ou en fin de fichier")
        errorsNames.append(currStudentName)
        errorTypes.append('pas de tag xml en debut ou en fin de fichier')
        continue
    #print(fullFileString)
    #
    #
    #### NOW LOAD THE STRING
    try:
        root = etree.fromstring(fullFileString)
    except:
        print("######## ERREUR : echec du decodage XML")
        errorsNames.append(currStudentName)
        errorTypes.append('echec du decodage XML')
        continue
        #
        #### first we remove the namespace, which is really annoying
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'): continue  # (1)
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    #
    objectify.deannotate(root, cleanup_namespaces=True)
    ####
    #
    currVarNames = []
    #### now display the variables ids
    for var in root.xpath("variables/variable"):
        #print(var.get("id"))
        currVarNames.append(var.get("id"))
    #
    #print(currVarNames)
    #
    studentNames.append(currStudentName)
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


for i in range(0,len(studentNames)):
    for j in range(i+1,len(studentNames)):
        matchingVars = []
        for varI in variableNames[i]:
            for varJ in variableNames[j]:
                if varI==varJ:
                    matchingVars.append(varI)
        if len(matchingVars)>0:
            printVar = "correspondance trouvee ! "
            printVar += studentNames[i] + " - " + studentNames[j]
            printVar += " pour les noms de variables : "
            print("-------------")
            print(printVar)
            print(matchingVars)
            print("-------------")
