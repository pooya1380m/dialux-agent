"""Minimal parsers for Eulumdat (.ldt) and IESNA LM-63 (.ies) files."""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class Luminaire:
    name: str
    luminous_flux_lm: float
    power_w: float
    max_intensity_cd: float = 0.0

    @property
    def efficacy_lm_per_w(self) -> float:
        return self.luminous_flux_lm / self.power_w if self.power_w else 0.0


def parse_ldt(text: str) -> Luminaire:
    """Parse an Eulumdat file (flux = sum of lamp flux x number of lamps)."""
    lines = [ln.strip() for ln in text.splitlines()]
    if len(lines) < 27:
        raise ValueError("LDT file too short")
    name = lines[2] or lines[0]
    n_sets = int(lines[25])  # number of lamp sets
    base = 26
    flux = power = 0.0
    for i in range(n_sets):
        o = base + i * 6
        n_lamps = abs(int(float(lines[o])))
        lamp_flux = float(lines[o + 2])
        lamp_w = float(lines[o + 5])
        flux += n_lamps * lamp_flux
        power += lamp_w
    return Luminaire(name, flux, power)


def parse_ies(text: str) -> Luminaire:
    """Parse an IES LM-63 file (lumens/power from header, peak candela)."""
    m = re.search(r"^TILT=.*$", text, re.M)
    if not m:
        raise ValueError("Missing TILT line")
    name_m = re.search(r"\[LUMCAT\]\s*(.*)", text) or re.search(r"\[LUMINAIRE\]\s*(.*)", text)
    name = name_m.group(1).strip() if name_m else "unknown"
    tilt = m.group(0).split("=", 1)[1].strip()
    tokens = text[m.end():].split()
    if tilt == "INCLUDE":
        raise ValueError("TILT=INCLUDE not supported")
    n_lamps, lumens_per_lamp, mult = int(tokens[0]), float(tokens[1]), float(tokens[2])
    n_v, n_h = int(tokens[3]), int(tokens[4])
    watts = float(tokens[12])
    start = 13 + n_v + n_h
    candela = [float(x) for x in tokens[start:start + n_v * n_h]]
    flux = n_lamps * lumens_per_lamp if lumens_per_lamp > 0 else 0.0
    peak = max(candela, default=0.0) * mult
    return Luminaire(name, flux, watts, peak)


def load(path: str) -> Luminaire:
    with open(path, encoding="latin-1") as f:
        text = f.read()
    return parse_ldt(text) if path.lower().endswith(".ldt") else parse_ies(text)
