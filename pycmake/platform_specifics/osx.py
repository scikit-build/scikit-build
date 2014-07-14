import abstract

class OSXPlatform(abstract.CMakePlatform):
    def __init__(self):
        super(OSXPlatform, self).__init__()
        self.default_generators = ["Unix Makefiles", ]