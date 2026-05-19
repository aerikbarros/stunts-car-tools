class Car:
    def __init__(self):
        self.p3s = None
        self.pvs_static = None
        self.pvs_moving = None
        self.res = None

        self.ext_3d = None
        self.ext_pvs = None

        self.is_compressed_3d = None
        self.is_compressed_pvs = None

        self.type = None
        self.valid_format = None

    def is_valid(self):
        return self.p3s is not None and self.res is not None
