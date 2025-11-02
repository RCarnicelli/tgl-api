FROM python:3.11-slim

# Evita mensagens interativas e melhora performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependências do sistema necessárias para o fretboardgtr e CairoSVG
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libfreetype6-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copia dependências do Python
COPY requirements.txt .

# Instala as libs Python (incluindo fretboardgtr)
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copia o resto da aplicação
COPY . .

# Define o comando padrão do container
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
