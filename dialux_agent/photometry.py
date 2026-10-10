"""Minimal parsers for Eulumdat (.ldt) and IESNA LM-63 (.ies) files."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re


def _number(value: str, field: str) -> float:
    try:
        number = float(value)
    except ValueError as e:
        raise ValueError(f"Invalid {field}: {value!r}") from e
    if not math.isfinite(number):
        raise ValueError(f"Invalid {field}: {value!r}")
    return number


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
    try:
        n_sets = int(lines[25])  # number of lamp sets
    except ValueError as e:
        raise ValueError("Invalid LDT lamp-set count") from e
    if n_sets < 1:
        raise ValueError("LDT must contain at least one lamp set")
    base = 26
    if len(lines) < base + n_sets * 6:
        raise ValueError("LDT file has incomplete lamp-set data")
    flux = power = 0.0
    for i in range(n_sets):
        o = base + i * 6
        n_lamps = abs(int(_number(lines[o], "LDT lamp count")))
        lamp_flux = _number(lines[o + 2], "LDT lamp flux")
        lamp_w = _number(lines[o + 5], "LDT lamp power")
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
    if tilt != "NONE":
        raise ValueError(f"TILT={tilt} is not supported")
    tokens = text[m.end():].split()
    if len(tokens) < 13:
        raise ValueError("IES file has incomplete photometric header")
    try:
        n_lamps = int(tokens[0])
        lumens_per_lamp = _number(tokens[1], "IES lamp lumens")
        mult = _number(tokens[2], "IES candela multiplier")
        n_v, n_h = int(tokens[3]), int(tokens[4])
        watts = _number(tokens[12], "IES input watts")
    except ValueError as e:
        raise ValueError("IES file has invalid photometric header") from e
    if n_lamps < 1 or n_v < 1 or n_h < 1:
        raise ValueError("IES lamp and angle counts must be positive")
    start = 13 + n_v + n_h
    end = start + n_v * n_h
    if len(tokens) < end:
        raise ValueError("IES file has incomplete angle or candela data")
    candela = [_number(x, "IES candela value") for x in tokens[start:end]]
    flux = n_lamps * lumens_per_lamp if lumens_per_lamp > 0 else 0.0
    peak = max(candela, default=0.0) * mult
    return Luminaire(name, flux, watts, peak)


def load(path: str) -> Luminaire:
    with open(path, encoding="latin-1") as f:
        text = f.read()
    suffix = str(path).lower()
    if suffix.endswith(".ldt"):
        return parse_ldt(text)
    if suffix.endswith(".ies"):
        return parse_ies(text)
    raise ValueError("Unsupported photometry file type; expected .ldt or .ies")
