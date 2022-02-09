from typing import NamedTuple
from View.SILabel import PlotUnits, PlotScales, SILabel
from enum import Enum

class Decorator(object):
    def __init__(self, xlabel=None, ylabel=None, zlabel=None, xlim=None, ylim=None, zlim=None, markersize=None,
                 linestyle=None, linewidth=None, cmap=None, connectDots=None, fitcolor=None, insetPosition=None,
                 insetWidth=None, insetHeight=None, insetBorderPad=None, legendOn=None, labelPad = None):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.zlabel = zlabel
        self.xlim = xlim # 2-element list
        self.ylim = ylim # 2-element list
        self.zlim = zlim # 2-element list
        self.markersize = markersize
        self.linestyle = linestyle
        self.linewidth = linewidth
        self.cmap = cmap
        self.connectDots = connectDots
        self.fitcolor = fitcolor
        self.insetPositon = insetPosition
        self.insetWidth = insetWidth
        self.insetHeight = insetHeight
        self.insetBorderPad = insetBorderPad
        self.legendOn = legendOn
        self.labelPad = labelPad

    def overrideDecorator(self, override):
        if override.xlabel is not None:
            self.xlabel = override.xlabel
        if override.ylabel is not None:
            self.ylabel = override.ylabel
        if override.zlabel is not None:
            self.zlabel = override.zlabel
        if override.xlim is not None:
            self.xlim = override.xlim
        if override.ylim is not None:
            self.ylim = override.ylim
        if override.zlim is not None:
            self.zlim = override.zlim
        if override.markersize is not None:
            self.markersize = override.markersize
        if override.linestyle is not None:
            self.linestyle = override.linestyle
        if override.linewidth is not None:
            self.linewidth = override.linewidth
        if override.cmap is not None:
            self.cmap = override.cmap
        if override.connectDots is not None:
            self.connectDots = override.connectDots
        if override.fitcolor is not None:
            self.fitcolor = override.fitcolor
        if override.insetPositon is not None:
            self.insetPosition = override.insetPosition
        if override.insetWidth is not None:
            self.insetWidth = override.insetWidth
        if override.insetHeight is not None:
            self.insetHeight = override.insetHeight
        if override.insetBorderPad is not None:
            self.insetBorderPad = override.insetBorderPad
        if override.legendOn is not None:
            self.legendOn = override.legendOn
        if override.labelPad is not None:
            self.labelPad = override.labelPad


class Decorators(Enum):
    SQI_IV = Decorator(xlabel = SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli),
                       ylabel = SILabel(PlotUnits.Current, PlotScales.Micro),
                       zlabel = SILabel(PlotUnits.Voltage, PlotScales.Micro))
    SQI_dVdI = Decorator(xlabel = SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli),
                         ylabel = SILabel(PlotUnits.Current, PlotScales.Micro),
                         zlabel = SILabel(PlotUnits.DifferentialResistance, PlotScales.Unit))
    SQI_IV_x = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_x, PlotScales.Milli),
                       ylabel=SILabel(PlotUnits.Current, PlotScales.Micro),
                       zlabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    SQI_dVdI_x = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_x, PlotScales.Milli),
                         ylabel=SILabel(PlotUnits.Current, PlotScales.Micro),
                         zlabel=SILabel(PlotUnits.DifferentialResistance, PlotScales.Unit))
    SQI_IV_y = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_y, PlotScales.Milli),
                       ylabel=SILabel(PlotUnits.Current, PlotScales.Micro),
                       zlabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    SQI_dVdI_y = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_y, PlotScales.Milli),
                         ylabel=SILabel(PlotUnits.Current, PlotScales.Micro),
                         zlabel=SILabel(PlotUnits.DifferentialResistance, PlotScales.Unit))
    SQI_IV_z = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_z, PlotScales.Milli),
                       ylabel=SILabel(PlotUnits.Current, PlotScales.Micro),
                       zlabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    SQI_dVdI_z = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_z, PlotScales.Milli),
                         ylabel=SILabel(PlotUnits.Current, PlotScales.Micro),
                         zlabel=SILabel(PlotUnits.DifferentialResistance, PlotScales.Unit))
    Ic_T = Decorator(xlabel = SILabel(PlotUnits.Temperature, PlotScales.Unit),
                     ylabel = SILabel(PlotUnits.CriticalCurrent, PlotScales.Micro))
    Ic_MagneticField = Decorator(xlabel = SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli),
                                 ylabel = SILabel(PlotUnits.CriticalCurrent, PlotScales.Micro))
    Ic_MagneticField_x = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_x, PlotScales.Milli),
                                 ylabel=SILabel(PlotUnits.CriticalCurrent, PlotScales.Micro))
    Ic_MagneticField_y = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_y, PlotScales.Milli),
                                 ylabel=SILabel(PlotUnits.CriticalCurrent, PlotScales.Micro))
    Ic_MagneticField_z = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_z, PlotScales.Milli),
                                 ylabel=SILabel(PlotUnits.CriticalCurrent, PlotScales.Micro))
    Current_Voltage = Decorator(xlabel = SILabel(PlotUnits.Current, PlotScales.Micro),
                                ylabel = SILabel(PlotUnits.Voltage, PlotScales.Micro))
    ConstantBias_T = Decorator(xlabel=SILabel(PlotUnits.Temperature, PlotScales.Unit),
                     ylabel=SILabel(PlotUnits.CriticalCurrent, PlotScales.Micro))
    ConstantBias_MagneticField = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli),
                                 ylabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    ConstantBias_MagneticField_x = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_x, PlotScales.Milli),
                                   ylabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    ConstantBias_MagneticField_y = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_y, PlotScales.Milli),
                                   ylabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    ConstantBias_MagneticField_z = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_z, PlotScales.Milli),
                                   ylabel=SILabel(PlotUnits.Voltage, PlotScales.Micro))
    Resistance_T = Decorator(xlabel=SILabel(PlotUnits.Temperature, PlotScales.Unit),
                               ylabel=SILabel(PlotUnits.Resistance, PlotScales.Unit))
    Resistance_MagneticField = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField, PlotScales.Milli),
                                           ylabel=SILabel(PlotUnits.Resistance, PlotScales.Unit))
    Resistance_MagneticField_x = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_x, PlotScales.Milli),
                                             ylabel=SILabel(PlotUnits.Resistance, PlotScales.Unit))
    Resistance_MagneticField_y = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_y, PlotScales.Milli),
                                             ylabel=SILabel(PlotUnits.Resistance, PlotScales.Unit))
    Resistance_MagneticField_z = Decorator(xlabel=SILabel(PlotUnits.InPlaneAppliedMagneticField_z, PlotScales.Milli),
                                             ylabel=SILabel(PlotUnits.Resistance, PlotScales.Unit))