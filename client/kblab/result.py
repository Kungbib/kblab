import kblab
from typing import NamedTuple
from collections import namedtuple
from collections.abc import Iterator
from multiprocessing import Pool

Hit = namedtuple('Hit', [ 'key', 'package' ])

class Result(NamedTuple):
    start: int
    n: int
    m: int
    keys: Iterator
    hits: Iterator

    def __iter__(self):
        return self.keys

    def map(self, f, processes=None, ordered=True, multi=False):
        if multi:
            with Pool(processes=processes) as pool:
               for x in pool.imap(f, self) if ordered else pool.imap_unordered(f, self):
                    yield x
        else:
            for x in map(f, self):
                yield x

def create_result(start, n, m, key_iter, archive):
    return Result(
            start,
            n,
            m,
            key_iter,
            package_generator(key_iter, archive) if archive else iter([]))


def package_generator(keys, archive):
    for key in keys:
        yield Hit(key, archive.get(key))

