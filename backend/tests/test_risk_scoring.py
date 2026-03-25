from core.risk_scoring import assess_climate_risk


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
