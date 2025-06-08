class NoDownloadLinkException(Exception):
    ...


class UnknownFileTypeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Unknown file type", *args, **kwargs)


__all__ = [
    'NoDownloadLinkException',
    'UnknownFileTypeException'
]
