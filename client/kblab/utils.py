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
from copy import deepcopy
from collections import Counter
from sys import stderr
from json import load
from copy import copy
from subprocess import Popen

from io import StringIO

TEMP_PREFIX='/tmp/starch-temp-'

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
    if isinstance(a, (str, int, float)):
        if isinstance(b, (str, int, float)):
            return a == b
        elif isinstance(b, (list, iter)):
            return any([ dict_search(a, x) for x in b ])
    elif isinstance(a, dict) and isinstance(b, dict):
        if set(a).issubset(b):
            return all([ dict_search(a[key], b[key]) for key in a ])

    return False


def wildcard_match(a, b):
    return a == b or a == '*'


def dict_values(d, path):
    p,di = [], deepcopy(path)

    while isinstance(di, dict):
        p += [ next(iter(di.keys())) ]
        di = next(iter(di.values()))

    p += [ di ]

    return _dict_values(d, p)


def _dict_values(d, path):
    if path == []:
        if isinstance(d, list):
            return Counter([ x for x in d if not isinstance(x, (list, dict, tuple)) ])
        elif not isinstance(d, (list, dict, tuple)):
            return Counter([d])
    else:
        if isinstance(d, (list, tuple)):
            s=Counter()
            for x in d:
                s.update(_dict_values(x, path))
            return s
        elif isinstance(d, dict) and path[0] in d:
            return _dict_values(d[path[0]], path[1:])
    
    return Counter()


def chunked(f, chunk_size=100*1024, max=None):
    pos,b = 0,None
    while b != b'' and b != '':
        b = f.read(chunk_size if not max else min(chunk_size, max - pos))
        #print('chunk %d' % len(b), file=stderr, flush=True)
        pos += len(b)

        if b != b'' and b != '':
            yield b


def stream_to_iter(raw, chunk_size=10*1024, max=None):
    with raw as f:
        yield from chunked(f, chunk_size=chunk_size, max=max)


def decode_range(srange):
    s = match('bytes=(\\d+)-(\\d*)', srange).groups()

    return ( int(s[0]), int(s[1]) if s[1] != '' else None )


@contextmanager
def nullctxmgr():
    yield


def nullcallback(msg, **kwargs):
    #print(msg, kwargs)

    if msg == 'lock':
        return nullctxmgr()


def rebase(desc, base, index_base, in_place=False):
    if base or index_base:
        ret = deepcopy(desc) if in_place else desc
        ret['@id'] = rebase_uri(['@id'], base, index_base)

        for f in ret['files']:
            f['@id'] = rebase_uri(f['@id'])

        return ret
    else:
        return desc


def rebase_uri(u, base, index_base):
    return (base or '') + (u[len(index_base):] if index_base else u)

def max_iter(i, max):
    n=0
    for chunk in i:
        if len(chunk) + n < max:
            yield chunk
            n += len(chunk)
        else:
            yield chunk[:max-n]

            return


def guess_content(path):
    if path.endswith('.jpg'):
        return 'image/jpeg'
    elif path.endswith('.jp2'):
        return 'image/jp2'
    elif path.endswith('.json'):
        return 'application/json'
    elif path.endswith('.pdf'):
        return 'application/pdf'
    elif path.endswith('.xml'):
        return 'text/xml'
    elif path.endswith('.metadata'):
        return 'text/xml'
    
    return 'application/octet-stream'


def flatten_structure(structure, levels=[ 'Part', 'Page' ]):
    for s in structure:
        if s['@type'] in levels:
            yield s

        if 'has_part' in s:
            yield from flatten_structure(s['has_part'])


def aggregate(structure, content, environment, meta):
    ret = copy(environment)
    ret_content = []

    if meta:
        ret['meta'] = meta

    stack = [ structure ]
    while len(stack) > 0:
        element = stack.pop(0)

        for x in element if isinstance(element, list) else [ element ]:
            i = x.get('@id', '')

            if i in content and content[i].get('content', '') != '':
                ret_content += [ content[i]['content'] if environment.get('@type', '') == 'Text' else content[i] ]

            if 'has_part' in x:
                stack.insert(0, x['has_part'])

    ret['content'] = ret_content

    return ret


def _flerge(structure, content, meta, level='Text', ignore = []):
    ret = []
    ignore += [ 'has_part', 'content' ]

    #stack = [ (deepcopy(meta), element) for element in structure ]
    stack = [ ({ 'path': []}, element) for element in structure ]
    while len(stack) != 0:
        environment,element = stack.pop(0)
        nenviron = { key:copy(environment[key]) for key in sorted(environment) }
        nenviron.update({ key:value for key,value in element.items() if key not in ignore })        

        if element.get('@type', None) == level:
            ret += [ aggregate(element, content, nenviron, meta) ]
        elif 'has_part' in element:
            nenviron['path'] += [ { '@id': element['@id'], '@type': element['@type'] } ]
            for x in element['has_part'][::-1]:
                stack.insert(0, (nenviron, x))

    return ret


def flerge(package, level='Text', ignore=[]):
    structure = load(package.get_raw('structure.json'))
    content = { x['@id']:x for x in load(package.get_raw('content.json')) }
    meta = load(package.get_raw('meta.json')) if 'meta.json' in package else {}
    desc = package.description()

    if level == 'Package':
        s = [ desc ]
        s[0]['meta'] = meta
        s[0]['has_part'] = structure
        
        structure = s
        #structure = [ { '@id': desc['@id'], '@type': desc['@type'], 'label': desc['label'], 'tags': desc['tags'], 'meta': meta, 'files': desc['files'], 'size': desc['size'], 'has_part': structure } ]
    else:
        structure = [ { '@id': desc['@id'], '@type': desc['@type'], 'label': desc['label'], 'tags': desc['tags'], 'meta': meta, 'has_part': structure } ]

    return _flerge(structure, content, meta, level, ignore)

