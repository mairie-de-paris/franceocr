class InvalidMRZException(Exception):
    def __init___(self, message):
        Exception.__init__(self, message)


class InvalidChecksumException(InvalidMRZException):
    def __init___(self, message):
        InvalidMRZException.__init__(self, message)
