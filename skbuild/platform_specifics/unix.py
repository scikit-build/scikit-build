from . import abstract


class UnixPlatform(abstract.CMakePlatform):

    def __init__(self):
        super(UnixPlatform, self).__init__()
        self.default_generators = ["Unix Makefiles", ]

