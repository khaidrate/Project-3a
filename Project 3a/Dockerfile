# =============================================================================
# Dockerfile — Stock Data Visualizer
# =============================================================================
# Builds a lightweight Python 3.11 image, installs dependencies, and starts
# the Flask development server on port 5000.
#
# Build:   docker build -t stock-visualizer .
# Run:     docker run -p 5000:5000 stock-visualizer
#   (or just use:  docker-compose up)
# =============================================================================

# Use the official slim Python 3.11 image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first so Docker can cache this layer
# (only re-runs pip install if requirements.txt actually changed)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port Flask listens on
EXPOSE 5000

# Start the Flask application
# Using python -m flask run makes FLASK_APP unnecessary
CMD ["python", "app.py"]
