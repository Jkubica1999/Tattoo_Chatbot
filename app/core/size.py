# app/core/size.py
from typing import Optional, Tuple, List, Dict
import math

IN2_TO_CM2 = 6.4516  # 1 in^2 -> cm^2

def pick_band_area_cm2(label: str, bands: List[Dict]) -> Tuple[float, str]:
    """
    Find a band by label; return a stable representative area (midpoint),
    and echo the label we used for copy.
    If the band is open-ended (max None), use min * 1.25 as a conservative rep.
    """
    for b in bands:
        if b.get("label") == label:
            mn = float(b.get("min_cm2") or 0)
            mx = b.get("max_cm2")
            if mx is None:
                area = mn * 1.25
            else:
                area = (mn + float(mx)) / 2.0
            return area, b["label"]

    # Fallback: first band's midpoint (or min*1.25 if open-ended)
    b0 = bands[0]
    mn0 = float(b0.get("min_cm2") or 0)
    mx0 = b0.get("max_cm2")
    area0 = ((mn0 + float(mx0)) / 2.0) if mx0 is not None else (mn0 * 1.25)
    return area0, b0["label"]

def nearest_band_label(area_cm2: float, bands: List[Dict]) -> str:
    """
    Map a numeric area to the nearest tenant band by range inclusion.
    If no range matches (shouldn't happen), return the last band.
    """
    for b in bands:
        mn = float(b.get("min_cm2") or 0)
        mx = b.get("max_cm2")
        if area_cm2 >= mn and (mx is None or area_cm2 <= float(mx)):
            return b["label"]
    return bands[-1]["label"]

def parse_dims_area_cm2(size_dims: str, unit: str) -> Optional[float]:
    """
    Parse WxH formats like '3x4', '3 x 4', '3 by 4'.
    Returns area in cm^2 or None if not parseable.
    """
    if not size_dims:
        return None
    s = size_dims.lower().replace(" ", "")
    s = s.replace("by", "x")  # handle '3by4' or '3 by 4'
    if "x" not in s:
        return None
    try:
        w_str, h_str = s.split("x", 1)
        w, h = float(w_str), float(h_str)
        area = w * h
        return area * IN2_TO_CM2 if unit == "in" else area
    except Exception:
        return None

def linear_to_area_cm2(value: float, unit: str) -> float:
    """
    Interpret a single linear size (e.g., '2in', '8cm') as an approximate diameter
    of a circular design and convert to area in cm^2.
    """
    d_cm = value * 2.54 if unit == "in" else value
    return math.pi * (d_cm / 2.0) ** 2

def to_area_cm2(
    size_band_label: Optional[str],
    size_value: Optional[float],
    size_unit: Optional[str],
    size_dims: Optional[str],
    tenant_bands: List[Dict],
    tenant_default_unit: str = "in",
) -> Tuple[float, str]:
    """
    Convert user-provided size info to (area_cm2, band_label_used).

    Priority:
      1) Explicit band label -> use band midpoint (or min*1.25 if open-ended)
      2) Dimensions (WxH) + unit -> numeric area
      3) Single linear value + unit -> circle approximation
      4) Fallback -> first band's representative area

    `tenant_default_unit` is used when unit is missing.
    """
    # 1) Band label wins if present
    if size_band_label:
        return pick_band_area_cm2(size_band_label, tenant_bands)

    # Normalize unit
    unit = (size_unit or tenant_default_unit or "in").lower()
    if unit not in {"cm", "in"}:
        unit = "in"

    # 2) WxH dims
    if size_dims:
        area = parse_dims_area_cm2(size_dims, unit)
        if area:
            label = nearest_band_label(area, tenant_bands)
            return float(area), label

    # 3) Single linear measurement
    if size_value and size_value > 0:
        area = linear_to_area_cm2(float(size_value), unit)
        label = nearest_band_label(area, tenant_bands)
        return float(area), label

    # 4) Fallback
    return pick_band_area_cm2(tenant_bands[0]["label"], tenant_bands)
