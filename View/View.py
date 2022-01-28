from View.Plotter import Plotter, ColorPlotter, Scatter2D
from enum import Enum, auto
from typing import NamedTuple
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams, rcParamsDefault
from matplotlib import gridspec

class PlotTypes(Enum):
    ColorPlot = auto()
    Scatter2D = auto()

class View():
    preferredAmountOfColumns = 2
    preferredFigureSize = (7, 4)
    preferredDpi = 240

    def __init__(self, useTex=False):
        self._subplots = []

        if useTex:
            rc('font', **{'family': 'serif', 'serif': ['Times']})
            rc('text', usetex=True)
            rc('text.latex', preamble=r"\usepackage{siunitx}")
        else:
            rcParams.update(rcParamsDefault)

    def subplotFromDataCapsules(self, dataCapsules, plotType, decorator):
        # First force dataCapsules to be a list:
        if not isinstance(dataCapsules, list):
            assert isinstance(dataCapsules, object)
            dataCapsules = [dataCapsules]

        # Then add to a Subplot instance based on the plotType.
        if plotType == PlotTypes.ColorPlot:
            subplot = Subplot(dataCapsules=dataCapsules, plotter=ColorPlotter(decorator))
            self._subplots.append(subplot)
            plotID = len(self._subplots) - 1
        elif plotType == PlotTypes.Scatter2D:
            subplot = Subplot(dataCapsules=dataCapsules, plotter=Scatter2D(decorator))
            self._subplots.append(subplot)
            plotID = len(self._subplots) - 1
        else:
            raise TypeError("Unsupported plot type.")
        return plotID

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

        plt.tight_layout()

        if savepath is not None:
            plt.savefig(savepath)

        plt.show()
        rcParams.update(rcParamsDefault)

    def addDatacapsuleToSubplot(self, dataCapsule, subplotID):
        self._subplots[subplotID].dataCapsules.append(dataCapsule)

    def dataCapsule(self, subplotID, dataCapsuleID):
        return self._subplots[subplotID].dataCapsules[dataCapsuleID]

    def decoratorFromSubplot(self, subplotID):
        return self._subplots[subplotID].plotter.decorator

    def isTeX(self):
        return plt.rcParams['text.usetex']

class Subplot(NamedTuple):
    dataCapsules: list
    plotter: Plotter