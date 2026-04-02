# Installation Guide

## Prerequisites

- Python 3.11+
- Google Earth Engine account

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy environment template:
   - `cp .env.example .env`
4. Authenticate Earth Engine:
   - `earthengine authenticate`
5. Start backend:
   - `cd backend`
   - `python main.py`
6. Start frontend in a separate terminal:
   - `streamlit run frontend/dashboard.py`

## Docker Setup

1. Build and start services:
   - `docker compose up --build`
2. Backend: `http://localhost:8000`
3. Frontend: `http://localhost:8501`
