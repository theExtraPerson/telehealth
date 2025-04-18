FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask app source code
COPY . .

# Expose the port Render expects
EXPOSE 8000

# Use gunicorn to run the app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
