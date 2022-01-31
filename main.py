from Controller.Fieldsweep import Fieldsweep
from Controller.Controller import DeviceTypes
from Model.SingleMeasurement import SweepTypes
from View.Decorators import  Decorator
from View.SILabel import SILabel, PlotUnits, PlotScales
from glob import glob

import numpy as np

sqiDecorator = Decorator(zlim=[-10,10], cmap='bwr')
icDecorator = Decorator(connectDots=False, fitcolor='red')

fieldsweep = Fieldsweep(DeviceTypes.Keithley, r"Data\ATEC3-6\Fieldsweeps\X-axis-fieldsweep-highres-gaussian-70uA-IV.txt")
fieldsweep.startPlot(useTex = False)
fieldsweep.removeSeriesResistance()
fieldsweep.plotConstantBias(SweepTypes.B_X, 60e-6)
print("Time to plot!")
fieldsweep.finishPlot(r"P:\STMSOT\ATEC3-6\Images\IcTSmallTransition.png")