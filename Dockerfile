FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY postwire/ postwire/
COPY .env.example .env

EXPOSE 8000

CMD ["uvicorn", "postwire.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
