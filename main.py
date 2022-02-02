from Controller.Fieldsweep import Fieldsweep
from Controller.Controller import DeviceTypes
from Model.SingleMeasurement import SweepTypes
from View.Decorators import  Decorator
from View.SILabel import SILabel, PlotUnits, PlotScales
from glob import glob

import numpy as np

fieldsweep = Fieldsweep(DeviceTypes.Keithley, r"Data\ATEC3-6\20220131_ATEC 3-6_RT_Cooldown.txt")
fieldsweep.startPlot(useTex = False)
fieldsweep.plotResistance(SweepTypes.T_SAMPLE)
fieldsweep.finishPlot()