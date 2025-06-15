class NoDownloadLinkException(Exception):
    ...


class OriginalGameNotExistException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Game file not exist!", *args, **kwargs)


class UnknownFileTypeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Unknown file type", *args, **kwargs)


__all__ = [
    'OriginalGameNotExistException',
    'NoDownloadLinkException',
    'UnknownFileTypeException'
]
