import os
import json
import re
from hashlib import sha1
from glob import glob 

# Get wordpress version
# Search for every php and js file excluding the wp-content directory
# Save the sha1sum of these files in json format (name file, sum)
# Compare the file with the file with sums of the original wordpress version

def sumToJson(fname, endDict):
    try:
        fp = open(fname, 'rb')
    except PermissionError:
        print('Permission error in %s' % fname)
        pass
    except FileNotFoundError:
        print('File not found: %s' % fname)
        pass

    csum = sha1(fp.read()).hexdigest()
    data = {fp.name: csum}
    fp.close()
    endDict.update(data)

def getVersion(dirname):
    versionfile = dirname + '/wp-includes/version.php'
    try:
        f = open(versionfile, 'r')
        for line in f:
            if line.startswith("$wp_version"):
                ver = line.split("=")[1].strip();
                version = re.sub("[';]", '', ver)
                return version
                break
    except FileNotFoundError:
        quit('File wp-includes/version.php doesn\'t exist!')

def RecursiveSearch(dirname, dDic):
    tmpDirs = []
    if os.path.isdir(dirname):
        contents = glob(str(dirname)+'/*')
        for node in contents:
            if(os.path.isdir(node) and os.path.basename(node) != 'wp-content'):
                try:
                    RecursiveSearch(node, dDic)
                except PermissionError:
                    pass
            else:
                if '.php' in os.path.basename(node) or '.js' in os.path.basename('node'):
                    sumToJson(node, dDic)
    else:
        exit('%s is not a directory.' % dirname)

def compareSums(originalSums, newSums):
    loadNew = json.load(newSums)
    loadOriginal = json.load(originalSums)
    if loadNew == loadOriginal:
        print('Everything good.')
    else:
    	print('Something is wrong...')
    	if(loadNew['Wordpress']['Version'] == loadOriginal['Wordpress']['Version']):
    		loadNew = sorted([repr(x) for x in loadNew['Wordpress']['Checksums']])
    		loadOriginal = sorted([repr(x) for x in loadOriginal['Wordpress']['Checksums']])

    		for a, b in zip(loadNew, loadOriginal):
    			if(a!=b):
    				print("* Difference found in:\n{}\n{}\n".format(a, b))
    	else:
    		exit('The versions don\'t match.')

def createJson(baseDic, fname, version):
    if not baseDic:
        print('Nothing to dump...')
        exit()
    if os.path.exists(fname):
        print('File already exists...')
        exit()
    finalDic = {"Wordpress": {"Version": version, "Checksums": [{key:value} for key,value in baseDic.items()]}}

    fp = open(fname, 'w')
    if json.dump(finalDic, fp):
    	print('Dumped!')
    fp.close()

if __name__ == '__main__':
    print("*** WordPress CheckSum ***")
    createFile = input("Do you want to make a new sums file? (y\\n): ")
    if(createFile == 'n'):
        compare = input("Do you want to compare two files? (y\\n): ")
        if(compare == 'n'):
            exit('There\'s not much to do, then.\n')
        elif(compare == 'y'):
            file1 = input('Input the name of the first sums file: ')
            file2 = input('Input the name of the second sums file: ')
            fp1 = open(file1, 'r')
            fp2 = open(file2, 'r')
            compareSums(fp1, fp2)
            fp1.close()
            fp2.close()
        else:
            exit('Bad input.')
    elif(createFile == 'y'):
        actDir = input("Input the directory name to start: ")
        dDic = {}
        RecursiveSearch(actDir, dDic)
        version = getVersion(actDir)
        if dDic:
            nameFile = input("Input the name of the resulting JSON file: ")
            createJson(dDic, nameFile, version)
    else:
        exit('Bad input.')
