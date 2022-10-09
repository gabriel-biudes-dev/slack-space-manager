import os, subprocess, hashlib, sys, math, random, time, psutil
from pathlib import Path
from cryptography.fernet import Fernet

#[CONDITIONS]
#Works only on linux
#Must execute with sudo (sudo python3 main.py)
#Must input the correct drivename

drivename = p = psutil.disk_partitions()[0].device
fernet = Fernet('bjq5lagsjEDIvxmWM6badVWEFD4wSGVatHaSCoYZqeI=')

class File:
    """Class to represent a file
    """
    def __init__(self, name, inode, size, clusters, lastcluster, iscorrupted):
        self.name = name
        self.inode = inode
        self.size = size
        self.clusters = clusters
        self.lastcluster = lastcluster
        self.iscorrupted = iscorrupted

class Printer():
    """Class to print data dynamically in a single line
    """
    def __init__(self,data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

def showMenu():
    """Show the application first menu

    Returns:
        int: Choosen option
    """
    print('Choose an option:')
    print('\t1)Show file data')
    print('\t2)Write message on file slack space')
    print('\t3)Clear file slack space')
    answer = int(input('Option: '))
    return answer

def showData(clusters, filesize):
    """Show data about the file clusters

    Args:
        clusters (list[int]): list of pointers in form of integer
        filesize (int): File size in bytes
    """
    drive = open(drivename, 'rb')
    i = 0
    for x in clusters:
        print(f'CLUSTER NUMBER {i + 1} ({x}):')
        drive.seek(x * 4096)
        info = str(drive.read(4096))
        info = info[2:-1]
        print(info)
        i = i + 1
    print(f'Number of clusters: {len(clusters)}')
    drive.seek((clusters[-1] * 4096) + (filesize % 4096))
    slackstr = str(drive.read(4096 - filesize % 4096))
    slackstr = slackstr[2:-1]
    hash_object = hashlib.md5(slackstr.encode())
    md5_hash = hash_object.hexdigest()
    print(f'File slack md5 hash: {md5_hash}')
    drive.close()

def writeData(message, cluster, filesize):
    """Write data inside the file slack space

    Args:
        message (str): Message to be written
        cluster (int): Reference to the last cluster
        filesize (int): File size in bytes
    """
    if len(message) > (4096 - (filesize % 4096)):
        print(f'Message is too long (max size: {4096 - (filesize % 4096)} characters)')
        return
    drive = open(drivename, 'wb')
    drive.seek((cluster * 4096) + (filesize % 4096))
    #drive.seek((cluster * 4096) + (filesize % 4096))
    if isinstance(message, str): drive.write(bytes(message, encoding='utf-8'))
    else: drive.write(bytes(message))
    drive.close()
    #print('Message written')

def clearSlack(cluster, filesize):
    """Clear a file slack space

    Args:
        cluster (int): Reference to the last cluster
        filesize (int): File size in bytes
    """
    interations = 4096 - (filesize % 4096)
    drive = open(drivename, 'wb')
    for x in range(interations):
        drive.seek((cluster * 4096) + (filesize % 4096)+ x)
        drive.write(bytes(b'\x00'))
    drive.close()

def showMenu2():
    """Shows the second application menu

    Returns:
        int: Choosen option
    """
    print('Choose an option:')
    print('\t1)Work with one file')
    print('\t2)System checkup')
    print('\t3)Store file in slack space')
    print('\t4)Recover stored file')
    answer = int(input('Option: '))
    return answer

def getFiles(p):
    """Gets all files inside a folder recursively

    Args:
        p (obj): Folder path object

    Returns:
        list[str]: List of all files absolute path
    """
    flist = p.glob('**/*')
    files = []
    for x in flist:
        try: 
            if x.is_file(): files.append(x)
        except Exception: pass
    return files

def getFilesNumber(path):
    """Gets the number of files inside a folder recursively

    Args:
        path (obj): Folder path object

    Returns:
        int: Number of files
    """
    print('Calculating number of files..')
    return len(getFiles(path))

def getClusters(text):
    """Gets all clusters from a file within a defined range

    Args:
        text (str): Clusters range

    Returns:
        list[int]: List of references to clusters in form of integers
    """
    text = text.split(':')[1]
    text = text.split('-')
    if len(text) == 1:
        text[0] = int(text[0])
        return text
    clusters = []
    value = int(text[1]) - int(text[0]) + 1
    for x in range(value): clusters.append(int(text[0]) + x)
    return clusters

def getAllClusters(text):
    """Gets all clusters from a file

    Args:
        text (str): Total cluster list range

    Returns:
        list[int]: List of references to clusters in form of integers
    """
    clusters = []
    text = text.split(',')
    for index,x in enumerate(text):
        text[index] = text[index].replace(' ', '')
        result = getClusters(text[index])
        for y in result: clusters.append(y)
    return clusters

def getData(filename):
    """Gets data about a file

    Args:
        filename (str): Path to the file

    Returns:
        obj: File object containing file data
    """
    filestats = os.stat(filename)
    fileino = filestats.st_ino
    filesize = filestats.st_size
    result = subprocess.run(['debugfs', '-R', 'stat <' +str(fileino)+'>', drivename], capture_output=True, encoding='utf-8')
    data = str(result.stdout)
    datalist = data.splitlines()
    clusters = getAllClusters(datalist[13])
    lastcluster = clusters[-1]
    drive = open(drivename, 'rb')
    drive.seek((clusters[-1] * 4096) + (filesize % 4096))
    slackstr = str(drive.read(4096 - filesize % 4096))
    slackstr = slackstr[2:-1]
    drive.close()
    iscorrupted = False
    for x in slackstr:
        if x != '\\' and x != 'x' and x != '0': iscorrupted = True
    return File(filename, fileino, filesize, clusters, lastcluster, iscorrupted)

def searchsystem():
    """Looks for used slack spaces in the entire system
    """
    p = Path('/').absolute()
    #Configure starting path
    p = p
    corruptedfiles = []
    total = getFilesNumber(p)
    for index, x in enumerate(getFiles(p)):
        output = 'Checking file ' + str(index + 1) + '/' + str(total)
        Printer(output)
        try: file = getData(x)
        except Exception: continue
        if file.iscorrupted: corruptedfiles.append(file)
    ammount = len(corruptedfiles)
    print(f'\nFiles with slack space modified: {ammount}')
    for x in corruptedfiles: print(x.name)
    if ammount == 0:
        print('Congratulations! You have no slack spaces corrupted')
        return
    answer = input('Do you want to clear file slacks now? (press y)')
    if answer == 'y' or answer == 'Y':
        print('Clearing slacks..')
        lenstr = str(len(corruptedfiles))
        for index,x in enumerate(corruptedfiles):
            output = 'Clearing file ' + str(index + 1) + '/' + lenstr
            Printer(output)
            clearSlack(x.lastcluster, x.size)
        print('\nSlack spaces cleared successfully')
        return
    print('Exiting program..')

def getfiles(path):
    """Get file names from a path

    Args:
        path (obj): Path object

    Returns:
        list[str]: File names
    """
    p = path.glob('**/*')
    return [str(x).split('/')[-1] for x in p if x.is_file()]

def createfile(path):
    hashlist = []
    rand1 = str(random.randint(0, 9999))
    rand2 = str(random.randint(0, 9999))
    rand3 = str(random.randint(0, 9999))
    rand4 = str(random.randint(0, 9999))
    list = [rand1, rand2, rand3, rand4]
    for x in list: hashlist.append(hashlib.md5(x.encode()).hexdigest())
    hashlist[0] = hashlist[0] + hashlist[1]
    hashlist[2] = hashlist[2] + hashlist[3]
    hashlist[0] = hashlib.md5(hashlist[0].encode()).hexdigest()
    hashlist[2] = hashlib.md5(hashlist[2].encode()).hexdigest()
    final = '.' + hashlist[0] + hashlist[2]
    ###
    #files = getfiles(path)
    #if final in files: return createfile(path)
    return final

def createSpaces(filename, folder):
    """Create blank files to store data

    Args:
        filename (str): File name
        folder (str): Blank files folder location

    Returns:
        list[str]: List of created file names
    """
    filescreated = []
    filestats = os.stat(filename)
    try: encrypt(filename)
    except Exception: pass
    f = open(filename, 'rb')
    filesize = len(f.read())
    f.close()
    clustersneeded = filesize / 4095
    clustersneeded = math.ceil(clustersneeded)
    path = Path().absolute() / folder
    for x in range(clustersneeded):
        output = 'Creating file ' + str(x + 1) + '/' + str(clustersneeded)
        Printer(output)
        created = createfile(path)
        filescreated.append(created)
        fullpath = path / created
        f = open(fullpath, 'w')
        f.write('a')
        f.close()
    print()
    return filescreated

def fileinsert(filename, hiddenfiles, folder):
    """Save a file data in the hiddenfiles slackspace

    Args:
        filename (str): File name
        hiddenfiles (list[str]): List of hidden file names
        folder (str): Folder where the hiddenfiles are stored
    """
    with open(filename, 'rb') as file: content = file.read()
    x = 4095
    filesiz = str(len(content))
    res = [content[y-x:y] for y in range(x, len(content) + x, x)]
    sizeint = len(hiddenfiles)
    size = str(sizeint)
    index = 0
    print('Loading..')
    time.sleep(5)
    while(index < sizeint):
        output = 'Writting file ' + str(index + 1) + '/' + size
        Printer(output)
        complete = folder + '/' + hiddenfiles[index]
        try:
            f = getData(complete)
            writeData(res[index], f.lastcluster, f.size)
        except Exception: 
            index = index - 1
            time.sleep(1)
        index = index + 1
    print()
    try: decrypt('data.txt')
    except Exception: pass
    f = open('data.txt', 'a')
    f.write('[START]\n')
    f.write(filename + '\n')
    f.write(filesiz + '\n')
    for x in hiddenfiles:
        f.write(x + ' ')
        print(f'File created: {x}')
    f.write('\n')
    f.close()
    try: encrypt('data.txt')
    except Exception: pass

def showstoredfiles():
    """Show the stored files

    Returns:
        list[str]: List of the names of the stored files
    """
    flist = []
    sz = os.stat('data.txt').st_size
    if sz == 0: return []
    try: decrypt('data.txt')
    except Exception: pass
    f = open('data.txt', 'r')
    lines = f.readlines()
    f.close()
    try: encrypt('data.txt')
    except Exception: pass
    for index,line in enumerate(lines):
        if line == '[START]\n': flist.append(lines[index + 1])
    return flist

def savedata(name, filesize, sourcefiles):
    """Saves the pointers to clusters in the text file

    Args:
        name (str): File name
        filesize (str): File size
        sourcefiles (list[int]): List of cluster numbers
    """
    name = name[0:-1]
    filesize = int(filesize[0:-1])
    clusters = []
    current = filesize
    index = 0
    sourcelen = len(sourcefiles)
    slstr = str(sourcelen)
    time.sleep(5)
    while(index < sourcelen):
        output = 'Recovering file ' + str(index + 1) + '/' + slstr
        Printer(output)
        dir = 'spaces/' + sourcefiles[index]
        try:
            f = getData(dir)
            clusters.append(f.lastcluster)
        except Exception: 
            index = index - 1
            time.sleep(1)
        index = index + 1

    for x in clusters:
        drive = open(drivename, 'rb')
        drive.seek((x * 4096) + 1)
        if current >= 4095:
            current = current - 4095
            slack = drive.read(4095)
        else: slack = drive.read(filesize % 4095)
        drive.close()
        try: decrypt(slack)
        except Exception: pass
        f2 = open(name, 'ab')
        f2.write(slack)
        f2.close()
    try: decrypt(name)
    except Exception: pass

def recover(option):
    """Recover the selected file

    Args:
        option (int): Choosen option
    """
    count = 0
    option = option - 1
    try: decrypt('data.txt')
    except Exception: pass
    f = open('data.txt', 'r')
    lines = f.readlines()
    for index,x in enumerate(lines):
        if lines[index] == '[START]\n':
            if count == option:
                name = lines[index + 1]
                filesize = lines[index + 2]
                sourcefiles = lines[index + 3]
            count = count + 1
    f.close()
    try: encrypt('data.txt')
    except Exception: pass
    sourcefiles = sourcefiles.split(' ')
    sourcefiles.pop(-1)
    savedata(name, filesize, sourcefiles)

def encrypt(filee):
    """Encrypt a file

    Args:
        filee (str): File path
    """
    with open(filee, 'rb') as file: original = file.read()
    encrypted = fernet.encrypt(original)
    with open(filee, 'wb') as encrypted_file: encrypted_file.write(encrypted)

def decrypt(filee):
    """Decrypt a file

    Args:
        filee (str): File path
    """
    with open(filee, 'rb') as file: content = file.read()
    decrypted = fernet.decrypt(content)
    with open(filee, 'wb') as file: file.write(decrypted)

def main():
    """Main function
    """
    answer = showMenu2()
    while answer != 9:
        if answer == 1:
            filename = input('File name: ')
            file = getData(filename)
            answer2 = showMenu()
            while(answer2 != 9):
                if answer2 == 1: showData(file.clusters, file.size)
                if answer2 == 2: writeData(input('Message: '), file.lastcluster, file.size)
                if answer2 == 3: clearSlack(file.lastcluster, file.size)
                answer2 = showMenu()
        if answer == 2:
            searchsystem()
            break
        if answer == 3:
            folder = 'spaces'
            try: os.mkdir(folder)
            except Exception: pass
            filename = input('File name: ')
            hiddenfiles = createSpaces(filename, folder)
            fileinsert(filename, hiddenfiles, folder)
            os.remove(filename)
            print('File saved successfully')
            break
        if answer == 4:
            flist = showstoredfiles()
            if len(flist) == 0:
                print('No files saved')
                break
            print('List of files saved:')
            for index,x in enumerate(flist): print('\t' + str(index + 1) + ')' + x, end = '')
            option = int(input('Option: '))
            print('Loading..')
            recover(option)
            print('\nFile recovered successfully')
            break

if __name__ == '__main__': main()
