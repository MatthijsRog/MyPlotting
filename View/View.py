from View.Plotter import Plotter, ColorPlotter, Scatter2D
from enum import Enum, auto
from typing import NamedTuple
import Module.Defaults as Defaults

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rc, rcParams, rcParamsDefault
from View.Figure import Figure
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, InsetPosition

from enum import Enum, auto

class PlotTypes(Enum):
    ColorPlot = auto()
    Scatter2D = auto()

class View():
    preferredAmountOfColumns = 1
    preferredFigureSize = (8.25, 4)
    preferredDpi = 600
    preferredBaxpad = .5

    def __init__(self, useTex=False):
        self._subplots = []
        self._insets   = []
        self._axes = []

        if useTex:
            rc('font', **{'family': 'serif', 'serif': ['Times']})
            rc('text', usetex=True)
            rc('text.latex', preamble=r"""\usepackage{siunitx}
                                          \usepackage{textgreek}""")

            params = {'axes.labelsize': 'xx-large', 'axes.titlesize': 'x-large', 'xtick.labelsize': 'x-large',
                      'ytick.labelsize': 'x-large', 'legend.fontsize': 'xx-large'}
            matplotlib.rcParams.update(params)
        else:
            rcParams.update(rcParamsDefault)

    def subplotFromDataCapsules(self, dataCapsules, plotType, decorator, sharex=None, sharey=None):
        # First force dataCapsules to be a list:
        dataCapsules = self._enforceList(dataCapsules)
        # Then add to a Subplot instance based on the plotType.
        subplot = self._subplotFromPlotType(dataCapsules, plotType, decorator, sharex, sharey)

        # Then add to the right lists:
        self._subplots.append(subplot)
        self._insets.append([])
        plotID = len(self._subplots) - 1
        return plotID

    def insetFromDataCapsules(self, dataCapsules, plotType, decorator, plotID, insetID):
        # First force dataCapsules to be a list:
        dataCapsules = self._enforceList(dataCapsules)

        # If inset already exists, add there:
        if insetID < len(self._insets[plotID]):
            for dataCapsule in dataCapsules:
                self.addDatacapsuleToInset(dataCapsule, plotID, insetID)
        else:
            # Then add to a Subplot instance based on the plotType.
            subplot = self._subplotFromPlotType(dataCapsules, plotType, decorator, None, None)
            self._insets[plotID].append(subplot)

    def makeAxes(self):
        nrows, ncols = self.countRowsAndColumns(View.preferredAmountOfColumns)
        dpi = View.preferredDpi
        figsize = View.preferredFigureSize

        sharex = self._generateSharexList(ncols)
        sharey = self._generateShareyList(ncols)
        bax = self._generateBaxList(ncols)
        colorplot = self._generateColorplotList(ncols)

        print("Making a new set of axes using parameters:")
        print(nrows, ncols, dpi, figsize, sharex, sharey, bax, colorplot)

        self.figure = Figure(nrows, ncols, dpi, figsize, sharex, sharey, bax, colorplot)

        return nrows, ncols

    def plotIDToTuple(self, plotID, rowLength):
        return [plotID // rowLength, plotID % rowLength]

    def _generateSharexList(self, ncols):
        sharex = []

        for subplotID, subplot in enumerate(self._subplots):
            shareID = subplot.sharex
            if shareID is not None:
                sharex.append([self.plotIDToTuple(subplotID, ncols), self.plotIDToTuple(shareID, ncols)])

        return sharex

    def _generateShareyList(self, ncols):
        sharey = []

        for subplotID, subplot in enumerate(self._subplots):
            shareID = subplot.sharey
            if shareID is not None:
                sharey.append([self.plotIDToTuple(subplotID, ncols), self.plotIDToTuple(shareID, ncols)])

        return sharey

    def _generateBaxList(self, ncols):
        bax = []

        for subplotID, subplot in enumerate(self._subplots):
            decorator = subplot.plotter.decorator
            if decorator.brokenYLim is not None:
                bax.append(self.plotIDToTuple(subplotID, ncols))

        return bax

    def _generateColorplotList(self, ncols):
        colorplot = []

        for subplotID, subplot in enumerate(self._subplots):
            if isinstance(subplot.plotter, ColorPlotter):
                colorplot.append(self.plotIDToTuple(subplotID, ncols))

        return colorplot

    def countRowsAndColumns(self, ncols):
        amountOfPlots = len(self._subplots)
        rows = amountOfPlots // self.preferredAmountOfColumns
        if amountOfPlots % self.preferredAmountOfColumns > 0:
            rows += 1
        if rows == 1:
            columns = amountOfPlots
        else:
            columns = self.preferredAmountOfColumns

        return rows, columns

    def plotAll(self, savepath=None):
        nrows, ncols = self.makeAxes()

        for plotID, subplot in enumerate(self._subplots):
            print("Plotting subplot", plotID)
            plotter = subplot.plotter

            # Collect the proper axes:
            row, col = self.plotIDToTuple(plotID, ncols)
            axesCollection = self.figure.axes[row][col]

            # Plot all data:
            for dataCapsule in subplot.dataCapsules:
                plotter.plotDataCapsule(axesCollection.majorAx, dataCapsule, bax=axesCollection.brokenAx,
                                        cax=axesCollection.colorAx)
                plotter.decorate(axesCollection.majorAx, bax=axesCollection.brokenAx, cax=axesCollection.colorAx)

            self.handleInsets(self._insets[plotID], axesCollection.majorAx)

        if savepath is not None:
            plt.savefig(savepath, bbox_inches='tight')

        plt.show()
        rcParams.update(rcParamsDefault)

    def handleInsets(self, insets, parentAx):
        rcParams.update({'font.size': 6})
        if insets:  # If not an empty list
            for inset in insets:
                plotter = inset.plotter

                loc = plotter.decorator.insetPositon if plotter.decorator.insetPositon is not None else Defaults.insetPosition
                width = plotter.decorator.insetWidth if plotter.decorator.insetWidth is not None else Defaults.insetWidth
                height = plotter.decorator.insetHeight if plotter.decorator.insetHeight is not None else Defaults.insetHeight
                borderpad = plotter.decorator.insetBorderPad if plotter.decorator.insetBorderPad is not None else Defaults.insetBorderPad

                if isinstance(loc, str) or isinstance(loc, int):
                    inset_ax = inset_axes(parentAx, width=width, height=height, loc=loc,
                                          borderpad=borderpad)
                else:
                    inset_ax = plt.axes([0, 0, 1, 1])
                    insetPosition = InsetPosition(parentAx, loc)
                    inset_ax.set_axes_locator(insetPosition)

                for dataCapsule in inset.dataCapsules:
                    plotter.plotDataCapsule(inset_ax, dataCapsule)
                plotter.decorate(inset_ax)

        # Return to standard font size:
        rcParams.update({'font.size': 10})

    def addDatacapsuleToSubplot(self, dataCapsule, subplotID):
        self._subplots[subplotID].dataCapsules.append(dataCapsule)

    def addDatacapsuleToInset(self, dataCapsule, subplotID, insetID):
        self._insets[subplotID][insetID].dataCapsules.append(dataCapsule)

    def dataCapsule(self, subplotID, dataCapsuleID):
        return self._subplots[subplotID].dataCapsules[dataCapsuleID]

    def decoratorFromSubplot(self, subplotID):
        return self._subplots[subplotID].plotter.decorator

    def isTeX(self):
        return plt.rcParams['text.usetex']

    def _enforceList(self, data):
        if not isinstance(data, list):
            assert isinstance(data, object)
            data = [data]
        return data

    def _subplotFromPlotType(self, dataCapsules, plotType, decorator, sharex, sharey):
        if plotType == PlotTypes.ColorPlot:
            return Subplot(dataCapsules=dataCapsules, plotter=ColorPlotter(decorator), sharex=sharex, sharey=sharey)
        elif plotType == PlotTypes.Scatter2D:
            return Subplot(dataCapsules=dataCapsules, plotter=Scatter2D(decorator), sharex=sharex, sharey=sharey)
        else:
            raise TypeError("Unsupported plot type.")

class Subplot(NamedTuple):
    dataCapsules: list
    plotter: Plotter
    sharex: int # PlotID of other subplot with which x-axis is shared. None if not implemented
    sharey: int # PlotID of other subplot with which y-axis is shared. None if not implemented