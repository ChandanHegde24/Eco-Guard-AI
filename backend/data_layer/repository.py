from sqlalchemy import select

from data_layer.models import AnalysisRun


def save_analysis_run(
    session,
    *,
    latitude: float,
    longitude: float,
    time_t1: str,
    time_t2: str,
    change_percentage: float,
    risk_level: str,
    recommended_action: str,
    alert_triggered: bool,
) -> AnalysisRun:
    run = AnalysisRun(
        latitude=latitude,
        longitude=longitude,
        time_t1=time_t1,
        time_t2=time_t2,
        change_percentage=change_percentage,
        risk_level=risk_level,
        recommended_action=recommended_action,
        alert_triggered=alert_triggered,
    )
    session.add(run)
    session.flush()
    return run


def get_recent_analysis_runs(session, limit: int = 20) -> list[AnalysisRun]:
    stmt = select(AnalysisRun).order_by(AnalysisRun.created_at.desc()).limit(limit)
    return list(session.scalars(stmt).all())
