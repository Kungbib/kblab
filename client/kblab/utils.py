#!/usr/bin/env python

from uuid import uuid4
from hashlib import md5
from re import split
from contextlib import contextmanager
from os import makedirs
from os.path import dirname,exists,abspath
from hashlib import sha1
from io import BytesIO
from urllib.request import urlopen
from random import random
from datetime import datetime
from re import match
from json import load,dumps
from copy import copy,deepcopy

TEMP_PREFIX='/tmp/kblab-temp-'

def __init__():
    pass


def get_temp_dirname():
    return TEMP_PREFIX + '%s/' % uuid4()


def convert(n, radix=32, pad_to=0, alphabet='0123456789bcdfghjklmnpqrstvxzBCDFGHJKLMNPQRSTVXZ'):
    ret = ''

    if radix > len(alphabet) or radix == 0:
        raise Exception('radix == 0 or radix > len(alphabet)')

    while n:
        n, rest = divmod(n, radix)
        ret = alphabet[rest] + ret

    while len(ret) < pad_to:
        ret = alphabet[0] + ret

    return ret or alphabet[0]


def valid_path(path):
    if path[0] in [ '/' ] or '../' in path:
        raise Exception('invalid path (%s)' % path)

    return path


def valid_file(path):
    if path[0] == '/' or '..' in path:
        raise Exception('invalid path (%s)' % path)

    return path


def valid_key(key):
    if '/' in key or '.' in key:
        raise Exception('invalid key (%s)' % key)

    return key


def timestamp():
    return datetime.utcnow().isoformat() + 'Z'


def dict_search(a, b):
    if not (isinstance(a, dict) or isinstance(b, dict)):
        return wildcard_match(a, b)
    
    for key in a:
        if key == '*':
            return any([ dict_search(a[key], x) for x in b.values() ])
        if key not in b:
            if a[key] != None:
                return False
        elif not dict_search(a[key], b[key]):
            return False

    return True


def wildcard_match(a, b):
    return a == b or a == '*'


def dict_values(d, path):
    return _dict_values(d, path.split('.'))


def _dict_values(d, path):
    if path == []:
        if isinstance(d, list):
            return set([ x for x in d if not isinstance(x, (list, dict, tuple)) ])
        elif not isinstance(d, (list, dict, tuple)):
            return set([d])
    else:
        if isinstance(d, (list, tuple)):
            s=set()
            for x in d:
                s.update(_dict_values(x, path))
            return s
        elif isinstance(d, dict) and path[0] in d:
            return _dict_values(d[path[0]], path[1:])
    
    return set()


def chunked(f, chunk_size=10*1024, max=None):
    pos,b = 0,None
    while b != b'' and b != '':
        b = f.read(chunk_size if not max else min(chunk_size, max - pos))
        #print('chunk %d' % len(b))
        pos += len(b)

        if b != b'' and b != '':
            yield b


def decode_range(srange):
    s = match('bytes=(\\d+)-(\\d*)', srange).groups()

    return ( int(s[0]), int(s[1]) if s[1] != '' else None )


def aggregate(structure, content, environment):
    ret = copy(environment)
    ret_content = []

    stack = [ structure ]
    while len(stack) > 0:
        element = stack.pop(0)

        for x in element if isinstance(element, list) else [ element ]:
            i = x.get('@id', '')

            if i in content and content[i].get('content', '') != '':
                ret_content += [ content[i].get('content', '') ]

                # fulhack
                if 'font' in content[i]:
                    if 'font' not in ret:
                        ret['font'] = []

                    for f in content[i]['font']:
                        if f not in ret['font']:
                            ret['font'] += [ f ]

            if 'has_part' in x:
                stack.insert(0, x['has_part'])

    ret['content'] = ret_content

    return ret


def _flerge(structure, content, meta, level='Text', ignore = []):
    ret = []
    ignore += [ 'has_part', 'content' ]

    stack = [ (deepcopy(meta), element) for element in structure ]
    while len(stack) != 0:
        environment,element = stack.pop(0)
        nenviron = copy(environment)
        nenviron.update({ key:value for key,value in element.items() if key not in ignore })        

        if element.get('@type', None) == level:
            ret += [ aggregate(element, content, nenviron) ]
        elif 'has_part' in element:
            for x in element['has_part'][::-1]:
                stack.insert(0, (nenviron, x))

    return ret


def flerge(structure=None, content=None, meta=None, package=None, level='Text', ignore=[]):
    if structure != None and content != None and meta != None:
        pass
    elif package != None:
        structure = load(package.get_raw('structure.json'))
        content = { x['@id']:x for x in load(package.get_raw('content.json')) }
        meta = load(package.get_raw('meta.json'))
    else:
        raise Exception('Pass either structure, content and meta or package')

    return _flerge(structure, content, meta, level, ignore)


#if __name__ == '__main__':
#    if len(argv) < 4 or len(argv) > 6:
#        print(f'usage: {argv[0]} <structure-file> <content-file> <meta-file> [level] [ignore]')
#        exit(1)
#
#    level = argv[4] if len(argv) > 4 else 'Text'
#    ignore = argv[5].split(',') if len(argv) > 5 else []
#
#    with open(argv[1], mode='rb') as sfile, open(argv[2], mode='rb') as cfile, open(argv[3], mode='rb') as mfile:
#        structure = load(sfile)
#        content = { x['@id']:x for x in load(cfile) }
#        meta = load(mfile)
#
#        print(dumps(flerge(structure, content, meta, level, ignore), indent=2))

