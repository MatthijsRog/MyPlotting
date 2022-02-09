from View.Plotter import Plotter, ColorPlotter, Scatter2D
from enum import Enum, auto
from typing import NamedTuple
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams, rcParamsDefault
from matplotlib import gridspec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

class PlotTypes(Enum):
    ColorPlot = auto()
    Scatter2D = auto()

class View():
    preferredAmountOfColumns = 2
    preferredFigureSize = (7, 4)
    preferredDpi = 240

    def __init__(self, useTex=False):
        self._subplots = []
        self._insets   = []

        if useTex:
            rc('font', **{'family': 'serif', 'serif': ['Times']})
            rc('text', usetex=True)
            rc('text.latex', preamble=r"\usepackage{siunitx}")
        else:
            rcParams.update(rcParamsDefault)

    def subplotFromDataCapsules(self, dataCapsules, plotType, decorator):
        # First force dataCapsules to be a list:
        dataCapsules = self._enforceList(dataCapsules)
        # Then add to a Subplot instance based on the plotType.
        subplot = self._subplotFromPlotType(dataCapsules, plotType, decorator)

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
            subplot = self._subplotFromPlotType(dataCapsules, plotType, decorator)
            self._insets[plotID].append(subplot)


    def plotAll(self, savepath=None):
        amountOfPlots = len(self._subplots)
        rows = amountOfPlots // self.preferredAmountOfColumns
        if amountOfPlots % self.preferredAmountOfColumns > 0:
            rows+=1
        if rows == 1:
            self.plotGrid = gridspec.GridSpec(rows, amountOfPlots)
        else:
            self.plotGrid = gridspec.GridSpec(rows, self.preferredAmountOfColumns)
        self.plotFigure = plt.figure(figsize=self.preferredFigureSize, dpi=self.preferredDpi)

        for i in range(amountOfPlots):
            ax = self.plotFigure.add_subplot(self.plotGrid[i])
            plotter = self._subplots[i].plotter

            # Plot all data:
            for dataCapsule in self._subplots[i].dataCapsules:
                plotter.plotDataCapsule(ax, dataCapsule)
            plotter.decorate(ax)

            # Goto smaller font:
            rcParams.update({'font.size': 6})

            insets = self._insets[i]
            if insets: # If not an empty list
                for inset in insets:
                    plotter = inset.plotter

                    loc = plotter.decorator.insetPositon if plotter.decorator.insetPositon is not None else 'lower right'
                    width = plotter.decorator.insetWidth if plotter.decorator.insetWidth is not None else 2.5
                    height = plotter.decorator.insetHeight if plotter.decorator.insetHeight is not None else 1
                    borderpad = plotter.decorator.insetBorderPad if plotter.decorator.insetBorderPad is not None else 5

                    inset_ax = inset_axes(ax, width=width, height=height, loc=loc, borderpad=borderpad)
                    for dataCapsule in inset.dataCapsules:
                        plotter.plotDataCapsule(inset_ax, dataCapsule)
                    plotter.decorate(inset_ax)

            # Return to standard font size:
            rcParams.update({'font.size': 10})

        plt.tight_layout()

        if savepath is not None:
            plt.savefig(savepath)

        plt.show()
        rcParams.update(rcParamsDefault)

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

    def _subplotFromPlotType(self, dataCapsules, plotType, decorator):
        if plotType == PlotTypes.ColorPlot:
            return Subplot(dataCapsules=dataCapsules, plotter=ColorPlotter(decorator))
        elif plotType == PlotTypes.Scatter2D:
            return Subplot(dataCapsules=dataCapsules, plotter=Scatter2D(decorator))
        else:
            raise TypeError("Unsupported plot type.")

class Subplot(NamedTuple):
    dataCapsules: list
    plotter: Plotter