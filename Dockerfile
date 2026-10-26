FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port and configure environment
EXPOSE 8080
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the Tornado web server
CMD ["python", "koraput_tourism/server.py"]
