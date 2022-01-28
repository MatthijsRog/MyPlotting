class DataCapsule():
    label = None

    def __init__(self, label=None):
        self.label = label

class Label():
    labeltext = None # If not None, always plotted
    labelfloat = None # If labeltext is None but labelfloat is not None, plotted
    labelfloatSILabel = None # SILabel used for labelfloat if not None. If None, y-axis Label is defaulted.

    def __init__(self, labeltext = None, labelfloat = None, labelfloatSILabel = None):
        self.labeltext = labeltext
        self.labelfloat = labelfloat
        self.labelfloatSILabel = labelfloatSILabel

class RegularData3D(DataCapsule):
    """Presents 3D data, regular in X and Y, on an (X,Y) grid."""
    xx = None
    yy = None
    zz = None

    def __init__(self, xx, yy, zz, label=None):
        self.xx = xx
        self.yy = yy
        self.zz = zz
        super().__init__(label=label)

class IrregularData3D(DataCapsule):
    """Presents 3D data with irregular Y lengths as follows: X is an array, Y a list of arrays, Z the same shape as Y."""
    x = None
    ylist = None
    zlist = None

    def __init__(self, x, ylist, zlist, label=None):
        self.x = x
        self.ylist = ylist
        self.zlist = zlist
        super().__init__(label=label)


class Data2D(DataCapsule):
    """Presents 2D data."""
    x = None
    y = None

    def __init__(self, x, y, label=None):
        self.x = x
        self.y = y
        super().__init__(label=label)

class SmoothFunction2D(DataCapsule):
    """Encapsulates smooth 2D functions."""
    func = None
    NPoints = None

    def __init__(self, func, NPoints, label=None):
        self.func = func
        self.NPoints = NPoints
        super().__init__(label=label)