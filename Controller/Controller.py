from __future__ import annotations
from enum import Enum, auto
from View.View import View
from DataCapsule.DataCapsules import SmoothFunction2D, Label
from scipy.optimize import curve_fit

class DeviceTypes(Enum):
    Keithley = auto()
    Synktek = auto()
    ZILockin = auto()

class Controller:
    def __init__(self):
        self._dataModel = None
        self._view = None

    def startPlot(self, useTex = False):
        self._view = View(useTex=useTex)

    def subscribeToView(self, controller: Controller):
        self._view = controller._view

    def finishPlot(self, savepath=None):
        self._view.plotAll(savepath=savepath)

    def addOverlayFunction(self, func, params, NPoints=500, plotID=-1, label=None):
        dataCapsule = SmoothFunction2D(lambda x: func(x, *params), NPoints, label=label)
        self._view.addDatacapsuleToSubplot(dataCapsule, plotID)

    def fitFunction(self, func, params0, NPoints=500, plotID=-1, dataCapsuleID=-1, x0 = None, x1 = None, paramLabelID = None, overrideLabel=None, overrideLabelSILabel=None,
                    paramLabelIndex=None):
        dataCapsule = self._view.dataCapsule(plotID, dataCapsuleID)
        x = dataCapsule.x
        y = dataCapsule.y

        if x0 is not None:
            fitmask = (x > x0) & (x < x1)
            x = x[fitmask]
            y = y[fitmask]

        param, pcov = curve_fit(func, x, y, p0=params0)

        if overrideLabel is None:
            if paramLabelID is not None:
                label = Label(labelfloat=param[paramLabelID])
                if overrideLabelSILabel is not None:
                    label.labelfloatSILabel = overrideLabelSILabel
            else:
                label = Label(labeltext="Fit")
        else:
            label = overrideLabel

        self.addOverlayFunction(func, param, NPoints, plotID, label=label)

        return param, pcov