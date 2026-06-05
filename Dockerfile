FROM python:3.8-slim-buster

# 1. Update, install system dependencies, and clean up in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Set the working directory
WORKDIR /app

# 3. Install Python dependencies (including AWS CLI)
# It is best practice to include 'awscli' in your requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application code
COPY . .

# 5. Run the application
CMD ["python3", "app.py"]