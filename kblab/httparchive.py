from requests import get,post
from urllib.parse import urljoin
from contextlib import closing
from json import dumps,loads
import kblab

MAX_ID=2**38

class HttpArchive(kblab.Archive):
    def __init__(self, root=None, base=None, auth=None):
        url=root
        self.url = url + ('/' if url[-1] != '/' else '')
        self.auth = auth
        self.base = base or url
        self.server_base = get(urljoin(self.url, 'base')).text

        if auth:
            if isinstance(auth, dict) and auth['type'] == 'basic':
                self.auth = (auth['user'], auth['pass'])
            elif isinstance(auth, tuple) and len(auth) == 2:
                    self.auth = auth
            else:
                raise Exception('unsupported auth configuration')


    def get(self, key, mode='r'):
        try:
            return kblab.Package(
                    self.url + key + '/',
                    mode=mode,
                    base=urljoin(self.base, key + '/'),
                    auth=self.auth,
                    server_base=urljoin(self.server_base, key + '/'))
        except:
            return None


    def search(self, query, start=0, max=None):
        g = self._search_iter(query, start, max)
        i,r,c = next(i).split()

        return i,r,c,g


    def _search_iter(self, query, start=0, max=None):
        params = { 'q': dumps(query), 'start': start }
        if max: params.update({ 'max': max })

        with closing(get(urljoin(self.url, 'search'),
            params=params,
            auth=self.auth,
            stream=True)) as r:

            if r.status_code == 200:
                 for key in r.raw:
                     yield key[:-1].decode('utf-8')
            else:
                raise Exception('Expected status 200, got %d' % r.status_code)


    def count(self, query, cats={}):
        with closing(get(urljoin(self.url, 'count'),
                         params={ 'q': dumps(query), 'c': dumps(cats) },
                         auth=self.auth)) as r:
                
            if r.status_code == 200:
                return loads(r.text)
            else:
                raise Exception('Expected status 200, got %d' % r.status_code)


    def get_location(self, key, path):
        return self.url + key + '/' + path


    def __iter__(self):
        with closing(get(self.url + 'packages', auth=self.auth, stream=True)) as r:
            if r.status_code == 200:
                for key in r.raw:
                    yield key[:-1].decode('utf-8')
            elif r.status_code != 404:
                raise Exception('server returned status %d' % r.status_code)


    def get_key(self, url):
        if url.startswith(self.url):
            return url[len(self.url):].split('/')[0]

        raise Exception('url (%s) does start with %s' % (url, self.url))


    def __contains__(self, key):
        with closing(get(self.url + key + '/')) as r:
            return r.status_code == 200


