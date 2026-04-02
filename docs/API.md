# API Reference

## Health Endpoints

- `GET /health`: Service liveness.
- `GET /ready`: Readiness with dependency checks.

## Analysis Endpoints

- `POST /api/v1/analyze-region`
  - Request body:
    - `latitude` (float)
    - `longitude` (float)
    - `time_t1` (date string, YYYY-MM-DD)
    - `time_t2` (date string, YYYY-MM-DD)
  - Returns composite risk analysis, index breakdown, and thumbnails.

- `GET /api/v1/analysis/recent?limit=20`
  - Returns recent analysis runs, newest first.
  - Limit is clamped to range 1..100.
