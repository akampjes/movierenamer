#!/usr/bin/python

import re
import sys
import urllib2
import json
import getopt
import os

SOURCES = 'brrip|r5|dvdrip|src|dvdscr|pvvrip|cam|telesync|ts|wp|workprint'
CODECS = 'xvid|x264|264|h264|divx'
RESOLUTION = '720|1080|PAL|NTSC'

debug=0
dryrun=0
imdb=0
finalsep='.'
formatting=['title','disk','year','source','codec']

def get_data(filename):
    d = dict()

    d['filename'] = filename
    d['extension'] = filename.split('.')[-1]

    #get rid of the extension
    l = filename.split('.')[:-1]
    #turn list back into a string with spaces instead of dots
    filename = ''
    for x in l:
        filename += x+' '
    filename = filename.strip()
    #may as well fix '_'s while we're at it
    filename = re.sub('_', ' ', filename)

    #discover source of rip
    result = re.search(SOURCES, filename, flags=re.IGNORECASE)
    if result:
        d['source'] = result.group()

    #discover codec
    result = re.search(CODECS, filename, flags=re.IGNORECASE)
    if result:
        d['codec'] = result.group()

    #discover year
    result = re.search('\d{4}', filename)
    if result:
        d['year'] = result.group()

    #part of a series of disks?
    result = re.search('cd(\d*)', filename, flags=re.IGNORECASE)
    if result:
        disk = result.group()
        disknum = re.search('(\d+)', disk, flags=re.IGNORECASE)
        d['disk'] = int(disknum.group())
    #720p or 1080?
    result = re.search(RESOLUTION, filename, flags=re.IGNORECASE)
    if result:
        d['res'] = result.group()

    #now we need to dump everything that isn't going to be the title
    result = re.search('\[|\(|\{|\d{4}|cd(\d*)|disk(\d*)|'+SOURCES+'|'+CODECS+'|'+RESOLUTION, filename, flags=re.IGNORECASE)
    if result:
        d['title'] = filename[:result.start()].strip(' -')
    else:
        d['title'] = filename.strip(' -')
    return d

def get_imdb_info(title, year=''):
    s='http://imdbapi.com/?t='+title+'&y='+str(year)
    url = urllib2.urlopen(s.replace(' ','.'))
    res = json.loads(url.read())
    if res['Response'] == 'True':
        return res
    else:
        return None


def usage(argv0):
    print('usage: '+argv0+' [OPTION] FILE...')
    print('''
    --format=       order of attributes, comma seperated
                    default, format=title,disk,year,source,codec
                    available attributes are title,source,codec,year,res
                    attributes not discovered will be skipped
    --dry           don't rename files, just show what would happen
    --debug         turn on debuging mode
    -h
    --help          show help
    --imdb          also output imdb info if available
    --spaces        use spaces instead of dots for the final name
    --underscores   use underscores instead of dots for the final name
    ''')
    sys.exit(1)

if __name__ == "__main__":
    try:
        args, files = getopt.gnu_getopt(sys.argv[1:], 'h',[
            'dry','debug','help','imdb', 'format=', 'spaces', 'underscores'])
    except:
        print(e)
        usage(sys.arg[0])

    for opt, arg in args:
        if opt in ['--help', '-h']:
            usage(sys.argv[0])
        elif opt in ['--dry']:
            dryrun=1
        elif opt in ['--debug']:
            debug=1
        elif opt in ['--imdb']:
            imdb=1
        elif opt in ['--format']:
            formatting = arg.split(',')
        elif opt in ['--spaces']:
            finalsep=' '
        elif opt in ['--underscores']:
            finalsep='_'
        else:
            print('unknown option '+opt)
            usage(sys.argv[0])
    
    for f in files:
        filename = f.split('/')[-1]
        d=get_data(filename)
        if not 'year' in d:
            d['year'] = ''
        if imdb:
            imdbinfo = get_imdb_info(d['title'],d['year'])
            if imdbinfo:
                for x in imdbinfo.keys():
                    print x+': '+imdbinfo[x]
                if 'Year' in imdbinfo:
                    d['year'] = imdbinfo['Year']
            else:
                print('imdb: nothing found')

        newfilename = ''
        for x in formatting:
            if x in d:
                newfilename += d[x]+'.'
        newfilename = newfilename.strip(' .')
        newfilename += '.'+d['extension']
        newfilename = newfilename.replace(' ','.')
        print('new filename: '+newfilename)
        if not dryrun:  #uhh this is bad, too late to find a better solution
            if len(f.rsplit('/',1)) == 1:
                os.rename(f, newfilename)
            else:
                os.rename(f, f.rsplit('/',1)[0]+'/'+newfilename)

