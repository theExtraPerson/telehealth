FROM python:3.11-slim

# Install OS-level build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy your Flask app source code
COPY . .

# Expose the port Render expects
EXPOSE 8000

# Use gunicorn to run the app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
