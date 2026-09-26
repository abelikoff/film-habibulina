FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY app .
COPY ads.txt static/ads.txt
COPY data/habib.db /data/habib.db

# Run as www-data
RUN mkdir -p /var/www && chown -R www-data:www-data /var/www
USER www-data

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]

