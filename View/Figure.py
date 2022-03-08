from typing import NamedTuple
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

class Figure():
    def __init__(self, nrows, ncols, dpi, figsize, sharex, sharey, bax, colorplot,
                 colorbarwidth=.05, figurepadding=0.2):
        """Sharex: list of tuples of linked positions.
           Sharey: list of tuples of linked positions.
           Bax: list of positions with broken axes
           Colorplot: list of positions with colorplots"""
        self.figure = plt.figure(figsize=figsize, dpi=dpi)
        width_ratios, height_ratios = self._generateWidthHeightRatios(nrows, ncols, colorbarwidth, figurepadding)
        print(width_ratios, height_ratios)

        self.grid = GridSpec(nrows * 3 - 1, ncols * 3 - 1, figure=self.figure, width_ratios=width_ratios,
                             height_ratios=height_ratios)

        self._fillGrid(nrows, ncols, sharex, sharey, bax, colorplot)

    def _fillGrid(self, nrows, ncols, sharex, sharey, bax, colorplot):
        self.axes = []
        for row in range(nrows):
            self.axes.append([])
            for col in range(ncols):
                sharexloc = self._isShareAx(row, col, sharex)
                shareyloc = self._isShareAx(row, col, sharey)
                futuresharexloc = self._isShareAxFuture(row, col, sharex)

                isBax = False
                if bax is not None:
                    isBax = True if [row, col] in bax else False

                isColorplot = False
                futureShareXByColorplot = False
                if colorplot is not None:
                    isColorplot = True if [row, col] in colorplot else False
                    futureShareXByColorplot = True if futuresharexloc in colorplot else False

                self.axes[row].append(self._generateAxesCollection(row, col, sharexloc, shareyloc, isBax,
                                                                   isColorplot, futureShareXByColorplot))

    def _generateAxesCollection(self, row, col, sharexloc, shareyloc, isBax, isColorplot, futureShareXByColorplot):
        startY = row * 3
        startX = col * 3

        xLinkedToColorplot = False
        if sharexloc is not None:
            if self.axes[sharexloc[0]][sharexloc[1]].colorAx is not None:
                xLinkedToColorplot = True
        if isColorplot or xLinkedToColorplot or futureShareXByColorplot:
            stopX = startX + 1
        else:
            stopX = startX + 2

        if isBax:
            stopY = startY + 1
        else:
            stopY = startY + 2

        if sharexloc is not None:
            majorAx = self.figure.add_subplot(self.grid[startY:stopY, startX:stopX],
                                              sharex=self.axes[sharexloc[0]][sharexloc[1]].majorAx)
        elif shareyloc is not None:
            majorAx = self.figure.add_subplot(self.grid[startY:stopY, startX:stopX],
                                              sharex=self.axes[shareyloc[0]][shareyloc[1]].majorAx)
        else:
            majorAx = self.figure.add_subplot(self.grid[startY:stopY, startX:stopX])

        if isBax:
            brokenAx = self.figure.add_subplot(self.grid[stopY:stopY + 1, startX:stopX], sharex=majorAx)
        else:
            brokenAx = None

        if isColorplot:
            colorAx = self.figure.add_subplot(self.grid[startY:stopY, stopX:stopX + 1])
        else:
            colorAx = None

        return AxesCollection(majorAx=majorAx, brokenAx=brokenAx, colorAx=colorAx)

    def _generateWidthHeightRatios(self, nrows, ncols, colorbarwidth, figurepadding):
        width_ratios = np.zeros(ncols * 3 - 1)
        width_ratios[0::3] = 1.0
        width_ratios[1::3] = colorbarwidth
        width_ratios[2::3] = figurepadding

        height_ratios = np.zeros(nrows * 3 - 1)
        height_ratios[0::3] = 1.0
        height_ratios[1::3] = 1.0
        height_ratios[2::3] = figurepadding

        return width_ratios, height_ratios

    def _isShareAx(self, row, col, sharedTuples):
        for tup in sharedTuples:
            if [row, col] == tup[0]:
                return tup[1]
        return None

    def _isShareAxFuture(self, row, col, sharedTuples):
        for tup in sharedTuples:
            print(tup[1], [row, col])
            if [row, col] == tup[1]:
                return tup[0]
        return None


class AxesCollection(NamedTuple):
    majorAx: plt.Axes
    brokenAx: plt.Axes
    colorAx: plt.Axes