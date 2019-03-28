
import glob, os, sys
import io
from path import Path
import zipfile



#analyzeDir = "S1-Eval2/exercice 2"
analyzeDir = sys.argv[1]


# record the number of files analyzed in case there was some mistake somewhere
nbFilesAnalyzed = 0


for f in Path(analyzeDir).walkfiles():
    if not (f.ext==".zip" or f.ext==".ZIP"):
        continue
    #print(f)
    newfolder = f.basename()[0:len(f.basename())-4]
    
    if not os.path.exists(analyzeDir + "/" + newfolder):
        os.makedirs(analyzeDir + "/" + newfolder)
        
    print(newfolder)
    
    
    #print(f.abspath())
    
    #continue

    zip_ref = zipfile.ZipFile(f, 'r')
    zip_ref.extractall(analyzeDir + "/" + newfolder)
    zip_ref.close()
    
    