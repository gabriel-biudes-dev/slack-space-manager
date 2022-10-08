import os, subprocess, hashlib, sys
from pathlib import Path

#[CONDITIONS]
#Works only on linux
#Must execute with sudo (sudo python3 main.py)
#Must input the correct drivename

drivename = '/dev/sdb3'

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
    drive.write(bytes(message, encoding='utf-8'))
    drive.close()
    print('Message written')

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
    print('Slack space cleared')

def showMenu2():
    """Shows the second application menu

    Returns:
        int: Choosen option
    """
    print('Choose an option:')
    print('\t1)Work with one file')
    print('\t2)System checkup')
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
        for x in corruptedfiles: clearSlack(x.lastcluster, x.size)
        print('Slack spaces cleared successfully')
        return
    print('Exiting program..')

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

if __name__ == '__main__': main()