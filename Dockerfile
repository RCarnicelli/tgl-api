FROM python:3.11-slim

# Instala dependências do sistema necessárias para compilar pycairo e svglib
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libfreetype6-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
