from core.risk_scoring import assess_climate_risk, assess_composite_climate_risk


def test_risk_scoring_green_band() -> None:
    result = assess_climate_risk(2.9)
    assert result["risk_level"] == "Green"
    assert result["trigger_alert"] is False


def test_risk_scoring_yellow_band() -> None:
    result = assess_climate_risk(10.0)
    assert result["risk_level"] == "Yellow"
    assert result["trigger_alert"] is False


def test_risk_scoring_red_band() -> None:
    result = assess_climate_risk(25.0)
    assert result["risk_level"] == "Red"
    assert result["trigger_alert"] is True


def test_composite_risk_reports_breakdown_and_confidence() -> None:
    result = assess_composite_climate_risk(8.0, 3.0)

    assert result["risk_level"] == "Yellow"
    assert result["trigger_alert"] is False
    assert result["composite_change_percentage"] == 6.5
    assert result["index_breakdown"]["weights"] == {"ndvi": 0.7, "ndwi": 0.3}
    assert 0.0 <= result["confidence"] <= 1.0
    assert "VEGETATION_STRESS_ELEVATED" in result["reason_codes"]


def test_composite_risk_turns_red_for_large_changes() -> None:
    result = assess_composite_climate_risk(20.0, 15.0)

    assert result["risk_level"] == "Red"
    assert result["trigger_alert"] is True
    assert "VEGETATION_STRESS_CRITICAL" in result["reason_codes"]
    assert "WATER_CHANGE_CRITICAL" in result["reason_codes"]
