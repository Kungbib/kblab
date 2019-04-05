import kblab

class Archive:
    def __new__(cls, root=None, **kwargs):
        if root and (isinstance(root, list) or isinstance(root, kblab.Archive)):
            return super(Archive, kblab.MultiArchive).__new__(kblab.MultiArchive)
        elif root and root.startswith('http'):
            return super(Archive, kblab.HttpArchive).__new__(kblab.HttpArchive)
        else:
            return super(Archive, kblab.FileArchive).__new__(kblab.FileArchive)

