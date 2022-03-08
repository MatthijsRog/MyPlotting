import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.ticker as ticker

import numpy as np

from abc import ABC, abstractmethod

from DataCapsule.DataCapsules import RegularData3D, IrregularData3D, Data2D, SmoothFunction2D

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

    def addColorbar(self, im, cax, ticks=None, toRemove=False):
        self.colorbar = plt.colorbar(im, cax=cax, ticks=ticks)

    @abstractmethod
    def plotDataCapsule(self, ax, dataCapsule, cax=None, bax=None):
        pass

    def decorate(self, ax, cax=None, bax=None, secondaryAxis=False):
        print("Bar!")
        labelpadx = self.decorator.labelPad[0] if self.decorator.labelPad is not None else 5
        labelpady = self.decorator.labelPad[1] if self.decorator.labelPad is not None else 3.5
        labelpadz = self.decorator.labelPadZ if self.decorator.labelPadZ is not None else 20

        if not secondaryAxis:
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

        if self.decorator.semilogy == True:
            ax.set_yscale('log')
        if self.decorator.xlim is not None:
            ax.set_xlim(self.decorator.xlim)
        if self.decorator.ylim is not None and self.decorator.brokenYLim is None:
            ax.set_ylim(self.decorator.ylim)
        if self.decorator.brokenYLim is not None:
            print("Snoot")
            if not secondaryAxis:
                ax.set_ylim(self.decorator.brokenYLim[1])
            else:
                print(self.decorator.brokenYLim[1])
                ax.set_ylim(self.decorator.brokenYLim[0])
        if self.decorator.minorticksOn is None or self.decorator.minorticksOn == True:
            print("Turning on minor ticks.")
            ax.minorticks_on()

        if self.decorator.majorTickSize is not None:
            ax.tick_params(which='major', width=self.decorator.majorTickSize[0], length=self.decorator.majorTickSize[1])
            for axis in ['top', 'bottom', 'left', 'right']:
                ax.spines[axis].set_linewidth(self.decorator.majorTickSize[0])  # change width
        if self.decorator.minorTickSize is not None:
            ax.tick_params(which='minor', width=self.decorator.minorTickSize[0], length=self.decorator.minorTickSize[1])

        self.setTickSpacingOnAxis(ax)

    def setTickSpacingOnAxis(self, ax):
        if self.decorator.tickspacing is not None:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(self.decorator.tickspacing[0]))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(self.decorator.tickspacing[1]))

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

    def plotDataCapsule(self, ax, dataCapsule, cax=None, bax=None):
        if isinstance(dataCapsule, RegularData3D):
            self.plotRegularData3D(ax, dataCapsule, cax, bax)
        elif isinstance(dataCapsule, IrregularData3D):
            self.plotIrregularData3D(ax, dataCapsule, cax, bax)
        else:
            raise TypeError("Un-supported data capsule type for SQIPlotter.")

    def plotRegularData3D(self, ax, regularData3D, cax, bax):
        vmin, vmax = self.getZrange(regularData3D)
        im = ax.pcolormesh(regularData3D.xx / self.decorator.xlabel.scale,
                           regularData3D.yy / self.decorator.ylabel.scale,
                           regularData3D.zz / self.decorator.title.scale,
                           shading = 'nearest', cmap=self.cmap, vmin=vmin, vmax=vmax)

        if bax is not None:
            print("Warning: currently broken axes for colorplots are not supported.")

        self.addColorbar(im, cax)

    def plotIrregularData3D(self, ax, irregularData3D, cax, bax):
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
        self.addColorbar(im, cax, ticks=np.linspace(vmin, vmax, 6))
        ax.contour(grid_x / self.decorator.xlabel.scale,
                   grid_y / self.decorator.ylabel.scale,
                   grid_z / self.decorator.zlabel.scale, linewidths=self.contourLinewidths, levels=levels,
                   colors='k', alpha=.4)

        if bax is not None:
            print("Warning: currently broken axes for colorplots are not supported.")

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

    def _plotData2DToAxis(self, ax, dataCapsule, color, toIm=True):
        label = dataCapsule.label

        if toIm:
            self.im = ax.scatter(dataCapsule.x / self.decorator.xlabel.scale,
                                 dataCapsule.y / self.decorator.ylabel.scale,
                                 s=self.markersize, color=color, label=self.labelText(label))
        else:
            ax.scatter(dataCapsule.x / self.decorator.xlabel.scale,
                       dataCapsule.y / self.decorator.ylabel.scale,
                       s=self.markersize, color=color, label=self.labelText(label))

        if (self.decorator.connectDots is None) or (self.decorator.connectDots == True):
            ax.plot(dataCapsule.x / self.decorator.xlabel.scale, dataCapsule.y / self.decorator.ylabel.scale,
                    linewidth=self.linewidth, linestyle=self.linestyle, color=color)

    def _plotSmoothFunction2DToAxis(self, ax, dataCapsule, toIm=True):
        label = dataCapsule.label

        x0, x1 = ax.get_xlim()
        xax = np.linspace(x0, x1, dataCapsule.NPoints)
        if toIm:
            self.im = ax.plot(xax,
                              dataCapsule.func(xax * self.decorator.xlabel.scale) / self.decorator.ylabel.scale,
                              linewidth=self.linewidth, linestyle='--', label=self.labelText(label),
                              color=self._fitcolor())
        else:
            ax.plot(xax,
                    dataCapsule.func(xax * self.decorator.xlabel.scale) / self.decorator.ylabel.scale,
                    linewidth=self.linewidth, linestyle='--', label=self.labelText(label),
                    color=self._fitcolor())

    def plotDataCapsule(self, ax, dataCapsule, cax=None, bax=None):
        if isinstance(dataCapsule, Data2D):
            color = self._linecolor()
            self._plotData2DToAxis(ax, dataCapsule, color, toIm=True)
            if bax is not None:
                self._plotData2DToAxis(bax, dataCapsule, color, toIm=False)


        elif isinstance(dataCapsule, SmoothFunction2D):
            self._plotSmoothFunction2DToAxis(ax, dataCapsule, toIm=True)
            if bax is not None:
                self._plotSmoothFunction2DToAxis(bax, dataCapsule, color, toIm=False)
        else:
            raise TypeError("Un-supported data capsule type for Scatter2D.")

        if cax is not None:
            print("Warning: currently colorbars for scatterplots are not supported.")

    def decorate(self, ax, cax=None, bax=None, baxpad=None):
        """Bax is the broken axis if using broken axes."""
        print("Foo!")
        super().decorate(ax)
        if bax is not None:
            print("Super decorating bax.")
            super().decorate(bax, secondaryAxis=True)

        if self.decorator.legendOn is None or self.decorator.legendOn == True:
            ax.legend(loc='upper left', bbox_to_anchor=[1.05,1])
        if self.decorator.gridOn is None or self.decorator.gridOn == True:
            ax.grid()
            if bax is not None:
                bax.grid()

        ax2 = ax.secondary_yaxis('right')
        ax3 = ax.secondary_xaxis('top')
        ax2.tick_params(which='major', axis="y", direction="in")
        ax2.tick_params(which='minor', axis="y", direction="in")
        ax2.tick_params(labelleft=False, labelright=False, labeltop=False, labelbottom=False)
        ax3.tick_params(which='major', axis="x", direction="in")
        ax3.tick_params(which='minor', axis="x", direction="in")
        ax3.tick_params(labelleft=False, labelright=False, labeltop=False, labelbottom=False)
        ax3.minorticks_on()

        if self.decorator.majorTickSize is not None:
            ax2.tick_params(which='major', width=self.decorator.majorTickSize[0], length=self.decorator.majorTickSize[1])
            ax3.tick_params(which='major', width=self.decorator.majorTickSize[0], length=self.decorator.majorTickSize[1])
        if self.decorator.minorTickSize is not None:
            ax2.tick_params(which='minor', width=self.decorator.minorTickSize[0], length=self.decorator.minorTickSize[1])
            ax3.tick_params(which='minor', width=self.decorator.minorTickSize[0], length=self.decorator.minorTickSize[1])

        self.setTickSpacingOnAxis(ax2)
        self.setTickSpacingOnAxis(ax3)

        if bax is not None:
            # Pull xlabel from ax to bax:
            xlabel = ax.get_xlabel()
            ax.set_xlabel(None)
            bax.set_xlabel(xlabel)

            bax2 = bax.secondary_yaxis('right')
            bax3 = bax.secondary_xaxis('top')
            bax2.tick_params(which='major', axis="y", direction="in")
            bax2.tick_params(which='minor', axis="y", direction="in")
            bax2.tick_params(labelleft=False, labelright=False, labeltop=False, labelbottom=False)
            bax3.tick_params(which='major', axis="x", direction="in")
            bax3.tick_params(which='minor', axis="x", direction="in")
            bax3.tick_params(labelleft=False, labelright=False, labeltop=False, labelbottom=False)
            bax3.minorticks_on()

            ax.spines['bottom'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)
            ax3.spines['bottom'].set_visible(False)
            ax.tick_params(which='major', bottom=False, labelbottom=False)
            ax.tick_params(which='minor', bottom=False, labelbottom=False)

            bax.spines['top'].set_visible(False)
            bax2.spines['top'].set_visible(False)
            bax3.spines['top'].set_visible(False)
            bax3.tick_params(which='major', top=False, labeltop=False)
            bax3.tick_params(which='minor', top=False, labeltop=False)

            if self.decorator.majorTickSize is not None:
                bax2.tick_params(which='major', width=self.decorator.majorTickSize[0],
                                length=self.decorator.majorTickSize[1])
                bax3.tick_params(which='major', width=self.decorator.majorTickSize[0],
                                length=self.decorator.majorTickSize[1])
            if self.decorator.minorTickSize is not None:
                bax2.tick_params(which='minor', width=self.decorator.minorTickSize[0],
                                length=self.decorator.minorTickSize[1])
                bax3.tick_params(which='minor', width=self.decorator.minorTickSize[0],
                                length=self.decorator.minorTickSize[1])

            # Mesh together the plots:
            d = .02
            kwargs = dict(transform=bax.transAxes, color='k', clip_on=False, linewidth=.8)
            bax.plot((-d, d), (-4 * d, 4 * d), **kwargs)  # top-left diagonal
            bax.plot((1 - d, 1 + d), (-4 * d, 4 * d), **kwargs)  # top-right diagonal

            kwargs.update(transform=ax.transAxes)  # switch to the bottom axes
            ax.plot((-d, +d), (1 - 4 * d, 1 + 4 * d), **kwargs)  # bottom-left diagonal
            ax.plot((1 - d, 1 + d), (1 - 4 * d, 1 + 4 * d), **kwargs)  # bottom-right diagonal

            self.setTickSpacingOnAxis(bax2)
            self.setTickSpacingOnAxis(bax3)

            # Set the ylabel to the correct position:
            bbox = ax.get_window_extent().transformed(plt.gcf().dpi_scale_trans.inverted())
            width, height = bbox.width, bbox.height
            labelpady = self.decorator.labelPad[1] if self.decorator.labelPad is not None else 3.5
            baxpad = self.decorator.baxpad if self.decorator.baxpad is not None else .5 # Needs bugfix
            ax.yaxis.set_label_coords(-labelpady/width/72, 1.0 + .5*baxpad, transform=ax.transAxes) # 72: ppi for matplotlib

        if self.decorator.semilogy is None or self.decorator.semilogy == False:
            ax2.minorticks_on()

            if bax is not None:
                bax2.minorticks_on()




