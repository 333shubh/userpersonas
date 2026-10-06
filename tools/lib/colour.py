"""Colour maths shared by the validators. Standard library only.

- WCAG 2.x relative luminance and contrast ratio.
- Colour-vision-deficiency simulation: Machado, Oliveira & Fernandes (2009),
  severity 1.0, applied in linear sRGB (same model as the dataviz skill, so the
  thresholds below are calibrated to it).
- Colour difference: Euclidean distance in OKLab, x100 ("dE").
"""

import math
import re

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# WCAG 2.2 thresholds
WCAG = {
    "AA": {"body": 4.5, "large": 3.0, "ui": 3.0},
    "AAA": {"body": 7.0, "large": 4.5, "ui": 3.0},  # 1.4.11 has no AAA level; 3:1 applies
}

# dataviz-skill CVD thresholds (OKLab dE x100)
CVD_TARGET = 8.0  # pass
CVD_FLOOR = 6.0  # legal only with a declared secondary (non-colour) cue
NORMAL_FLOOR = 15.0  # unsimulated vision, hard gate for distinguish-pairs

MACHADO = {
    "protanopia": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}
CVD_KINDS = tuple(MACHADO)


def is_hex(value):
    return isinstance(value, str) and bool(HEX_RE.match(value))


def hex_to_srgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def srgb_to_hex(rgb):
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02X}" for c in rgb)


def _to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_gamma(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def linear(h):
    return tuple(_to_linear(c) for c in hex_to_srgb(h))


def luminance(h):
    r, g, b = linear(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def simulate_linear(h, kind):
    m = MACHADO[kind]
    r, g, b = linear(h)
    return tuple(max(0.0, min(1.0, row[0] * r + row[1] * g + row[2] * b)) for row in m)


def simulate(h, kind):
    """Hex as seen under the given CVD (for reports and swatches)."""
    return srgb_to_hex(tuple(_to_gamma(c) for c in simulate_linear(h, kind)))


def oklab_from_linear(rgb):
    r, g, b = rgb
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def oklch(h):
    L, a, b = oklab_from_linear(linear(h))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def delta_e(a, b, kind=None):
    """OKLab Euclidean distance x100. kind=None means unsimulated vision."""
    la = oklab_from_linear(simulate_linear(a, kind) if kind else linear(a))
    lb = oklab_from_linear(simulate_linear(b, kind) if kind else linear(b))
    return 100 * math.dist(la, lb)


def is_achromatic(h):
    r, g, b = hex_to_srgb(h)
    return r == g == b


def hsv_saturation(h):
    rgb = hex_to_srgb(h)
    mx, mn = max(rgb), min(rgb)
    return 0.0 if mx == 0 else (mx - mn) / mx


def mix(a, b, t):
    """Mix in gamma sRGB (how a duotone tint is specified in print terms)."""
    ra, rb = hex_to_srgb(a), hex_to_srgb(b)
    return srgb_to_hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def srgb_distance(a, b):
    return max(abs(x - y) for x, y in zip(hex_to_srgb(a), hex_to_srgb(b))) * 255


def _self_test():
    assert abs(contrast("#000000", "#FFFFFF") - 21.0) < 1e-9
    assert abs(contrast("#777777", "#FFFFFF") - 4.48) < 0.01
    assert delta_e("#123456", "#123456") == 0
    assert is_achromatic("#7A7A7A") and not is_achromatic("#7A7A7B")
    # Machado deuteranopia collapses pure red and a matching green far more than normal vision
    assert delta_e("#D62728", "#2CA02C", "deuteranopia") < delta_e("#D62728", "#2CA02C")


_self_test()
