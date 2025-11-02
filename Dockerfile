FROM python:3.11-slim

WORKDIR /app

# Instala dependências de sistema necessárias para matplotlib e fretboardgtr
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libfreetype6-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Comando padrão para rodar no Render
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
