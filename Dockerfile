# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the Flask default port
EXPOSE 5000

# Define the command to run the Flask app
CMD ["python", "app.py"]
