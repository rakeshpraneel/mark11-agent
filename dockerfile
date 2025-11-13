# Use a lightweight Python base image
FROM python:3.10-slim-buster


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app


EXPOSE 8000

# Define the command to run the FastAPI application with Uvicorn
# Replace 'main:app' with the actual path to your FastAPI application instance
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]