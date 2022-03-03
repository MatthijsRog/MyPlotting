import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from abc import ABC, abstractmethod

from DataCapsule.DataCapsules import RegularData3D, IrregularData3D, Data2D, SmoothFunction2D
from View.SILabel import SILabel, PlotUnits, PlotScales

from scipy.interpolate import griddata

class Plotter(ABC):
    roundDecimals = 2
    _defaultFitcolors = ['red', 'green']
    _defaultLinecolors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']

    def __init__(self, decorator):
        self.decorator = decorator
        self.markersize = decorator.markersize if decorator.markersize is not None else 5
        self.linewidth = decorator.linewidth if decorator.linewidth is not None else 2
        self.linestyle = decorator.linestyle if decorator.linestyle is not None else '-'
        self.linecolors = self.decorator.linecolors if self.decorator.linecolors is not None else self._defaultLinecolors
        self.fitcolors = self.decorator.fitcolors if self.decorator.fitcolors is not None else self._defaultFitcolors
        self.linecolorindex = 0
        self.fitcolorindex = 0
        pass

    def _linecolor(self):
        if self.linecolorindex == len(self.linecolors):
            self.linecolorindex = 0
        color = self.linecolors[self.linecolorindex]
        self.linecolorindex += 1
        return color

    def _fitcolor(self):
        if self.fitcolorindex == len(self.fitcolors):
            self.fitcolorindex = 0
        color = self.fitcolors[self.fitcolorindex]
        self.fitcolorindex += 1
        return color

    @abstractmethod
    def plotDataCapsule(self, ax, dataCapsule):
        pass

    def decorate(self, ax):
        labelpadx = self.decorator.labelPad[0] if self.decorator.labelPad is not None else 5
        labelpady = self.decorator.labelPad[1] if self.decorator.labelPad is not None else 3.5
        labelpadz = self.decorator.labelPadZ if self.decorator.labelPadZ is not None else 20

        if plt.rcParams['text.usetex']:
            ax.set_xlabel(self.decorator.xlabel.generateLaTeXLabel(), labelpad=labelpadx)
            ax.set_ylabel(self.decorator.ylabel.generateLaTeXLabel(), labelpad=labelpady)
            if self.decorator.title is not None:
                ax.set_title(self.decorator.title.generateLaTeXLabel())
            if self.decorator.zlabel is not None:
                self.colorbar.ax.set_title(self.decorator.zlabel.generateLaTeXLabel(), pad=labelpadz)
        else:
            ax.set_xlabel(self.decorator.xlabel.generateTextLabel(), labelpad=labelpadx)
            ax.set_ylabel(self.decorator.ylabel.generateTextLabel(), labelpad=labelpady)
            if self.decorator.title != None:
                ax.set_title(self.decorator.title.generateTextLabel())
            if self.decorator.zlabel is not None:
                self.colorbar.ax.set_title(self.decorator.zlabel.generateTextLabel(), pad=labelpadz)

        if self.decorator.xlim is not None:
            ax.set_xlim(self.decorator.xlim)
        if self.decorator.ylim is not None:
            ax.set_ylim(self.decorator.ylim)
        if self.decorator.minorticksOn is not None or self.decorator.minorticksOn == True:
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
                    labelText = silabel.generateTextUnit() + r" = " + str(round(label.labelfloat / silabel.scale, self.roundDecimals))
                    labelText += silabel.generateTextSymbol()
        return labelText


class ColorPlotter(Plotter):
    def __init__(self, decorator):
        super().__init__(decorator)
        self.cmap = self.decorator.cmap if self.decorator.cmap is not None else 'turbo'
        self.contourFillLevels = self.decorator.contourFillLevels if self.decorator.contourFillLevels is not None else 40
        self.contourLevels = self.decorator.contourLevels if self.decorator.contourLevels is not None else 6
        self.contourLinewidths = .4 # Magic number

    def plotDataCapsule(self, ax, dataCapsule):
        if isinstance(dataCapsule, RegularData3D):
            self.plotRegularData3D(ax, dataCapsule)
        elif isinstance(dataCapsule, IrregularData3D):
            self.plotIrregularData3D(ax, dataCapsule)
        else:
            raise TypeError("Un-supported data capsule type for SQIPlotter.")

    def plotRegularData3D(self, ax, regularData3D):
        vmin, vmax = self.getZrange(regularData3D)
        im = ax.pcolormesh(regularData3D.xx / self.decorator.xlabel.scale,
                           regularData3D.yy / self.decorator.ylabel.scale,
                           regularData3D.zz / self.decorator.title.scale,
                           shading = 'nearest', cmap=self.cmap, vmin=vmin, vmax=vmax)
        self.colorbar = plt.colorbar(im)

    def plotIrregularData3D(self, ax, irregularData3D):
        vmin, vmax = self.getZrange(irregularData3D)
        xlist = np.concatenate([np.repeat(irregularData3D.x[i], len(irregularData3D.ylist[i])) for i in range(len(irregularData3D.x))], axis=0)
        ylist = np.concatenate(irregularData3D.ylist, axis=0)
        zlist = np.concatenate(irregularData3D.zlist, axis=0)

        xax = np.linspace(np.min(xlist), np.max(xlist), 100)
        yax = np.linspace(np.min(ylist), np.max(ylist), 100)
        grid_x, grid_y = np.meshgrid(xax, yax)
        grid_z = griddata((xlist, ylist), zlist, (grid_x, grid_y), method='cubic')

        levelsf = np.linspace(vmin, vmax, self.contourFillLevels+2, endpoint=False)[1:]
        levels = np.linspace(vmin, vmax, self.contourLevels+2, endpoint=False)[1:]

        im = ax.contourf(grid_x / self.decorator.xlabel.scale,
                         grid_y / self.decorator.ylabel.scale,
                         grid_z / self.decorator.zlabel.scale, levels=levelsf, cmap=self.cmap,
                         extend='both')
        self.colorbar = plt.colorbar(im, ticks=np.linspace(vmin, vmax, 6))
        ax.contour(grid_x / self.decorator.xlabel.scale,
                   grid_y / self.decorator.ylabel.scale,
                   grid_z / self.decorator.zlabel.scale, linewidths=self.contourLinewidths, levels=levels,
                   colors='k', alpha=.4)

    def getZrange(self, data3D):
        if isinstance(data3D, RegularData3D):
            datamin = np.min(data3D.zz)
            datamax = np.max(data3D.zz)

        elif isinstance(data3D, IrregularData3D):
            datamin = np.min([np.min(data3D.zlist[i]) for i in range(len(data3D.zlist))])
            datamax = np.max([np.max(data3D.zlist[i]) for i in range(len(data3D.zlist))])
        else:
            raise TypeError("Dataset type not recognized.")

        vmin = self.decorator.zlim[0] if self.decorator.zlim is not None else datamin / self.decorator.zlabel.scale
        vmax = self.decorator.zlim[1] if self.decorator.zlim is not None else datamax / self.decorator.zlabel.scale
        return vmin, vmax

class Scatter2D(Plotter):
    def __init__(self, decorator):
        super().__init__(decorator)

    def plotDataCapsule(self, ax, dataCapsule):
        label = dataCapsule.label

        if isinstance(dataCapsule, Data2D):
            color = self._linecolor()
            ax.scatter(dataCapsule.x/self.decorator.xlabel.scale, dataCapsule.y/self.decorator.ylabel.scale,
                       s=self.markersize, color=color, label=self.labelText(label))
            if (self.decorator.connectDots is None) or (self.decorator.connectDots == True):
                ax.plot(dataCapsule.x/self.decorator.xlabel.scale, dataCapsule.y/self.decorator.ylabel.scale, linewidth = self.linewidth, linestyle=self.linestyle, color=color)
        elif isinstance(dataCapsule, SmoothFunction2D):
            x0, x1 = ax.get_xlim()
            xax = np.linspace(x0, x1, dataCapsule.NPoints)

            ax.plot(xax, dataCapsule.func(xax*self.decorator.xlabel.scale)/self.decorator.ylabel.scale, linewidth = self.linewidth, linestyle='--', label=self.labelText(label), color=self._fitcolor())
        else:
            raise TypeError("Un-supported data capsule type for Scatter2D.")

    def decorate(self, ax):
        print("Foo!")
        super().decorate(ax)
        if self.decorator.legendOn is None or self.decorator.legendOn == True:
            ax.legend(loc='upper left', bbox_to_anchor=[1.05,1])
        if self.decorator.gridOn is None or self.decorator.gridOn == True:
            ax.grid()