from Controller.Fieldsweep import Fieldsweep
from Controller.Controller import DeviceTypes
from Model.SingleMeasurement import SweepTypes
from View.Decorators import  Decorator
from View.SILabel import SILabel, PlotUnits, PlotScales
from glob import glob

import numpy as np

cooldown_before = Fieldsweep(DeviceTypes.Keithley, r"Data\ATEC3-6\RT-15K-ATEC3-6")
#cooldown_after  = Fieldsweep(DeviceTypes.Keithley, r"Data\ATEC3-6\20220131_ATEC 3-6_RT_Cooldown.txt")

cooldown_before.startPlot(useTex = False)
cooldown_before.plotResistance(SweepTypes.T_SAMPLE)
cooldown_before.plotResistance(SweepTypes.T_SAMPLE, plotID=0, insetID=0)
#cooldown_after.subscribeToView(cooldown_before)
#cooldown_after.plotResistance(SweepTypes.T_SAMPLE, plotID=0)
cooldown_before.finishPlot()