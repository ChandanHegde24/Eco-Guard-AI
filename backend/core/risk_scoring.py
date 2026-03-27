import sys
import io
from typing import Any

# Fix Windows console encoding for emoji/unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def assess_climate_risk(change_percentage: float) -> dict:
    """
    Evaluates the percentage of environmental change and assigns a risk level and action 
    based on the Eco-Guard AI climate risk scoring system.
    """
    # Evaluate for Green Level: Less than 5% change
    if change_percentage < 5.0:
        return {
            "change_percentage": round(change_percentage, 2),
            "risk_level": "Green",
            "indicator": "🟢",
            "action": "Monitor",
            "trigger_alert": False
        }
        
    # Evaluate for Yellow Level: Between 5% and 15% change
    elif 5.0 <= change_percentage <= 15.0:
        return {
            "change_percentage": round(change_percentage, 2),
            "risk_level": "Yellow",
            "indicator": "🟡",
            "action": "Warning",
            "trigger_alert": False 
        }
        
    # Evaluate for Red Level: Greater than 15% change
    else:
        return {
            "change_percentage": round(change_percentage, 2),
            "risk_level": "Red",
            "indicator": "🔴",
            "action": "Immediate Alert",
            "trigger_alert": True
        }


def assess_composite_climate_risk(
    ndvi_change_percentage: float,
    ndwi_change_percentage: float,
) -> dict[str, Any]:
    """
    Computes a composite risk report from vegetation and water index changes.

    NDVI is weighted higher because vegetation stress is the primary indicator in
    the current product. NDWI contributes additional context for water-related
    changes.
    """
    ndvi = abs(ndvi_change_percentage)
    ndwi = abs(ndwi_change_percentage)

    composite_change = (0.7 * ndvi) + (0.3 * ndwi)
    base = assess_climate_risk(composite_change)

    reason_codes: list[str] = []
    if ndvi >= 15.0:
        reason_codes.append("VEGETATION_STRESS_CRITICAL")
    elif ndvi >= 5.0:
        reason_codes.append("VEGETATION_STRESS_ELEVATED")

    if ndwi >= 12.0:
        reason_codes.append("WATER_CHANGE_CRITICAL")
    elif ndwi >= 4.0:
        reason_codes.append("WATER_CHANGE_ELEVATED")

    if not reason_codes:
        reason_codes.append("STABLE_CONDITIONS")

    # Confidence grows as both indicators move in the same direction and with
    # larger magnitude. Keep this simple and bounded for predictable behavior.
    agreement_bonus = min(abs(ndvi - ndwi), 10.0)
    confidence = min(0.55 + (composite_change / 40.0) + (agreement_bonus / 200.0), 0.99)

    report = {
        "composite_change_percentage": round(composite_change, 2),
        "index_breakdown": {
            "ndvi_change_percentage": round(ndvi_change_percentage, 2),
            "ndwi_change_percentage": round(ndwi_change_percentage, 2),
            "weights": {"ndvi": 0.7, "ndwi": 0.3},
        },
        "confidence": round(confidence, 2),
        "reason_codes": reason_codes,
    }
    report.update(base)
    # Preserve backward-compatible key while clarifying it is composite.
    report["change_percentage"] = report["composite_change_percentage"]
    return report