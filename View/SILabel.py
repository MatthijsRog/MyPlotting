from enum import Enum, auto
from typing import NamedTuple

class UnitSymbol(NamedTuple):
    unit: str
    textSymbol: str
    SISymbol: str

class SizeSymbol(NamedTuple):
    scale: float
    textSymbol: str
    SISymbol: str

class PlotUnits(UnitSymbol, Enum):
    Current                       = UnitSymbol(unit=r"Current",       textSymbol=r"A",    SISymbol=r"\ampere")
    Voltage                       = UnitSymbol(unit=r"Voltage",       textSymbol=r"A",    SISymbol=r"\volt")
    InPlaneAppliedMagneticField   = UnitSymbol(unit=r"$\mu_0 H$",     textSymbol=r"T",    SISymbol=r"\tesla")
    InPlaneAppliedMagneticField_x = UnitSymbol(unit=r"$\mu_0 H_x$", textSymbol=r"T", SISymbol=r"\tesla")
    InPlaneAppliedMagneticField_y = UnitSymbol(unit=r"$\mu_0 H_y$", textSymbol=r"T", SISymbol=r"\tesla")
    InPlaneAppliedMagneticField_z = UnitSymbol(unit=r"$\mu_0 H_z$", textSymbol=r"T", SISymbol=r"\tesla")
    DifferentialResistance        = UnitSymbol(unit=r"$dV/dI$",       textSymbol=r"Ohms", SISymbol=r"\ohm")
    CriticalCurrent               = UnitSymbol(unit=r"$I_C$",         textSymbol=r"A",    SISymbol=r"\ampere")
    Temperature                   = UnitSymbol(unit=r"Temperature",   textSymbol=r"K",    SISymbol=r"\kelvin")
    CurrentPerTemperature         = UnitSymbol(unit=r"$dI/dT$",       textSymbol=r"A/K",  SISymbol=r"\current\per\kelvin")
    StandardDeviation_MagneticField  = UnitSymbol(unit=r"$\sigma$",       textSymbol=r"T", SISymbol=r"\tesla")
    InductancePerArea             = UnitSymbol(unit=r"dL/dA", textSymbol=r"H/m^2", SISymbol=r"\henry\per\meter\squared")

class PlotScales(SizeSymbol, Enum):
    Giga = SizeSymbol(scale = 1e9, textSymbol = r"G", SISymbol = r"\giga")
    Mega = SizeSymbol(scale = 1e6, textSymbol = r"M", SISymbol = r"\mega")
    Kilo = SizeSymbol(scale = 1e3, textSymbol = r"K", SISymbol = r"\kilo")
    Unit = SizeSymbol(scale = 1e0, textSymbol = r"", SISymbol = r"")
    Milli = SizeSymbol(scale = 1e-3, textSymbol = r"m", SISymbol = r"\milli")
    Micro = SizeSymbol(scale = 1e-6, textSymbol = r"u", SISymbol = r"\micro")
    Nano = SizeSymbol(scale = 1e-9, textSymbol = r"n", SISymbol = r"\nano")
    Pico = SizeSymbol(scale = 1e-12, textSymbol = r"p", SISymbol = r"\pico")

class SILabel():
    _label = None # Not set standard
    _unit  = None
    _scale  = PlotScales.Unit

    def __init__(self, plotUnit, plotScale, label=None):
        if label != None:
            self._label = label.encode('unicode-escape')
        self._unit = plotUnit
        self._scale = plotScale

    @property
    def scale(self):
        return float(self._scale.scale)

    def generateLaTeXSymbol(self):
        return r"\SI{}{" + self._scale.SISymbol + self._unit.SISymbol + r"}"

    def generateTextSymbol(self):
        return self._scale.textSymbol + self._unit.textSymbol

    def generateLaTeXUnit(self):
        return self._unit.unit

    def generateTextUnit(self):
        return self._unit.unit

    def generateLaTeXLabel(self):
        if self._label == None:
            return self._unit.unit + r" (" + self.generateLaTeXSymbol() + r")"
        else:
            return self._label + + r" (" + self.generateLaTeXSymbol() + r")"

    def generateTextLabel(self):
        if self._label == None:
            return self._unit.unit + r" (" + self.generateTextSymbol() + r")"
        else:
            return self._label + r" (" + self.generateTextSymbol() + r")"
