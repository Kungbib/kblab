class RangeNotSupported(Exception):
    def __init__(self):
        super().__init__()


class HttpNotFoundException(Exception):
    pass

