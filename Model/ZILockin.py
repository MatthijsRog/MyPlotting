from Model.Model import VectorMagnetModel
from Model.SingleMeasurement import SingleMeasurement
from DataCapsule.DataCapsules import Data2D
import numpy as np

class ZILockin(VectorMagnetModel):
    def __init__(self, paths):
        super().__init__(paths)

    def loadDataFromFile(self, path):
        VTITemperature, sampleTemperature, Bx, By, Bz = self.vectorMagnetTemperatureAndField(path)
        R, Phi = self.loadLockinData(path)
        singleMeasurementFirstIndices = self.singleMeasurementFirstIndices([VTITemperature, sampleTemperature, Bx, By, Bz])

        for i, start in enumerate(singleMeasurementFirstIndices):
            if i < len(singleMeasurementFirstIndices) - 1:
                end = singleMeasurementFirstIndices[i+1]
            else:
                end = len(VTITemperature)

            r = R[start:end]
            phi = Phi[start:end]
            self._data.append(ZILockinData(VTITemperature[start],
                                      sampleTemperature[start],
                                      Bx[start],
                                      By[start],
                                      Bz[start],
                                      r,
                                      phi))

    def loadLockinData(self, path):
        rPerDevice, phiPerDevice = self.load2DDataForVectorMagnet(path, "R", "Phi")
        return rPerDevice[0], phiPerDevice[0]

    def sweepR(self, sweepType, deviceID=0):
        """Returns (x,R,Rstd) data for some environmental variable x."""
        x = np.zeros(len(self._data))
        y = np.zeros_like(x)
        yerr = np.zeros_like(y)

        for i, data in enumerate(self._data):
            x[i] = data.environmental(sweepType)
            y[i] = np.mean(data.R)
            yerr[i] = np.std(data.R)

        return Data2D(x,y)


class ZILockinData(SingleMeasurement):
    def __init__(self, VTITemperature, sampleTemperature, Bx, By, Bz, R, phi):
        self.VTITemperature = float(VTITemperature)
        self.sampleTemperature = float(sampleTemperature)
        self.Bx = float(Bx)
        self.By = float(By)
        self.Bz = float(Bz)
        self.R = R
        self.phi = phi