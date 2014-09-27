#coding=utf8

import json, sys, time
from optparse import OptionParser
from pcsv import saveCSV, readCSV
from prod import ProductParser

ps = OptionParser()
ps.add_option("-f", "--file", dest="filename")
ps.add_option("-m", "--mode", dest="mode")
ps.add_option("-u", "--url", dest="url")
ps.add_option("-o", "--output", dest="output")
ps.add_option("-i", "--input", dest="input")

(options, args) = ps.parse_args()

if options.filename is None:   # if filename is not given
    ps.error('Filename not given')
    sys.exit(0)

try:
    config_file = open (options.filename, "r")
    config = json.loads(config_file.read())
    parser = ProductParser(config)

except Exception, e:
    print 'Error', e 
    ps.error('File not exist')
    sys.exit(0)

if options.mode not in ['scan', 'find', 'update']: 
    ps.error('Mode not given')
    sys.exit(0)

start_time = time.time()

if options.mode == 'scan':
    if options.output is None:
        ps.error('Output not given')
        sys.exit(0)
    
    products, keys, urls = parser.scan()

    saveCSV(options.output+'_products.csv', products, keys)
    saveCSV(options.output+'_urls.csv', [[u] for u in urls])
    
elif options.mode == 'find':
    if options.url is None:
        ps.error('URL not given')
        sys.exit(0)
    
    info = parser.find(options.url)
    if info is None:
        print 'Not found info'
    else:
        for k,v in info.items():
            print "%s: %s" % (k, v)

elif options.mode == 'update':
    if options.input is None:
        ps.error('Input not given')
        sys.exit(0)
    if options.output is None:
        ps.error('Output not given')
        sys.exit(0)

    urls = [d['url'] for d in readCSV(options.input)]
    updates, keys = parser.update(urls)

    saveCSV(options.output+'_updates.csv', updates, keys)


print("--- %s seconds ---" % (time.time() - start_time))
