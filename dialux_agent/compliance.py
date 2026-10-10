"""Subset of EN 12464-1 requirements (verify against the current standard)."""
from __future__ import annotations

# room type: (maintained Em lux, min uniformity U0, max UGR, min Ra)
REQUIREMENTS = {
    "office": (500, 0.6, 19, 80),
    "classroom": (300, 0.6, 19, 80),
    "corridor": (100, 0.4, 28, 40),
    "meeting room": (500, 0.6, 19, 80),
    "warehouse": (100, 0.4, 25, 60),
    "kitchen": (500, 0.6, 22, 80),
}


def check(room_type: str, em: float, u0: float, ugr: float | None = None,
          ra: float | None = None) -> list[str]:
    """Return a list of violations (empty means compliant)."""
    key = room_type.lower()
    if key not in REQUIREMENTS:
        raise KeyError(f"Unknown room type: {room_type}")
    r_em, r_u0, r_ugr, r_ra = REQUIREMENTS[key]
    out = []
    if em < r_em:
        out.append(f"Em {em} lx < required {r_em} lx")
    if u0 < r_u0:
        out.append(f"U0 {u0} < required {r_u0}")
    if ugr is not None and ugr > r_ugr:
        out.append(f"UGR {ugr} > limit {r_ugr}")
    if ra is not None and ra < r_ra:
        out.append(f"Ra {ra} < required {r_ra}")
    return out
