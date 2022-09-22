import os, subprocess, hashlib
from pathlib import Path

drivename = '/dev/sda1'

def getClusters(text):
    text = text.split(':')[1]
    text = text.split('-')
    if len(text) == 1:
        text[0] = int(text[0])
        return text
    clusters = []
    for x in range(int(text[1]) - int(text[0]) + 1):
        clusters.append(int(text[0]) + x)
    return clusters

def showMenu():
    print('Choose an option:')
    print('\t1)Show file data')
    print('\t2)Write message on file slack space')
    print('\t3)Clear file slack space')
    answer = int(input('Option: '))
    return answer

def showData():
    drive = open(drivename, 'rb')
    i = 0
    for x in clusters:
        print(f'CLUSTER NUMBER {i + 1} ({x}):')
        drive.seek(x * 4096)
        info = str(drive.read(4096)).split("'")[1]
        print(info)
        i = i + 1
    print(f'Number of clusters: {len(clusters)}')
    drive.seek((clusters[-1] * 4096) + (filesize % 4096))
    slackstr = str(drive.read(4096 - filesize % 4096)).split("'")[1]
    hash_object = hashlib.md5(slackstr.encode())
    md5_hash = hash_object.hexdigest()
    print(f'File slack md5 hash: {md5_hash}')
    drive.close()

def writeData(message):
    if len(message) > (4096 - (filesize % 4096)):
        print(f'Message is too long (max size: {4096 - (filesize % 4096)} characters)')
        return
    drive = open(drivename, 'wb')
    drive.seek((clusters[-1] * 4096) + (filesize % 4096))
    drive.write(bytes(message, encoding='utf-8'))
    drive.close()
    print('Message written')

def clearSlack():
    interations = 4096 - (filesize % 4096)
    drive = open(drivename, 'wb')

    for x in range(interations):
        drive.seek((clusters[-1] * 4096) + (filesize % 4096)+ x)
        drive.write(bytes(b'\x00'))
    drive.close()
    print('Slack space cleared')

def showMenu2():
    print('Choose an option:')
    print('\t1)Work with one file')
    print('\t2)System checkup')
    answer = int(input('Option: '))
    return answer

def getFilesNew(p):
    flist = p.glob('**/*')
    files = [x for x in flist if x.is_file()]
    return files

def getFilesNumber(pathlist):
    total = 0;
    for p in pathlist:
        path = Path(p).absolute()
        for x in getFilesNew(path): total = total + 1
    return total

def isCorrupted(p):
    filename = str(p)
    filestat = os.stat(filename)
    fileino = filestat.st_ino
    filesize = filestat.st_size
    result = subprocess.run(['debugfs', '-R', 'stat <' +str(fileino)+'>', '/dev/sda1'], capture_output=True, encoding='utf-8')
    data = str(result.stdout)
    datalist = data.splitlines()
    checksum = datalist[11].split()[-1]
    clusters = getClusters(datalist[13])
    print(p)
    print(clusters)
    print('')
    return 1

def getLog(pathlist):
    print('Calculating number of files..')
    n = 1
    filesNumber = getFilesNumber(pathlist)
    warnings = []
    for p in pathlist:
        path_atual = Path(p).absolute()
        for x in getFilesNew(path_atual):
            #print(str(n) + '/' + str(filesNumber) + '  ' + str(x))
            if isCorrupted(x): warnings.append(x)
            n = n + 1
    print('System analysis finished')
    print('[WARNINGS]')
    #for x in warnings:
        #print(x)


answer = showMenu2()
while answer != 9:
    if answer == 1:
        filename = input('File name: ')
        filestat = os.stat(filename)
        fileino = filestat.st_ino
        filesize = filestat.st_size
        result = subprocess.run(['debugfs', '-R', 'stat <' +str(fileino)+'>', '/dev/sda1'], capture_output=True, encoding='utf-8')
        data = str(result.stdout)
        datalist = data.splitlines()
        checksum = datalist[11].split()[-1]
        clusters = getClusters(datalist[13])
        answer2 = showMenu()
        while(answer2 != 9):
            if answer2 == 1: showData()
            if answer2 == 2: writeData(input('Message: '))
            if answer2 == 3: clearSlack()
            answer2 = showMenu()
    if answer == 2:
        pathlist = ['/home/gabriel/Desktop/scripts/z']
        getLog(pathlist)
        break

