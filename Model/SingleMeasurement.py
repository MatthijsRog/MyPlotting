import numpy as np
from enum import Enum, auto

class SweepTypes(Enum):
    T_VTI = auto()
    T_SAMPLE = auto()
    B_X = auto()
    B_Y = auto()
    B_Z = auto()

class SingleMeasurement():
    VTITemperature = -1.0
    sampleTemperature = -1.0
    Bx = 0.0
    By = 0.0
    Bz = 0.0

    def environmental(self, sweepType):
        if sweepType==SweepTypes.B_X:
            return self.Bx
        elif sweepType==SweepTypes.B_Y:
            return self.By
        elif sweepType==SweepTypes.B_Z:
            return self.Bz
        elif sweepType==SweepTypes.T_VTI:
            return self.VTITemperature
        elif sweepType==SweepTypes.T_SAMPLE:
            return self.sampleTemperature
        else:
            raise TypeError("Unknown axis type.")