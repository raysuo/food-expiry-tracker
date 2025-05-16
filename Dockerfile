# Use the official Python image for ARM (Raspberry Pi)
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Initialize the database
RUN sqlite3 /app/food.db "CREATE TABLE IF NOT EXISTS foods \
    (id INTEGER PRIMARY KEY AUTOINCREMENT, \
    name TEXT NOT NULL, \
    expiry_date DATE NOT NULL, \
    added_date DATE NOT NULL)"

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
