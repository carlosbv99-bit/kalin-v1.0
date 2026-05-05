FROM python:3.11-slim

# Crear usuario no-root para seguridad
RUN groupadd -r kalin && useradd -r -g kalin kalin

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias primero (mejor cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs sessions cache plugins && \
    chown -R kalin:kalin /app

# Cambiar a usuario no-root
USER kalin

# Puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV FLASK_DEBUG=0
ENV KALIN_MODE=local

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health') || exit 1"

# Comando de inicio
CMD ["python", "run.py"]
