FROM python:3.12-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY app /app


ENTRYPOINT ["python", "/app/stocks_orchestrator.py"]