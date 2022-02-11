from Controller.Controller import Controller, DeviceTypes
from Model.Keithley import Keithley
from Model.ZILockin import ZILockin
from View.View import View, PlotTypes
from View.Decorators import Decorators
from Model.SingleMeasurement import SweepTypes
from View.SILabel import SILabel, PlotUnits, PlotScales
from DataCapsule.DataCapsules import Label
import numpy as np

class Fieldsweep(Controller):
    def __init__(self, deviceType, paths):
        super().__init__()
        if deviceType == DeviceTypes.Keithley:
            self._dataModel = Keithley(paths)
        elif deviceType == DeviceTypes.ZILockin:
            self._dataModel = ZILockin(paths)

    def plotLockinMagnitude(self, fieldAxisSweepType, overrideDecorator=None, plotID = None,
                            insetID = None, overrideLabel=None):
        plotType = PlotTypes.Scatter2D
        if fieldAxisSweepType == SweepTypes.B_X:
            baseDecorator = Decorators.Lockin_Magnitude_MagneticField_x.value
        if fieldAxisSweepType == SweepTypes.B_Y:
            baseDecorator = Decorators.Lockin_Magnitude_MagneticField_y.value
        if fieldAxisSweepType == SweepTypes.B_Z:
            baseDecorator = Decorators.Lockin_Magnitude_MagneticField_z.value

        dataCapsule = self._dataModel.sweepR(fieldAxisSweepType)

        if overrideLabel is not None:
            dataCapsule.label = overrideLabel

        if self._view == None:
            self.startPlot()

        if overrideDecorator is None:
            decorator = baseDecorator
        else:
            overrideDecorator.overrideDecorator(baseDecorator)
            decorator = overrideDecorator

        if insetID is None:
            # Make a top-level plot:
            if plotID is None:
                plotID = self._view.subplotFromDataCapsules(dataCapsule, plotType, decorator)
            else:
                self._view.addDatacapsuleToSubplot(dataCapsule, plotID)
        else:
            # Make an inset in a plot:
            self._view.insetFromDataCapsules(dataCapsule, plotType, decorator, plotID, insetID)

        return plotID

    def plotSQI(self, fieldAxisSweepType, dVdI=False, deviceID=0, overrideDecorator=None):
        if dVdI:
            plotType = PlotTypes.ColorPlot
            if fieldAxisSweepType == SweepTypes.B_X:
                baseDecorator = Decorators.SQI_dVdI_x.value
            if fieldAxisSweepType == SweepTypes.B_Y:
                baseDecorator = Decorators.SQI_dVdI_y.value
            if fieldAxisSweepType == SweepTypes.B_Z:
                baseDecorator = Decorators.SQI_dVdI_z.value
            dataCapsule = self._dataModel.sweepIdVdI(fieldAxisSweepType, deviceID=deviceID)
        else:
            plotType = PlotTypes.ColorPlot
            if fieldAxisSweepType == SweepTypes.B_X:
                baseDecorator = Decorators.SQI_IV_x.value
            if fieldAxisSweepType == SweepTypes.B_Y:
                baseDecorator = Decorators.SQI_IV_y.value
            if fieldAxisSweepType == SweepTypes.B_Z:
                baseDecorator = Decorators.SQI_IV_z.value
            dataCapsule = self._dataModel.sweepIV(fieldAxisSweepType, deviceID=deviceID)

        if overrideDecorator is None:
            decorator = baseDecorator
        else:
            overrideDecorator.overrideDecorator(baseDecorator)
            decorator = overrideDecorator

        if self._view == None:
            self.startPlot()
        plotID = self._view.subplotFromDataCapsules([dataCapsule], plotType, decorator)
        return plotID

    def plotIC(self, fieldAxisSweepType, fromdVdI=False, vThreshold = None, dVdIThreshold = None, deviceID=0,
               plotID = None, selection=None, sweepRange=None, overrideDecorator=None, positiveCurrents=True):
        if fromdVdI:
            xIcDataCapsule = self._dataModel.ICFromIdVdI(fieldAxisSweepType, dVdIThreshold, deviceID = deviceID, selection=selection, sweepRange=sweepRange, positiveCurrent=positiveCurrents)
        else:
            xIcDataCapsule = self._dataModel.ICFromIV(fieldAxisSweepType, vThreshold, deviceID = deviceID, selection=selection, sweepRange=sweepRange, positiveCurrent=positiveCurrents)

        plotType = PlotTypes.Scatter2D

        if fieldAxisSweepType == SweepTypes.B_X:
            baseDecorator = Decorators.Ic_MagneticField_x.value
        elif fieldAxisSweepType == SweepTypes.B_Y:
            baseDecorator = Decorators.Ic_MagneticField_y.value
        elif fieldAxisSweepType == SweepTypes.B_Z:
            baseDecorator = Decorators.Ic_MagneticField_z.value
        elif fieldAxisSweepType == SweepTypes.T_VTI or fieldAxisSweepType == SweepTypes.T_SAMPLE:
            baseDecorator = Decorators.Ic_T.value

        if overrideDecorator is None:
            decorator = baseDecorator
        else:
            overrideDecorator.overrideDecorator(baseDecorator)
            decorator = overrideDecorator

        if self._view == None:
            self.startPlot()

        if plotID is None:
            plotID = self._view.subplotFromDataCapsules([xIcDataCapsule], plotType, decorator)
        else:
            self._view.addDatacapsuleToSubplot(xIcDataCapsule, plotID)
        return plotID

    def plotIVs(self, fieldAxisSweepType, deviceID=0, overrideDecorator=None, plotID = None, insetID = None,
                selection=None, sweepRange=None):
        plotIDs = []

        baseDecorator = Decorators.Current_Voltage.value
        plotType = PlotTypes.Scatter2D

        if self._view == None:
            self.startPlot()

        if overrideDecorator is None:
            decorator = baseDecorator
        else:
            overrideDecorator.overrideDecorator(baseDecorator)
            decorator = overrideDecorator

        dataCapsules2D = self._dataModel.getIVs(fieldAxisSweepType, deviceID=deviceID, selection=selection,
                                                sweepRange=sweepRange)

        if insetID is None:
            # Make a top-level plot:
            if plotID is None:
                plotID = self._view.subplotFromDataCapsules(dataCapsules2D, plotType, decorator)
            else:
                for dataCapsule in dataCapsules2D:
                    self._view.addDatacapsuleToSubplot(dataCapsule, plotID)
        else:
            # Make an inset in a plot:
            self._view.insetFromDataCapsules(dataCapsules2D, plotType, decorator, plotID, insetID)

        return plotID

    def plotConstantBias(self, fieldAxisSweepType, ybias, deviceID=0, overrideDecorator=None, plotID = None, insetID = None, selection=None, sweepRange=None):
        plotIDs = []

        dataCapsules = []

        if not isinstance(ybias, list) and not isinstance(ybias, np.ndarray):
            ybias = [ybias]

        for yb in ybias:
            dataCapsules.append(
                self._dataModel.getConstantBias(fieldAxisSweepType, yb, deviceID=deviceID, selection=selection,
                                                sweepRange=sweepRange))
            dataCapsules[-1].label = Label(labelfloat=yb, labelfloatSILabel=SILabel(PlotUnits.BiasCurrent, PlotScales.Micro))

        if fieldAxisSweepType == SweepTypes.B_X:
            baseDecorator = Decorators.ConstantBias_MagneticField_x.value
        elif fieldAxisSweepType == SweepTypes.B_Y:
            baseDecorator = Decorators.ConstantBias_MagneticField_y.value
        elif fieldAxisSweepType == SweepTypes.B_Z:
            baseDecorator = Decorators.ConstantBias_MagneticField_z.value
        elif fieldAxisSweepType == SweepTypes.T_VTI or fieldAxisSweepType == SweepTypes.T_SAMPLE:
            baseDecorator = Decorators.ConstantBias_T.value

        plotType = PlotTypes.Scatter2D

        if self._view == None:
            self.startPlot()

        if overrideDecorator is None:
            decorator = baseDecorator 
        else:
            overrideDecorator.overrideDecorator(baseDecorator)
            decorator = overrideDecorator

        if insetID is None:
            # Make a top-level plot:
            if plotID is None:
                plotID = self._view.subplotFromDataCapsules(dataCapsules, plotType, decorator)
            else:
                for capsule in dataCapsules:
                    self._view.addDatacapsuleToSubplot(capsule, plotID)
        else:
            # Make an inset in a plot:
            self._view.insetFromDataCapsules(dataCapsules, plotType, decorator, plotID, insetID)
        return plotID

    def plotResistance(self, fieldAxisSweepType, deviceID=0, overrideDecorator=None, plotID = None, insetID = None, selection=None, sweepRange=None, overrideLabel=None):
        dataCapsule = self._dataModel.getResistance(fieldAxisSweepType, selection=selection, sweepRange=sweepRange)
        dataCapsule.label = overrideLabel if overrideLabel is not None else dataCapsule.label

        if fieldAxisSweepType == SweepTypes.B_X:
            baseDecorator = Decorators.Resistance_MagneticField_x.value
        elif fieldAxisSweepType == SweepTypes.B_Y:
            baseDecorator = Decorators.Resistance_MagneticField_y.value
        elif fieldAxisSweepType == SweepTypes.B_Z:
            baseDecorator = Decorators.Resistance_MagneticField_z.value
        elif fieldAxisSweepType == SweepTypes.T_VTI or fieldAxisSweepType == SweepTypes.T_SAMPLE:
            baseDecorator = Decorators.Resistance_T.value

        plotType = PlotTypes.Scatter2D

        if self._view is None:
            self.startPlot()

        if overrideDecorator is None:
            decorator = baseDecorator 
        else:
            overrideDecorator.overrideDecorator(baseDecorator)
            decorator = overrideDecorator

        if insetID is None:
            # Make a top-level plot:
            if plotID is None:
                plotID = self._view.subplotFromDataCapsules(dataCapsule, plotType, decorator)
            else:
                self._view.addDatacapsuleToSubplot(dataCapsule, plotID)
        else:
            # Make an inset in a plot:
            self._view.insetFromDataCapsules(dataCapsule, plotType, decorator, plotID, insetID)
        return plotID

    def removeSeriesResistance(self, deviceID=0, Npoints=4):
        self._dataModel.removeSeriesResistance(deviceID=deviceID, Npoints=Npoints)