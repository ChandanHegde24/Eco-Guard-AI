FROM python:3.11-slim

WORKDIR /app

# Install dependencies (only streamlit and folium requests are strictly needed for the frontend, but we can reuse requirements)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ ./

ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
