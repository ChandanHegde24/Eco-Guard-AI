import sys
import io

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