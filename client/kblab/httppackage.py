from contextlib import closing
from json import loads,dumps
from requests import head,get,post,delete,put
from os.path import join,basename,abspath,isdir
from kblab.utils import valid_path,valid_key,chunked
from kblab.exceptions import RangeNotSupported
from hashlib import sha256
from copy import deepcopy
from urllib.parse import urljoin
from re import compile
from os import listdir
import kblab.package
from urllib.parse import urljoin
from tempfile import TemporaryFile

VERSION = 0.1

class HttpPackage(kblab.Package):
    def __init__(self, url, mode='r', base=None, auth=None, server_base=None):
        self.url = url
        self._mode = mode
        self.auth = auth
        self.base = base or url
        self.server_base = server_base or url

        if mode in [ 'r', 'a' ]:
            r = get(self.url, headers={ 'Accept': 'application/json' }, auth=self.auth)

            if r.status_code != 200:
                raise Exception('%d %s' % (r.status_code, r.text))

            self._desc = loads(r.text)
            self._desc['files'] = { x['path']:x for x in self._desc['files'] }
        elif mode in [ 'w', 'a' ]:
            raise Exception('mode \'w\' or \'a\' not supported for HttpPackage()')
        else:
            raise Exception('unsupported mode (\'%s\')' % mode)


    def get_raw(self, path, range=None):
        headers = {}

        if path not in self:
            raise Exception('%s does not exist in package' % path)

        if range and not (range[0] == 0 and not range[1]):
            headers['Range'] = 'bytes=%d-%s' % (range[0], str(int(range[1])) if range[1] else '')

        # @TODO potential resource leak
        r = get(self.url + path, stream=True, auth=self.auth, headers=headers)
        r.raw.decode_stream = True

        if range and 'Accept-Ranges' not in r.headers or ('Accept-Ranges' in r.headers and r.headers['Accept-Ranges'] != 'bytes'):
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
        return get(self.url + path, auth=self.auth).text


    def list(self):
        return list(self._desc['files'].keys())


    def finalize(self):
        if self._mode == 'r':
            raise Exception('package is in read-only mode')


    def description(self):
        ret = deepcopy(self._desc)
        server_base = self.server_base

        if self.base != server_base:
            ret['@id'] = ret['@id'].replace(server_base, self.base)

            for path in ret['files']:
                f = ret['files'][path]
                f['@id'] = f['@id'].replace(server_base, self.base)

        return ret


    def close(self):
        self._mode = 'r'


    def status(self):
        return self._desc['status']


    def _reload(self):
        self._desc = loads(get(self.url, auth=self.auth).text)


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

