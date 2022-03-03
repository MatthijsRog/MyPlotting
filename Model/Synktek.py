from Model.Model import VectorMagnetModel
from Model.TransportMeasurement import TransportMeasurement
from Model.SingleMeasurement import SingleMeasurement
from DataCapsule.DataCapsules import RegularData3D, IrregularData3D, Data2D
from typing import NamedTuple
import numpy as np
from scipy.optimize import curve_fit

class Synktek(VectorMagnetModel, TransportMeasurement):
    def __init__(self, paths, invertVoltage=False):
        self.invertVoltage = invertVoltage
        super().__init__(paths)

    def loadDataFromFile(self, path):
        VTITemperature, sampleTemperature, Bx, By, Bz = self.vectorMagnetTemperatureAndField(path)
        currentPerDevice, voltagePerDevice, dvdiPerDevice = self.loadCurrentAndVoltagePerDevice(path)
        singleMeasurementFirstIndices = self.singleMeasurementFirstIndices([VTITemperature, sampleTemperature, Bx, By, Bz])

        for i, start in enumerate(singleMeasurementFirstIndices):
            if i < len(singleMeasurementFirstIndices) - 1:
                end = singleMeasurementFirstIndices[i+1]
            else:
                end = len(VTITemperature)

            ivPerDevice = []
            for deviceID in range(len(currentPerDevice)):
                current, voltage, dVdI = self.fixOrigin(currentPerDevice[deviceID][start:end],
                                                        voltagePerDevice[deviceID][start:end],
                                                        dvdiPerDevice[deviceID][start:end])
                iv = SynktekIV(current = current,
                               voltage = voltage,
                               dVdI = dVdI)
                ivPerDevice.append(iv)
            self._data.append(SynktekData(VTITemperature[start],
                                      sampleTemperature[start],
                                      Bx[start],
                                      By[start],
                                      Bz[start],
                                      ivPerDevice))

    def fixOrigin(self, current, voltage, dvdi):
        argmin = np.argmin(np.abs(current))
        voltage = voltage - voltage[argmin] # Enforce I = 0 -> V = 0
        if self.invertVoltage:
            voltage = -1*voltage
        return current, voltage, dvdi



    def loadCurrentAndVoltagePerDevice(self, path):
        return self.load3DDataForVectorMagnet(path, "I_DC", "DC", "dV/dI")

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
        x = np.zeros(len(self._data))
        I = []
        dVdI = []

        for i, data in enumerate(self._data):
            x[i] = data.environmental(sweepType)
            I.append(data.IVPerDevice[deviceID].current)
            dVdI.append(data.IVPerDevice[deviceID].dVdI)

        capsule = IrregularData3D(x, I, dVdI)

        return capsule

    def removeSeriesResistance(self, deviceID=0, Npoints=4):
        smallestResistance = np.inf

        for ivdata in self._data:
            current = ivdata.IVPerDevice[deviceID].current
            dvdi = ivdata.IVPerDevice[deviceID].dVdI
            centerIndex = np.argmin(np.abs(current))
            smallestResistance = np.min(dvdi[centerIndex-Npoints:centerIndex+Npoints])

        if smallestResistance > 0:
            print("Subtracting residual resistance of", round(smallestResistance*1e3), "mOhms")

            for i, ivdata in enumerate(self._data):
                newIV = KeithleyIV(current=ivdata.IVPerDevice[deviceID].current,
                                   voltage=ivdata.IVPerDevice[deviceID].voltage - ivdata.IVPerDevice[deviceID].current*smallestResistance,
                                   dVdI=ivdata.IVPerDevice[deviceID].dVdI - smallestResistance)
                self._data[i].IVPerDevice[deviceID] = newIV
        else:
            print("Smallest resistance was non-positive, not modifying dataset.")



class SynktekData(SingleMeasurement):
    def __init__(self, VTITemperature, sampleTemperature, Bx, By, Bz, IVPerDevice):
        self.VTITemperature = float(VTITemperature)
        self.sampleTemperature = float(sampleTemperature)
        self.Bx = float(Bx)
        self.By = float(By)
        self.Bz = float(Bz)

        if isinstance(IVPerDevice, list):
            self.IVPerDevice = IVPerDevice
        else:
            raise TypeError("IVPerDevice member of SynktekIV must be a list of device indices pointing to IV curves.")

    def resistance(self, deviceID=0):
        iv = self.IVPerDevice[deviceID]
        params, _ = curve_fit(lambda x, a, b: a*x+b, iv.current, iv.voltage, p0=[iv.voltage[0]/iv.current[0], 0.0])
        return params[0]

class SynktekIV(NamedTuple):
    current: np.ndarray
    voltage: np.ndarray
    dVdI: np.ndarray
