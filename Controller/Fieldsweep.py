from Controller.Controller import Controller, DeviceTypes
from Model.Keithley import  Keithley
from View.View import View, PlotTypes
from View.Decorators import Decorators
from Model.SingleMeasurement import SweepTypes

class Fieldsweep(Controller):
    def __init__(self, deviceType, paths):
        super().__init__()
        if deviceType == DeviceTypes.Keithley:
            self._dataModel = Keithley(paths)


    def plotSQI(self, fieldAxisSweepType, dVdI=False, deviceID=0, overrideDecorator=None):
        if dVdI:
            plotType = PlotTypes.ColorPlot
            if fieldAxisSweepType == SweepTypes.B_X:
                decorator = Decorators.SQI_dVdI_x.value
            if fieldAxisSweepType == SweepTypes.B_Y:
                decorator = Decorators.SQI_dVdI_y.value
            if fieldAxisSweepType == SweepTypes.B_Z:
                decorator = Decorators.SQI_dVdI_z.value
            dataCapsule = self._dataModel.sweepIdVdI(fieldAxisSweepType, deviceID=deviceID)
        else:
            plotType = PlotTypes.ColorPlot
            if fieldAxisSweepType == SweepTypes.B_X:
                decorator = Decorators.SQI_IV_x.value
            if fieldAxisSweepType == SweepTypes.B_Y:
                decorator = Decorators.SQI_IV_y.value
            if fieldAxisSweepType == SweepTypes.B_Z:
                decorator = Decorators.SQI_IV_z.value
            dataCapsule = self._dataModel.sweepIV(fieldAxisSweepType, deviceID=deviceID)

        if overrideDecorator is not None:
            decorator.overrideDecorator(overrideDecorator)

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
            decorator = Decorators.Ic_MagneticField_x.value
        elif fieldAxisSweepType == SweepTypes.B_Y:
            decorator = Decorators.Ic_MagneticField_y.value
        elif fieldAxisSweepType == SweepTypes.B_Z:
            decorator = Decorators.Ic_MagneticField_z.value
        elif fieldAxisSweepType == SweepTypes.T_VTI or fieldAxisSweepType == SweepTypes.T_SAMPLE:
            decorator = Decorators.Ic_T.value

        if overrideDecorator is not None:
            decorator.overrideDecorator(overrideDecorator)

        if self._view == None:
            self.startPlot()

        if plotID is None:
            plotID = self._view.subplotFromDataCapsules([xIcDataCapsule], plotType, decorator)
        else:
            self._view.addDatacapsuleToSubplot(xIcDataCapsule, plotID)
        return plotID

    def plotIVs(self, fieldAxisSweepType, deviceID=0, overrideDecorator=None, plotID = None, selection=None, sweepRange=None):
        plotIDs = []

        decorator = Decorators.Current_Voltage.value
        plotType = PlotTypes.Scatter2D

        if self._view == None:
            self.startPlot()

        if overrideDecorator is not None:
            decorator.overrideDecorator(overrideDecorator)

        dataCapsules2D = self._dataModel.getIVs(fieldAxisSweepType, deviceID=deviceID, selection=selection, sweepRange=sweepRange)

        if plotID is None:
            plotID = self._view.subplotFromDataCapsules(dataCapsules2D, plotType, decorator)
        else:
            for dataCapsule in dataCapsules2D:
                self._view.addDatacapsuleToSubplot(dataCapsule, plotID)

        return plotID

    def plotConstantBias(self, fieldAxisSweepType, ybias, deviceID=0, overrideDecorator=None, plotID = None, selection=None, sweepRange=None):
        plotIDs = []

        dataCapsules = []

        if not isinstance(ybias, list):
            ybias = [ybias]

        for yb in ybias:
            dataCapsules.append(
                self._dataModel.getConstantBias(fieldAxisSweepType, yb, deviceID=deviceID, selection=selection,
                                                sweepRange=sweepRange))

        if fieldAxisSweepType == SweepTypes.B_X:
            decorator = Decorators.ConstantBias_MagneticField_x.value
        elif fieldAxisSweepType == SweepTypes.B_Y:
            decorator = Decorators.ConstantBias_MagneticField_y.value
        elif fieldAxisSweepType == SweepTypes.B_Z:
            decorator = Decorators.ConstantBias_MagneticField_z.value
        elif fieldAxisSweepType == SweepTypes.T_VTI or fieldAxisSweepType == SweepTypes.T_SAMPLE:
            decorator = Decorators.ConstantBias_T.value

        plotType = PlotTypes.Scatter2D

        if self._view == None:
            self.startPlot()

        if overrideDecorator is not None:
            decorator.overrideDecorator(overrideDecorator)

        if plotID is None:
            plotID = self._view.subplotFromDataCapsules(dataCapsules, plotType, decorator)
        else:
            for capsule in dataCapsules:
                self._view.addDatacapsuleToSubplot(capsule, plotID)
        return plotID

    def plotResistance(self, fieldAxisSweepType, deviceID=0, overrideDecorator=None, plotID = None, insetID = None, selection=None, sweepRange=None):
        dataCapsule = self._dataModel.getResistance(fieldAxisSweepType, selection=selection, sweepRange=sweepRange)

        if fieldAxisSweepType == SweepTypes.B_X:
            decorator = Decorators.Resistance_MagneticField_x.value
        elif fieldAxisSweepType == SweepTypes.B_Y:
            decorator = Decorators.Resistance_MagneticField_y.value
        elif fieldAxisSweepType == SweepTypes.B_Z:
            decorator = Decorators.Resistance_MagneticField_z.value
        elif fieldAxisSweepType == SweepTypes.T_VTI or fieldAxisSweepType == SweepTypes.T_SAMPLE:
            decorator = Decorators.Resistance_T.value

        plotType = PlotTypes.Scatter2D

        if self._view is None:
            self.startPlot()

        if overrideDecorator is not None:
            decorator.overrideDecorator(overrideDecorator)

        if insetID is None:
            # Make a top-level plot:
            if plotID is None:
                plotID = self._view.subplotFromDataCapsules(dataCapsule, plotType, decorator)
            else:
                self._view.addDatacapsuleToSubplot(dataCapsule, plotID)
        else:
            # Make an inset in a plot:
            self._view.insetFromDataCapsules(dataCapsule, plotType, decorator, plotID)
        return plotID

    def removeSeriesResistance(self, deviceID=0, Npoints=4):
        self._dataModel.removeSeriesResistance(deviceID=deviceID, Npoints=Npoints)