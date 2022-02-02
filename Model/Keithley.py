from Model.Model import VectorMagnetModel
from Model.TransportMeasurement import TransportMeasurement
from Model.SingleMeasurement import SingleMeasurement
from DataCapsule.DataCapsules import RegularData3D, IrregularData3D, Data2D
from typing import NamedTuple
import numpy as np
from scipy.optimize import curve_fit

class Keithley(VectorMagnetModel, TransportMeasurement):
    def __init__(self, paths):
        super().__init__()
        if isinstance(paths, list):
            for path in paths:
                if isinstance(path, str):
                    self.loadDataFromFile(path)
                else:
                    raise TypeError("Paths contains a non-string element.")
        elif isinstance(paths, str):
            self.loadDataFromFile(paths)
        else:
            raise TypeError("Paths is not a list of strings, or a string.")

    def loadDataFromFile(self, path):
        VTITemperature, sampleTemperature, Bx, By, Bz = self.vectorMagnetTemperatureAndField(path)
        currentPerDevice, voltagePerDevice = self.loadCurrentAndVoltagePerDevice(path)
        singleMeasurementFirstIndices = self.singleMeasurementFirstIndices([VTITemperature, sampleTemperature, Bx, By, Bz])

        for i, start in enumerate(singleMeasurementFirstIndices):
            if i < len(singleMeasurementFirstIndices) - 1:
                end = singleMeasurementFirstIndices[i+1]
            else:
                end = len(VTITemperature)

            ivPerDevice = []
            for deviceID in range(len(currentPerDevice)):
                iv = KeithleyIV(current = currentPerDevice[deviceID][start:end],
                                voltage = voltagePerDevice[deviceID][start:end])
                ivPerDevice.append(iv)
            self._data.append(KeithleyData(VTITemperature[start],
                                      sampleTemperature[start],
                                      Bx[start],
                                      By[start],
                                      Bz[start],
                                      ivPerDevice))

    def loadCurrentAndVoltagePerDevice(self, path):
        return self.load2DDataForVectorMagnet(path, "I", "V")

    def isRegular(self, deviceID=0):
        isRegular = True

        # Check if all I-axes are equally long, so that the data can be put into a grid:
        for data in self._data:
            if len(data.IVPerDevice[deviceID].current) != len(self._data[0].IVPerDevice[deviceID].current):
                isRegular = False
                break

        return isRegular

    def sweepResistance(self, sweepType, deviceID=0):
        """Returns (x,R) data for some environmental x."""
        x = np.zeros(len(self._data))
        y = np.zeros_like(x)

        for i in range(len(x)):
            x[i] = self._data[i].environmental(sweepType)
            y[i] = self._data[i].resistance(deviceID=deviceID)

        return Data2D(x,y)

    def sweepIV(self, sweepType, deviceID=0):
        """Returns (x,I,V) data for some environmental variable x."""
        if self.isRegular(deviceID=0):
            xx = np.zeros((len(self._data[0].IVPerDevice[deviceID].current), len(self._data)))
            II = np.zeros_like(xx)
            VV = np.zeros_like(II)

            for i, data in enumerate(self._data):
                xx[:, i] = data.environmental(sweepType)
                II[:, i] = data.IVPerDevice[deviceID].current
                VV[:, i] =  data.IVPerDevice[deviceID].voltage

            capsule = RegularData3D(xx, II, VV)

        else:
            x = np.zeros(len(self._data))
            I = []
            V = []

            for i, data in enumerate(self._data):
                x[i] = data.environmental(sweepType)
                I.append(data.IVPerDevice[deviceID].current)
                V.append(data.IVPerDevice[deviceID].voltage)

            capsule = IrregularData3D(x, I, V)

        return capsule

    def sweepIdVdI(self, sweepType, deviceID=0):
        """Returns (x,I,V) data for some environmental variable x."""
        if self.isRegular(deviceID=0):
            xx = np.zeros((len(self._data[0].IVPerDevice[deviceID].current), len(self._data)))
            II = np.zeros_like(xx)
            dVdIGrid = np.zeros_like(xx)

            for i, data in enumerate(self._data):
                xx[:, i] = data.environmental(sweepType)
                II[:, i] = data.IVPerDevice[deviceID].current
                dVdIGrid[:, i] = self.derivative(II[:,i], data.IVPerDevice[deviceID].voltage)

            capsule = RegularData3D(xx, II, dVdIGrid)

        else:
            x = np.zeros(len(self._data))
            I = []
            dVdI = []

            for i, data in enumerate(self._data):
                x[i] = data.environmental(sweepType)
                I.append(data.IVPerDevice[deviceID].current)
                dVdI.append(self.derivative(data.IVPerDevice[deviceID].current, data.IVPerDevice[deviceID].voltage))

            capsule = IrregularData3D(x, I, dVdI)

        return capsule

    def removeSeriesResistance(self, deviceID=0, Npoints=4):
        smallestResistance = np.inf

        for ivdata in self._data:
            current = ivdata.IVPerDevice[deviceID].current
            voltage = ivdata.IVPerDevice[deviceID].voltage

            centerindex = np.argmin(np.abs(current))
            if centerindex == 0:
                centerindex = 1

            dvdi = (voltage[centerindex+Npoints] - voltage[centerindex-Npoints]) / (current[centerindex+Npoints] - current[centerindex-Npoints])
            param, _ = curve_fit(lambda x,a,b: a*x+b, current[centerindex-Npoints:centerindex+Npoints+1], voltage[centerindex-Npoints:centerindex+Npoints+1], p0=[dvdi, 0.0])
            if param[0] < smallestResistance:
                smallestResistance = param[0]

        if smallestResistance > 0:
            print("Subtracting residual resistance of", round(smallestResistance*1e3), "mOhms")

            for i, ivdata in enumerate(self._data):
                newIV = KeithleyIV(current=ivdata.IVPerDevice[deviceID].current,
                                   voltage=ivdata.IVPerDevice[deviceID].voltage - ivdata.IVPerDevice[deviceID].current*smallestResistance)
                self._data[i].IVPerDevice[deviceID] = newIV
        else:
            print("Smallest resistance was non-positive, not modifying dataset.")



class KeithleyData(SingleMeasurement):
    def __init__(self, VTITemperature, sampleTemperature, Bx, By, Bz, IVPerDevice):
        self.VTITemperature = float(VTITemperature)
        self.sampleTemperature = float(sampleTemperature)
        self.Bx = float(Bx)
        self.By = float(By)
        self.Bz = float(Bz)
        if isinstance(IVPerDevice, list):
            self.IVPerDevice = IVPerDevice
        else:
            raise TypeError("IVPerDevice member of KeithleyData must be a list of device indices pointing to IV curves.")

    def resistance(self, deviceID=0):
        iv = self.IVPerDevice[deviceID]
        params, _ = curve_fit(lambda x, a, b: a*x+b, iv.current, iv.voltage, p0=[iv.voltage[0]/iv.current[0], 0.0])
        return params[0]

class KeithleyIV(NamedTuple):
    current: np.ndarray
    voltage: np.ndarray
