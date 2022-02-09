import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from abc import ABC, abstractmethod

from DataCapsule.DataCapsules import RegularData3D, IrregularData3D, Data2D, SmoothFunction2D
from View.SILabel import SILabel, PlotUnits, PlotScales

class Plotter(ABC):
    roundDecimals = 2
    _fitcolors = ['red', 'green']

    def __init__(self, decorator):
        self.decorator = decorator
        self.markersize = decorator.markersize if decorator.markersize is not None else 5
        self.linewidth = decorator.linewidth if decorator.linewidth is not None else 2
        self.linestyle = decorator.linestyle if decorator.linestyle is not None else '-'
        self.fitcolor = self.decorator.fitcolor if self.decorator.fitcolor is not None else 'red'
        self.fitcolorindex = 0
        pass

    def _fitcolor(self):
        if self.fitcolorindex == len(self._fitcolors):
            self.fitcolorindex = 0
        color = self._fitcolors[self.fitcolorindex]
        self.fitcolorindex += 1
        return color

    @abstractmethod
    def plotDataCapsule(self, ax, dataCapsule):
        pass

    def decorate(self, ax):
        if plt.rcParams['text.usetex']:
            ax.set_xlabel(self.decorator.xlabel.generateLaTeXLabel())
            ax.set_ylabel(self.decorator.ylabel.generateLaTeXLabel())
            if self.decorator.zlabel != None:
                ax.set_title(self.decorator.zlabel.generateLaTeXLabel())
        else:
            labelpadx = self.decorator.labelPad[0] if self.decorator.labelPad is not None else 0
            labelpady = self.decorator.labelPad[1] if self.decorator.labelPad is not None else -2

            ax.set_xlabel(self.decorator.xlabel.generateTextLabel(), labelpad=labelpadx)
            ax.set_ylabel(self.decorator.ylabel.generateTextLabel(), labelpad=labelpady)
            if self.decorator.zlabel != None:
                ax.set_title(self.decorator.zlabel.generateTextLabel())

        if self.decorator.xlim is not None:
            ax.set_xlim(self.decorator.xlim)
        if self.decorator.ylim is not None:
            ax.set_ylim(self.decorator.ylim)

        ax.minorticks_on()

    def labelText(self, label):
        labelText = ""
        if label is not None:
            if label.labeltext is not None:
                labelText = label.labeltext
            elif label.labelfloat is not None:
                silabel = label.labelfloatSILabel if label.labelfloatSILabel is not None else self.decorator.ylabel
                if plt.rcParams['text.usetex']:
                    labelText = silabel.generateLaTeXUnit() + r" = " + str(round(label.labelfloat / silabel.scale, self.roundDecimals))
                    labelText += silabel.generateLaTeXSymbol()
                else:
                    labelText = silabel.generateLaTeXUnit() + r" = " + str(round(label.labelfloat / silabel.scale, self.roundDecimals))
                    labelText += silabel.generateTextSymbol()
        return labelText


class ColorPlotter(Plotter):
    def __init__(self, decorator):
        super().__init__(decorator)
        self.cmap = self.decorator.cmap if self.decorator.cmap is not None else 'turbo'

    def plotDataCapsule(self, ax, dataCapsule):
        if isinstance(dataCapsule, RegularData3D):
            self.plotRegularData3D(ax, dataCapsule)
        elif isinstance(dataCapsule, IrregularData3D):
            self.plotIrregularData3D(ax, dataCapsule)
        else:
            raise TypeError("Un-supported data capsule type for SQIPlotter.")

    def plotRegularData3D(self, ax, regularData3D):
        vmin = self.decorator.zlim[0] if self.decorator.zlim is not None else np.min(
            regularData3D.zz/self.decorator.zlabel.scale)
        vmax = self.decorator.zlim[1] if self.decorator.zlim is not None else np.max(
            regularData3D.zz / self.decorator.zlabel.scale)
        im = ax.pcolormesh(regularData3D.xx/self.decorator.xlabel.scale,
                           regularData3D.yy/self.decorator.ylabel.scale,
                           regularData3D.zz/self.decorator.zlabel.scale,
                      shading = 'nearest', cmap=self.cmap, vmin=vmin, vmax=vmax)
        plt.colorbar(im)

    def plotIrregularData3D(self, ax, irregularData3D):
        pass

class Scatter2D(Plotter):
    def __init__(self, decorator):
        super().__init__(decorator)

    def plotDataCapsule(self, ax, dataCapsule):
        label = dataCapsule.label

        if isinstance(dataCapsule, Data2D):
            ax.scatter(dataCapsule.x/self.decorator.xlabel.scale, dataCapsule.y/self.decorator.ylabel.scale, s=self.markersize, label=self.labelText(label))
            if (self.decorator.connectDots is None) or (self.decorator.connectDots == True):
                ax.plot(dataCapsule.x/self.decorator.xlabel.scale, dataCapsule.y/self.decorator.ylabel.scale, linewidth = self.linewidth, linestyle=self.linestyle)
        elif isinstance(dataCapsule, SmoothFunction2D):
            x0, x1 = ax.get_xlim()
            xax = np.linspace(x0, x1, dataCapsule.NPoints)

            ax.plot(xax, dataCapsule.func(xax*self.decorator.xlabel.scale)/self.decorator.ylabel.scale, linewidth = self.linewidth, linestyle='--', label=self.labelText(label), color=self._fitcolor())
        else:
            raise TypeError("Un-supported data capsule type for Scatter2D.")

    def decorate(self, ax):
        super().decorate(ax)
        if self.decorator.legendOn is None or self.decorator.legendOn == True:
            ax.legend(bbox_to_anchor=[1.05,1.05])
        ax.grid()