"""Lumen-method estimation."""
from __future__ import annotations

import math


def room_index(length: float, width: float, height_above_workplane: float) -> float:
    return length * width / (height_above_workplane * (length + width))


def utilance_estimate(k: float, rho_ceiling: float = 0.7, rho_walls: float = 0.5) -> float:
    """Rough utilance factor from room index (approximation, not a table lookup)."""
    base = 0.85 * (1 - math.exp(-0.9 * k))
    refl = 0.8 + 0.2 * (rho_ceiling + rho_walls) / 1.2
    return min(base * refl, 0.95)


def luminaires_needed(target_lux: float, length: float, width: float,
                      luminaire_flux_lm: float, height_above_workplane: float,
                      maintenance_factor: float = 0.8, utilance: float | None = None) -> int:
    if min(length, width, height_above_workplane, luminaire_flux_lm, maintenance_factor) <= 0:
        raise ValueError("Dimensions, flux and maintenance factor must be positive")
    u = utilance if utilance is not None else utilance_estimate(
        room_index(length, width, height_above_workplane))
    return math.ceil(target_lux * length * width / (luminaire_flux_lm * u * maintenance_factor))


def average_illuminance(n: int, flux_lm: float, length: float, width: float,
                        utilance: float, maintenance_factor: float = 0.8) -> float:
    return n * flux_lm * utilance * maintenance_factor / (length * width)
