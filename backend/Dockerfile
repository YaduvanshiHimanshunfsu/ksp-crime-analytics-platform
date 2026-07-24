FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY Dataset /app/Dataset
ENV DATA_PATH=/app/Dataset/processed/synthetic_cases.csv
ENV PUBLIC_DATA_DIR=/app/Dataset/OpenCity.in Karnataka Crime Data 2025
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

