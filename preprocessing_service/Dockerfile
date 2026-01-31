FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# poppler-utils: for pdf2image
# libgl1-mesa-glx & libglib2.0-0: for opencv (even headless sometimes needs these linked libs)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
