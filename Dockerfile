# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Copy & Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"]