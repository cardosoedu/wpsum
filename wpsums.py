import os, json, re, urllib.request
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

# function compareSums(newSums, originalSums, fromWeb)
# @newSums          :   the new hashes file
# @originalSums     :   the original hashes file, like: sums_versionName.json
# @fromWeb          :   specifies if the script is going to download the hash from my repository
#
# This function will take two hash files and compare the two, returning if there's a difference.

def compareSums(newSums, originalSums, fromWeb = False):
    # Check if we're going to take the file from the repository
    if fromWeb:
        try:
            url = "https://raw.githubusercontent.com/cardosoedu/wpsum/master/sums/sums_{}.json".format(originalSums)
        except urllib.HTTPError:
            # The error most tipically is going to be because there's not a hash file available for that version
            exit("Unsupported version.")
        finally:
            exit("Unknown error.")
        print("Downloading the hashes file from {}...".format(url))
        req = urllib.request.urlopen(url)
        loadOriginal = json.loads(req.read().decode())
    else:
        # If we are not downloading the file, then it should be provided by the user
        loadOriginal = json.load(originalSums)

    # Now we can load the @newSums file
    loadNew = json.load(newSums)
    # If both files are the "same", then there's nothing to do.
    if loadNew == loadOriginal:
        exit('Everything good!')
    else:
        print('Something is wrong...')
        # If the @newSums version is different than the @originalSums, there's nothing to do.
        if(loadNew['Wordpress']['Version'] != loadOriginal['Wordpress']['Version']):
            exit("Versions do not match.")
        else:
            # loadNew becomes a list of the dictionaries in Wordpress:Checksums of the @newSums
            loadNew = sorted([repr(x) for x in loadNew['Wordpress']['Checksums']])
            # loadOriginal becomes a list of dictionaries in Wordpress:Checksums of the @originalSums
            loadOriginal = sorted([repr(x) for x in loadOriginal['Wordpress']['Checksums']])
            # Now we check if there's any item that is in the @newSums but not in @originalSums
            filesNotThere = sorted([x for x in loadNew if x not in loadOriginal])
            # And we cut out the files that are not there in both lists
            trimOriginals = sorted([repr(x) for x in loadOriginal if x in loadNew])
            trimNew = sorted([repr(x) for x in loadNew if x in loadOriginal])

            # If there's any item that isnt in the @originalSums, print it out
            if(len(filesNotThere) > 0):
                print("**** Files not in the original Hashes file: ")
                for fl in filesNotThere:
                    print(fl)

            # Create a pair with both lists so we can quickly check them.
            # There shouldnt be any errors here and the only differences that could be shown
            # are the ones where the hash is different.
            pairs = zip(trimNew, trimOriginals)
            for x, y in pairs:
                if(x != y):
                    print("Files do not match: ")
                    print("*** Your file: %s" % x)
                    print("Original file: %s" % y)
            print("-------------")

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
    auto = input("Run on auto-mode? y/n (default: y): ")
    if auto == 'y' or auto == '':
        print("Autorun assumes that you're in the Wordpress directory.")
        dDict = {}
        RecursiveSearch('./', dDict)
        print("Searching files...")
        version = getVersion('./')
        print("Getting your Wordpress version.")
        nameFile = 'newsums_'+version+'.json'
        if dDict:
            print("Creating JSON...")
            createJson(dDict, nameFile, version)
            pFileNew = open(nameFile, 'r')
            print("Checking the integrity of your Wordpress core files.\nComparing against the original Wordpress {} core files.".format(version))
            compareSums(pFileNew, version, True)
        else:
            exit('Something went wrong.')
    elif auto == 'n':
        createFile = input("Do you want to make a new sums file? (y\\n): ")
        if(createFile == 'n'):
            compare = input("Do you want to compare two files? (y\\n): ")
            if(compare == 'n'):
                exit('There\'s not much to do, then.\n')
            elif(compare == 'y'):
                file1 = input('Input the name of the first sums file: ')
                file2 = input('Input the name of the second sums file: ')
                try:
                    fp1 = open(file1, 'r')
                except FileNotFoundError:
                    exit('File not found.')
                else:
                    try:
                        fp2 = open(file2, 'r')
                    except FileNotFoundError:
                        exit('File not found.')
                    compareSums(fp2, fp1, False)
                    fp1.close()
                    fp2.close()
            else:
                exit('Bad input.')
        elif(createFile == 'y' or createFile == ''):
            actDir = input("Input the directory name to start (default current directory): ")
            dDic = {}
            if actDir == '':
                actDir = './'
            RecursiveSearch(actDir, dDic)
            version = getVersion(actDir)
            if dDic:
                nameFile = input("Input the name of the resulting JSON file (default: sums_version.json): ")
                if(nameFile == ""):
                    nameFile = 'sums_'+version+'.json'
                createJson(dDic, nameFile, version)
        else:
            exit('Bad input.')
    else:
        exit('Bad input.')
