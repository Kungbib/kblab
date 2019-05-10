import kblab

VERSION = 0.1

class Package:
    def __new__(cls, first=None, **kwargs):
        if first and isinstance(first, kblab.Package):
            return super(Package, kblab.MultiPackage).__new__(kblab.MultiPackage)
        if first and first.startswith('http'):
            return super(Package, kblab.HttpPackage).__new__(kblab.HttpPackage)
        else:
            return super(Package, kblab.FilePackage).__new__(kblab.FilePackage)

