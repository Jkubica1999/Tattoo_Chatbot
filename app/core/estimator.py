from typing import Tuple

def estimate(size_band: str, style: str, placement: str, color: str,
             rate: float = 120.0, shop_min: float = 80.0,
             k: float = 0.06,
             style_mul: dict | None = None,
             place_mul: dict | None = None,
             color_mul: dict | None = None) -> Tuple[float,int,int]:
    size_map = {"≤5cm":10, "6–10cm":40, "11–15cm":100, ">15cm":225}
    area = size_map.get(size_band, 40)
    style_m = (style_mul or {"Fine-line":0.85,"Traditional":1.0,"Realism":1.2,"Japanese":1.1}).get(style, 1.0)
    place_m = (place_mul or {"Forearm":1.0,"Ribs":1.2,"Hand":1.2,"Back":1.05}).get(placement, 1.1)
    color_m = (color_mul or {"Color":1.15,"Black & grey":1.0}).get(color, 1.0)

    hours = max(0.5, k * (area ** 0.5) * style_m * place_m * color_m)
    price_mid = max(shop_min, round(hours * rate))
    low, high = round(price_mid * 0.85), round(price_mid * 1.25)
    return round(hours, 1), low, high

def estimate_from_area(area_cm2: float, style: str, placement: str, color: str,
                       rate: float = 120.0, shop_min: float = 80.0,
                       k: float = 0.06,
                       style_mul: dict | None = None,
                       place_mul: dict | None = None,
                       color_mul: dict | None = None) -> tuple[float,int,int]:
    style_m = (style_mul or {"Fine-line":0.85,"Traditional":1.0,"Realism":1.2,"Japanese":1.1}).get(style, 1.0)
    place_m = (place_mul or {"Forearm":1.0,"Ribs":1.2,"Hand":1.2,"Back":1.05}).get(placement, 1.1)
    color_m = (color_mul or {"Color":1.15,"Black & grey":1.0}).get(color, 1.0)
    hours = max(0.5, k * (area_cm2 ** 0.5) * style_m * place_m * color_m)
    price_mid = max(shop_min, round(hours * rate))
    low, high = round(price_mid * 0.85), round(price_mid * 1.25)
    return round(hours, 1), low, high