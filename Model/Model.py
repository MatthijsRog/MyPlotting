import numpy as np
import warnings
from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self, paths):
        self._data = []
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

    @abstractmethod
    def loadDataFromFile(self, path):
        # Loads data from a single file
        pass

    def columnTitles(self, path):
        with open(path) as f:
            header = f.readline().rstrip()
            f.close()
        columnTitles = header.split()

        return columnTitles

    def singleMeasurementFirstIndices(self, listOfArrays):
        singleMeasurementFirstIndices = [0]

        for i in range(1, len(listOfArrays[0])):
            for array in listOfArrays:
                if array[i] != array[i-1]:
                    singleMeasurementFirstIndices.append(i)
                    break

        return singleMeasurementFirstIndices

    def derivative(self, x, y):
        dydx = np.zeros_like(y)

        for i in range(1,len(x)-1):
            dydx[i] = (y[i+1]-y[i-1])/(x[i+1]-x[i-1])
        dydx[0]  = (-1.5*y[0]  + 2*y[1]  - .5*y[2])/(x[i+1]-x[i])
        dydx[-1] = ( 1.5*y[-1] - 2*y[-2] +.5*y[-3])/(x[-1]-x[-2])

        return dydx


class VectorMagnetModel(Model):
    def genColumnsFromTxtForVectorMagnet(self, path, columnList):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="ConversionWarning: Some errors were detected !")
            returnValues = np.genfromtxt(path, skip_header=1, usecols=columnList, invalid_raise=False, unpack=False)
        return returnValues.T

    def vectorMagnetTemperatureAndField(self, path):
        columnTitles = self.columnTitles(path)

        VTITemperatureIndex = columnTitles.index("T(K)[VTI]")
        sampleTemperatureIndex = columnTitles.index("T(K)[Sample]")
        BxIndex = columnTitles.index("Bx(T)")
        ByIndex = columnTitles.index("By(T)")
        BzIndex = columnTitles.index("Bz(T)")

        VTITemperature, sampleTemperature, Bx, By, Bz = self.genColumnsFromTxtForVectorMagnet(path, [VTITemperatureIndex,
                                                                                                     sampleTemperatureIndex,
                                                                                                     BxIndex,
                                                                                                     ByIndex,
                                                                                                     BzIndex])
        return VTITemperature, sampleTemperature, Bx, By, Bz

    def load2DDataForVectorMagnet(self, path, xIdentifier, yIdentifier):
        columnTitles = self.columnTitles(path)

        # The Keithley data sets come with I, V data that we want for every device:
        xIndices = []
        yIndices = []

        for i, title in enumerate(columnTitles):
            if title[:len(xIdentifier)+1] == xIdentifier + "(":
                xIndices.append(i)
            if title[:len(yIdentifier)+1] == yIdentifier + "(":
                yIndices.append(i)

        xPerDevice = []
        yPerDevice = []
        for i, xIndex in enumerate(xIndices):
            yIndex = yIndices[i]

            x, y = self.genColumnsFromTxtForVectorMagnet(path, [xIndex, yIndex])
            xPerDevice.append(x)
            yPerDevice.append(y)

        return xPerDevice, yPerDevice

    def load3DDataForVectorMagnet(self, path, xIdentifier, yIdentifier, zIdentifier):
        columnTitles = self.columnTitles(path)

        # The Keithley data sets come with I, V data that we want for every device:
        xIndices = []
        yIndices = []
        zIndices = []

        for i, title in enumerate(columnTitles):
            if title[:len(xIdentifier) + 1] == xIdentifier + "(":
                xIndices.append(i)
            if title[:len(yIdentifier) + 1] == yIdentifier + "(":
                yIndices.append(i)
            if title[:len(zIdentifier) + 1] == zIdentifier + "(":
                zIndices.append(i)

        xPerDevice = []
        yPerDevice = []
        zPerDevice = []

        for xIndex, yIndex, zIndex in zip(xIndices, yIndices, zIndices):
            x, y, z = self.genColumnsFromTxtForVectorMagnet(path, [xIndex, yIndex, zIndex])
            xPerDevice.append(x)
            yPerDevice.append(y)
            zPerDevice.append(z)

        return xPerDevice, yPerDevice, zPerDevice

