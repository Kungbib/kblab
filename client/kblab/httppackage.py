from contextlib import closing
from json import loads,dumps
from requests import head,get,post,delete,put
from os.path import join,basename,abspath,isdir
from kblab.utils import valid_path,valid_key,chunked
from kblab.exceptions import RangeNotSupported
from hashlib import sha256
from copy import deepcopy
from urllib.parse import urljoin,unquote
from re import compile
from os import listdir
import kblab.package
from urllib.parse import urljoin
from tempfile import TemporaryFile
from io import BytesIO
from htfile import open as htopen

VERSION = 0.1

class HttpPackage(kblab.Package):
    def __init__(self, url, mode='r', base=None, auth=None, server_base=None, label=None):
        self.url = url
        self._mode = mode
        self.auth = auth
        self.base = base or url
        self.server_base = server_base or url

        if mode in [ 'r', 'a' ]:
            with closing(get(self.url, headers={ 'Accept': 'application/json' }, auth=self.auth, verify=kblab.VERIFY_CA)) as r:
                #print(self.url)

                if r.status_code == 404:
                    raise kblab.HttpNotFoundException(r.text)
                elif r.status_code != 200:
                    raise Exception('%d %s' % (r.status_code, r.text))

                self._desc = loads(r.text)

                if mode is 'a' and self._desc['status'] == 'finalized':
                    raise Exception('package is finalized, use patch(...)')

                self._desc['files'] = { x['path']:x for x in self._desc['files'] }
        elif mode == 'w':
            raise Exception('mode \'w\' not supported for HttpPackage(), use mode \'a\' or HttpArchive.new(...)')
        else:
            raise Exception('unsupported mode (\'%s\')' % mode)


    def get_location(self, path):
        return self.url + path


    def get_raw(self, path, range=None):
        headers = {}

        if path not in self:
            raise Exception('%s does not exist in package' % path)

        if range and not (range[0] == 0 and not range[1]):
            headers['Range'] = 'bytes=%d-%s' % (range[0], str(int(range[1])) if range[1] else '')

        # @TODO potential resource leak
        r = get(self.get_location(path), stream=True, auth=self.auth, headers=headers, verify=kblab.VERIFY_CA)
        r.raw.decode_stream = True

        if range and 'bytes' not in r.headers.get('Accept-Ranges', ''):
            raise RangeNotSupported()

        if r.status_code not in [ 200, 206 ]:
            raise Exception('Unexpected status %d' % r.status_code)

        return r.raw


    def get_iter(self, path, chunk_size=10*1024, range=None):
        if path in self:
            return self._get_iter(
                        self.get_raw(path, range=range),
                        chunk_size=chunk_size,
                        max=range[1]-range[0] if range and range[1] else None)
        else:
            raise Exception('%s does not exist in package' % path)


    def _get_iter(self, raw, chunk_size=10*1024, max=None):
        with raw as f:
            yield from chunked(f, chunk_size=chunk_size, max=max)


    def read(self, path):
        return get(self.url + path, auth=self.auth, verify=kblab.VERIFY_CA).text


    def list(self):
        return list(self._desc['files'].keys())


    def description(self):
        ret = deepcopy(self._desc)
        server_base = self.server_base

        if self.base != server_base:
            ret['@id'] = ret['@id'].replace(server_base, self.base)

            for path in ret['files']:
                f = ret['files'][path]
                f['@id'] = f['@id'].replace(server_base, self.base)

        # de-dict
        ret['files'] = [ x for x in ret['files'].values() ]

        return ret


    def close(self):
        self._mode = 'r'


    def status(self):
        return self._desc['status']


    @property
    def label(self):
        return self._desc['label']


    def _reload(self):
        self._desc = loads(get(self.url, auth=self.auth, verify=kblab.VERIFY_CA).text)
        self._desc['files'] = { x['path']:x for x in self._desc['files'] }


    def __iter__(self):
        return iter(self.list())


    def __contains__(self, key):
        return key in self._desc['files']


    def __getitem__(self, key):
        return self._desc['files'][key]


    def __setitem__(self, key, value):
        self._desc['files'][key] = value


    def __str__(self):
        return dumps(self.description(), indent=4)


#    def __len__(self):
#        return len(self._desc['files'])


def do_hash(fname):
    h = sha256()
    with open(fname, mode='rb') as f:
        b=None
        while b != b'':
            b = f.read(100*1024)
            h.update(b)

    return 'SHA256:' + h.digest().hex()

