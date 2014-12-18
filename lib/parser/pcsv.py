import csv
import json
import StringIO

def readCSV(filename):
    f = open(filename, 'rb')
    return parseCSV(f.read())

def parseCSV(string):
    f = StringIO.StringIO(string[3:])
    data = csv.DictReader(f,delimiter=';')
    return [d for d in data]

def saveCSV(filename, data, keys=None):
    with open(filename, 'wb') as f:
        if keys is not None:
            w = csv.DictWriter(f,keys,delimiter=';')
            data = [{k:v.encode('utf8') for k,v in d.items()} for d in data]
            f.write(u'\ufeff'.encode('utf8')) # BOM
            w.writeheader()
        else:
            w = csv.writer(f,delimiter=';')
            data = [[v.encode('utf8') for v in d] for d in data]
            f.write(u'\ufeff'.encode('utf8')) # BOM
        w.writerows(data)
        f.close()