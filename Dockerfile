# Dockerfile for the FastAPI + Streamlit application
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Function to run FastAPI\n\
start_fastapi() {\n\
    echo "Starting FastAPI server..."\n\
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &\n\
    FASTAPI_PID=$!\n\
    echo "FastAPI started with PID $FASTAPI_PID"\n\
}\n\
\n\
# Function to run Streamlit\n\
start_streamlit() {\n\
    echo "Starting Streamlit UI..."\n\
    streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 &\n\
    STREAMLIT_PID=$!\n\
    echo "Streamlit started with PID $STREAMLIT_PID"\n\
}\n\
\n\
# Start both services\n\
start_fastapi\n\
start_streamlit\n\
\n\
# Wait for any process to exit\n\
wait -n\n\
\n\
# Exit with status of process that exited first\n\
exit $?' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
