FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependências do sistema (necessárias para CairoSVG e fretboardgtr)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libcairo2-dev pkg-config python3-dev libfreetype6-dev build-essential \
 && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copia o app
COPY . .

EXPOSE 10000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
