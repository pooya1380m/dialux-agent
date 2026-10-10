"""Lumen-method estimation."""
from __future__ import annotations

import math


def _positive_finite(**values: float) -> None:
    for name, value in values.items():
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a positive finite number")


def _factor(value: float, name: str) -> None:
    if not math.isfinite(value) or not 0 < value <= 1:
        raise ValueError(f"{name} must be greater than 0 and at most 1")


def room_index(length: float, width: float, height_above_workplane: float) -> float:
    _positive_finite(length=length, width=width, height_above_workplane=height_above_workplane)
    return length * width / (height_above_workplane * (length + width))


def utilance_estimate(k: float, rho_ceiling: float = 0.7, rho_walls: float = 0.5) -> float:
    """Rough utilance factor from room index (approximation, not a table lookup)."""
    _positive_finite(k=k)
    for name, reflectance in (("rho_ceiling", rho_ceiling), ("rho_walls", rho_walls)):
        if not math.isfinite(reflectance) or not 0 <= reflectance <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    base = 0.85 * (1 - math.exp(-0.9 * k))
    refl = 0.8 + 0.2 * (rho_ceiling + rho_walls) / 1.2
    return min(base * refl, 0.95)


def luminaires_needed(target_lux: float, length: float, width: float,
                      luminaire_flux_lm: float, height_above_workplane: float,
                      maintenance_factor: float = 0.8, utilance: float | None = None) -> int:
    if not math.isfinite(target_lux) or target_lux < 0:
        raise ValueError("target_lux must be a nonnegative finite number")
    _positive_finite(length=length, width=width, height_above_workplane=height_above_workplane,
                     luminaire_flux_lm=luminaire_flux_lm)
    _factor(maintenance_factor, "maintenance_factor")
    if utilance is not None:
        _factor(utilance, "utilance")
    u = utilance if utilance is not None else utilance_estimate(
        room_index(length, width, height_above_workplane))
    return math.ceil(target_lux * length * width / (luminaire_flux_lm * u * maintenance_factor))


def average_illuminance(n: int, flux_lm: float, length: float, width: float,
                        utilance: float, maintenance_factor: float = 0.8) -> float:
    if not math.isfinite(n) or n < 0 or not float(n).is_integer():
        raise ValueError("n must be a nonnegative integer")
    _positive_finite(flux_lm=flux_lm, length=length, width=width)
    _factor(utilance, "utilance")
    _factor(maintenance_factor, "maintenance_factor")
    return n * flux_lm * utilance * maintenance_factor / (length * width)
