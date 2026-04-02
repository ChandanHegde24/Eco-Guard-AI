# Developer Guide

## Repository Layout

- `backend/`: FastAPI service and analysis pipeline.
- `frontend/`: Streamlit dashboard.
- `backend/tests/`: pytest suite.

## Testing

- Run all backend tests:
  - `pytest backend/tests -q`

## Configuration

Settings are loaded from environment variables via `backend/core/config.py`.

Important performance settings:

- `ANALYSIS_CACHE_TTL_SECONDS`
- `ANALYSIS_CACHE_MAX_ITEMS`

## Notes

- Earth Engine dependent endpoints require valid authentication.
- Keep external calls mocked in tests for reliability.
