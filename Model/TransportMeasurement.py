from abc import ABC, abstractmethod
from itertools import compress

import numpy as np

from DataCapsule.DataCapsules import RegularData3D, IrregularData3D, Data2D, Label
from Model.SingleMeasurement import SweepTypes
from View.SILabel import SILabel, PlotUnits, PlotScales


class TransportMeasurement(ABC):
    @abstractmethod
    def sweepIV(self, sweepType, deviceID=0):
        pass

    @abstractmethod
    def sweepIdVdI(self, sweepType, deviceID=0):
        pass

    @abstractmethod
    def removeSeriesResistance(self, deviceID=0, Npoints=4):
        pass

    def ICFromIdVdI(self, sweepType, dVdIThreshold, deviceID=0, positiveCurrent = True, sweepRange = None, selection = None):
        dataCapsule = self.sweepIdVdI(sweepType, deviceID=deviceID)
        dataCapsule = self._selectSweepValuesDataCapsule(dataCapsule, sweepRange=sweepRange, selection = selection)
        if isinstance(dataCapsule, RegularData3D):
            return self._ICFromRegularData3D(dVdIThreshold, dataCapsule, posyonly=positiveCurrent, negyonly=not positiveCurrent)
        elif isinstance(dataCapsule, IrregularData3D):
            return self._ICFromIrregularData(dVdIThreshold, dataCapsule, posyonly=positiveCurrent, negyonly=not positiveCurrent)
        else:
            raise TypeError("Unknown datacapsule type.")

    def getConstantBias(self, sweepType, yb, deviceID=0, selection=None, sweepRange=None):
        allIVs = self.sweepIV(sweepType, deviceID=deviceID)
        allIVs = self._selectSweepValuesDataCapsule(allIVs, sweepRange=sweepRange, selection=selection)

        if isinstance(allIVs, RegularData3D):
            return self._getConstantBiasRegular(allIVs, yb)
        elif isinstance(allIVs, IrregularData3D):
            return self._getConstantBiasIrregular(allIVs, yb)

    def _getConstantBiasRegular(self, allIVs, yb):
        xs = allIVs.xx[0,:]
        ys = allIVs.yy[:,0]
        index = np.argmin(np.abs(ys - yb))
        zs = allIVs.zz[index,:]

        curve = Data2D(xs, zs)
        curve.labelfloat = yb

        return curve

    def _getConstantBiasIrregular(self, allIVs, yb):
        xs = allIVs.x
        zs = np.zeros_like(xs)
        for i, x in enumerate(xs):
            y = allIVs.ylist[i]
            index = np.argmin(np.abs(y - yb))
            zs[i] = allIVs.zlist[i][index]

        curve = Data2D(xs, zs)
        curve.labelfloat = yb

        return curve


    def ICFromIV(self, sweepType, vThreshold, deviceID=0, positiveCurrent = True, sweepRange = None, selection = None):
        dataCapsule = self.sweepIV(sweepType, deviceID=deviceID)
        dataCapsule = self._selectSweepValuesDataCapsule(dataCapsule, sweepRange=sweepRange, selection=selection)
        if isinstance(dataCapsule, RegularData3D):
            return self._ICFromRegularData3D(vThreshold, dataCapsule, posyonly=positiveCurrent, negyonly=not positiveCurrent)
        elif isinstance(dataCapsule, IrregularData3D):
            return self._ICFromIrregularData(vThreshold, dataCapsule, posyonly=positiveCurrent, negyonly=not positiveCurrent)
        else:
            raise TypeError("Unknown datacapsule type.")

    def _ICFromRegularData3D(self, zThreshold: float, regularDataCapsule: RegularData3D, posyonly=False, negyonly=False):
        x = regularDataCapsule.xx[0, :]
        II = regularDataCapsule.yy
        zz = regularDataCapsule.zz
        Ic = np.zeros_like(x)

        if posyonly:
            mask = II > 0
        elif negyonly:
            mask = II < 0
        else:
            mask = II > -np.inf

        for i in range(len(x)):
            I = II[:,i][mask[:,i]]
            z = zz[:,i][mask[:,i]]

            if negyonly:
                Ic[i] = (I[::-1])[np.argmax(z[::-1] > zThreshold)]
            else:
                Ic[i] = I[np.argmax(z > zThreshold)]  # I[np.argmin(np.abs(z - zThreshold))]


        return Data2D(x, Ic)

    def _ICFromIrregularData(self, zThreshold: float, irregularDataCapsule: IrregularData3D, posyonly=False, negyonly=False):
        x = irregularDataCapsule.x
        Ilist = irregularDataCapsule.ylist
        zlist = irregularDataCapsule.zlist
        Ic = np.zeros_like(x)

        for i, I in enumerate(Ilist):
            z = zlist[i]

            if posyonly:
                mask = I > 0
            elif negyonly:
                mask = I < 0
            else:
                mask = I > -np.inf

            z = z[mask]

            Ic[i] = I[mask][np.argmax(z > zThreshold)]

        return Data2D(x, Ic)

    def getIVs(self, sweepType, deviceID=0, sweepRange=None, selection=None):
        """Gets IV curves from the underlying dataset. """
        dataCapsule = self.sweepIV(sweepType, deviceID=deviceID)
        if isinstance(dataCapsule, RegularData3D):
            return self._getIVRegular(dataCapsule, sweepType, sweepRange = sweepRange, selection = selection)
        elif isinstance(dataCapsule, IrregularData3D):
            return self._getIVIrregular(dataCapsule, sweepType, sweepRange = sweepRange, selection = selection)
        else:
            raise TypeError("Unknown datacapsule type.")

    def _getIVRegular(self, dataCapsule, sweepType, sweepRange = None, selection = None):
        dataCapsules2D = []
        xs = dataCapsule.xx[0,:]
        mask = self._getMaskForX(xs, sweepRange=sweepRange, selection=selection)

        if sweepType == SweepTypes.B_X or sweepType == SweepTypes.B_Y or sweepType == SweepTypes.B_Z:
            silabel = SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli)
        elif sweepType == SweepTypes.T_VTI or sweepType == SweepTypes.T_SAMPLE:
            silabel = SILabel(PlotUnits.Temperature, PlotScales.Unit)

        for i, x in enumerate(xs):
            if mask[i]:
                label = Label(labelfloat=x, labelfloatSILabel=silabel)
                dataCapsules2D.append(Data2D(dataCapsule.yy[:,i], dataCapsule.zz[:,i], label=label))

        return dataCapsules2D

    def _getIVIrregular(self, dataCapsule, sweepType, sweepRange = None, selection = None):
        dataCapsules2D = []
        xs = dataCapsule.x
        mask = self._getMaskForX(xs, sweepRange=sweepRange, selection=selection)

        if sweepType == SweepTypes.B_X or sweepType == SweepTypes.B_Y or sweepType == SweepTypes.B_Z:
            silabel = SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli)
        elif sweepType == SweepTypes.T_VTI or sweepType == SweepTypes.T_SAMPLE:
            silabel = SILabel(PlotUnits.Temperature, PlotScales.Unit)

        for i, x in enumerate(xs):
            if mask[i]:
                label = Label(labelfloat=x, labelfloatSILabel=silabel)
                dataCapsules2D.append(Data2D(dataCapsule.ylist[i], dataCapsule.zlist[i], label=label))

        return dataCapsules2D

    def _selectSweepValuesDataCapsule(self, dataCapsule, sweepRange=None, selection=None):
        if isinstance(dataCapsule, RegularData3D):
            x = dataCapsule.xx[0,:]
            mask = self._getMaskForX(x, sweepRange=sweepRange, selection=selection)
            return RegularData3D(dataCapsule.xx[:,mask], dataCapsule.yy[:,mask], dataCapsule.zz[:,mask])
        elif isinstance(dataCapsule, IrregularData3D):
            x = dataCapsule.x
            mask = self._getMaskForX(x, sweepRange=sweepRange, selection=selection)
            return IrregularData3D(dataCapsule.x[mask], list(compress(dataCapsule.ylist,mask)), list(compress(dataCapsule.zlist,mask)))
        else:
            TypeError("This type of datacapsule does not support masking.")

    def _getMaskForX(self, x, sweepRange=None, selection=None):
        if sweepRange is not None:
            x0 = sweepRange[0]
            x1 = sweepRange[1]
            mask = (x >= x0) & (x <= x1)
        elif selection is not None:
            mask = selection
        else:
            mask = x > -np.inf
        return mask