from requests import get,post,delete as htdelete
from urllib.parse import urljoin
from contextlib import closing
from json import dumps,loads
from sys import stderr
from time import sleep
from kblab.result import create_result
import kblab
import logging

MAX_ID=2**38
MAX_RETRIES=2
MAX_RETRY_WAIT=60

logging.getLogger('requests').setLevel(logging.CRITICAL)
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class HttpArchive(kblab.Archive):
    def __init__(self, root=None, base=None, auth=None):
        url=root
        self.url = url + ('/' if url[-1] != '/' else '')
        self.base = base or url

        if auth:
            if isinstance(auth, dict) and auth['type'] == 'basic':
                self.auth = (auth['user'], auth['pass'])
            elif isinstance(auth, tuple) and len(auth) == 2:
                self.auth = auth
            else:
                raise Exception('unsupported auth configuration')
        else:
            self.auth = None

        n_retries=0
        retry_wait=1
        while True:
            try:
                r = get(urljoin(self.url, 'base'), auth=self.auth, verify=kblab.VERIFY_CA)
            except Exception as e:
                if n_retries == MAX_RETRIES:
                    raise Exception('Max number of retries (%d) reached. %s' % (MAX_RETRIES, str(e)))

                print('Exception while connecting. Retry %d of %s in %d seconds. %s' % (n_retries+1, str(MAX_RETRIES), retry_wait, str(e)), file=stderr, flush=True)
            else:
                if r.status_code in [ 401, 403 ]:
                    raise Exception('Unauthorized. HTTP status = %d' % r.status_code)

                if r.status_code == 200:
                    self.server_base = r.text
                    break;

                if n_retries == MAX_RETRIES:
                    raise Exception('Max number of retries (%d) reached.')
                
                print('Unexpected HTTP status code = %d Retry %d of %s in %d seconds' % (r.status_code, n_retries+1, str(MAX_RETRIES), retry_wait), file=stderr, flush=True)

            n_retries += 1
            sleep(retry_wait)

            if 2*retry_wait < MAX_RETRY_WAIT:
                retry_wait *= 2


    def new(self, **kwargs):
        r = post(urljoin(self.url,'new'), params=kwargs, auth=self.auth, verify=kblab.VERIFY_CA, allow_redirects=False)
        
        if r.status_code != 201:
            raise Exception('expected HTTP status 201, but got %d' % r.status_code)

        url = self.url + r.headers['Location'].split('/')[-2] + '/'

        return (self._get_key(url),
                kblab.Package(
                    url,
                    mode='a',
                    auth=self.auth,
                    server_base=url.replace(self.url, self.base)))


    def ingest(self, package, key=None):
        files = { path:package.get_raw(path) for path in package }
        r = post(self.url + 'ingest', files=files, auth=self.auth, verify=kblab.VERIFY_CA)

        if r.status_code != 201:
            raise Exception('expected HTTP status 201, but got %d with content %s' % (r.status_code, r.text))

        url = r.headers['Location']

        return self._get_key(url)


    def get(self, key, mode='r'):
        try:
            return kblab.Package(
                    self.url + key + '/',
                    mode=mode,
                    base=urljoin(self.base, key + '/'),
                    auth=self.auth,
                    server_base=urljoin(self.server_base, key + '/'))
        except kblab.HttpNotFoundException:
            return None
        except:
            raise


    def delete(self, key, force=False):
        if force:
            p = self.get(key, mode='a')
            r = htdelete(self.url + key + '/', auth=self.auth, verify=kblab.VERIFY_CA)

            if r.status_code == 404:
                return False

            if r.status_code not in  [ 200, 202, 204 ]:
                raise Exception(f'Expected status code 200, 202 or 204, got {r.status_code}')

            return True
        else:
            raise Exception('Use the force (parameter)')


    def search(self, query, start=0, max=None):
        g = self._search_iter(query, start, max)
        i,r,c = next(g).split()

        return create_result(i, r, c, g, self)


    def _search_iter(self, query, start=0, max=None):
        params = { 'q': dumps(query), 'start': start }
        if max: params.update({ 'max': max })

        with closing(get(urljoin(self.url, 'search'),
            params=params,
            verify=kblab.VERIFY_CA,
            auth=self.auth,
            stream=True)) as r:

            if r.status_code == 200:
                 for key in r.raw:
                     yield key[:-1].decode('utf-8')
            else:
                raise Exception('Expected status 200, got %d' % r.status_code)


    def count(self, query, cats={}):
        with closing(get(urljoin(self.url, 'count'),
                         verify=kblab.VERIFY_CA,
                         params={ 'q': dumps(query), 'c': dumps(cats) },
                         auth=self.auth)) as r:
                
            if r.status_code == 200:
                return loads(r.text)
            else:
                raise Exception('Expected status 200, got %d' % r.status_code)


    def get_location(self, key, path):
        return self.url + key + '/' + path


    def keys(self):
        with closing(get(self.url + 'packages', auth=self.auth, stream=True, verify=kblab.VERIFY_CA)) as r:
            if r.status_code == 200:
                for key in r.raw:
                    yield key[:-1].decode('utf-8')
            elif r.status_code != 404:
                raise Exception('server returned status %d' % r.status_code)


    def __iter__(self):
        yield from self.keys()


    def items(self):
        for key in self:
            yield (key, self.get(key))


    def _get_key(self, url):
        if url.startswith(self.url):
            return url[len(self.url):].split('/')[0]

        raise Exception('url (%s) does not start with %s' % (url, self.url))


    def __contains__(self, key):
        with closing(get(self.url + key + '/', auth=self.auth, verify=kblab.VERIFY_CA)) as r:
            return r.status_code == 200


    def __getitem__(self, key):
        return self.get(key)

