# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and CSV data file into the container
COPY . .

# Expose the application port
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]