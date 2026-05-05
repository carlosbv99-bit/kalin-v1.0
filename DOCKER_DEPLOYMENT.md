# 🐳 GUÍA DE DESPLIEGUE SEGURO CON DOCKER - KALIN v3.0

## ¿Por qué usar Docker?

Docker **aisla Kalin** del sistema principal, proporcionando:
- 🔒 **Seguridad**: Si algo sale mal, solo afecta el contenedor
- 📦 **Portabilidad**: Funciona igual en Windows, Mac y Linux
- 🔄 **Consistencia**: Mismo entorno en desarrollo y producción
- 🧹 **Limpieza**: Fácil de instalar y desinstalar sin dejar rastros

---

## 📋 REQUISITOS PREVIOs

1. **Docker Desktop instalado**
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Mac: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/engine/install/

2. **Docker Compose** (viene incluido con Docker Desktop)

3. **Kalin descargado**
   ```bash
   git clone https://github.com/tu-usuario/kalin.git
   cd kalin
   ```

---

## 🚀 DESPLIEGUE RÁPIDO (5 minutos)

### Paso 1: Crear archivo `Dockerfile`

Ya está creado en la raíz del proyecto. Contenido:

```dockerfile
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
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Comando de inicio
CMD ["python", "run.py"]
```

### Paso 2: Crear archivo `docker-compose.yml`

```yaml
version: '3.8'

services:
  kalin:
    build: .
    container_name: kalin
    restart: unless-stopped
    ports:
      - "127.0.0.1:5000:5000"  # Solo localhost, NO exponer públicamente
    volumes:
      - ./logs:/app/logs
      - ./sessions:/app/sessions
      - ./cache:/app/cache
      - ./plugins:/app/plugins
      - ./proyectos:/app/proyectos  # Monta tus proyectos aquí
    environment:
      - KALIN_MODE=${KALIN_MODE:-local}
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
      - FLASK_DEBUG=0
      # API Keys (opcional, usa secrets en producción)
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
    networks:
      - kalin-network
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/health')"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G

  # Opcional: Redis para Celery (task queue)
  redis:
    image: redis:7-alpine
    container_name: kalin-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - kalin-network
    command: redis-server --appendonly yes

networks:
  kalin-network:
    driver: bridge

volumes:
  redis-data:
```

### Paso 3: Crear archivo `.env` para Docker

```env
# Modo de operación
KALIN_MODE=local

# API Keys (dejar vacío si usas Ollama local)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Configuración de recursos
COMPOSE_PROJECT_NAME=kalin
```

### Paso 4: Construir y ejecutar

```bash
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar que está corriendo
docker-compose ps

# Ver logs
docker-compose logs -f kalin
```

### Paso 5: Acceder a Kalin

Abre tu navegador: **http://localhost:5000**

¡Listo! 🎉

---

## 🔧 COMANDOS ÚTILES DE DOCKER

### Gestión básica
```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f kalin

# Detener y eliminar todo (incluyendo volúmenes)
docker-compose down -v
```

### Mantenimiento
```bash
# Actualizar a nueva versión
git pull
docker-compose build --no-cache
docker-compose up -d

# Limpiar imágenes antiguas
docker image prune -a

# Ver uso de recursos
docker stats kalin
```

### Debugging
```bash
# Ejecutar comando dentro del contenedor
docker exec -it kalin bash

# Ver logs en tiempo real
docker logs -f kalin

# Inspeccionar contenedor
docker inspect kalin

# Verificar health check
docker inspect --format='{{.State.Health.Status}}' kalin
```

---

## 🔒 CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN

### 1. Usar Docker Secrets (NO variables de entorno)

Crea archivo `secrets/api_keys.txt`:
```
OPENAI_API_KEY=sk-proj-tu-key-real
ANTHROPIC_API_KEY=sk-ant-tu-key-real
```

Actualiza `docker-compose.yml`:
```yaml
services:
  kalin:
    # ... resto de configuración ...
    secrets:
      - openai_key
      - anthropic_key

secrets:
  openai_key:
    file: ./secrets/openai_key.txt
  anthropic_key:
    file: ./secrets/anthropic_key.txt
```

### 2. Restrictir acceso de red

**NUNCA** expongas Kalin directamente a internet. Usa un reverse proxy:

```yaml
# docker-compose.yml con Nginx reverse proxy
services:
  kalin:
    # No exponer puerto públicamente
    # ports:
    #   - "5000:5000"  # ❌ NO HACER ESTO
    
    networks:
      - kalin-network
  
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"  # HTTPS
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - kalin
    networks:
      - kalin-network
```

### 3. Configurar Nginx con SSL

`nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream kalin {
        server kalin:5000;
    }

    server {
        listen 443 ssl;
        server_name kalin.tudominio.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://kalin;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # Headers de seguridad
            add_header X-Frame-Options "DENY";
            add_header X-Content-Type-Options "nosniff";
            add_header Strict-Transport-Security "max-age=31536000";
        }
    }
}
```

### 4. Limitar recursos

En `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Máximo 2 CPUs
      memory: 4G       # Máximo 4GB RAM
    reservations:
      cpus: '0.5'      # Reservar 0.5 CPU
      memory: 1G       # Reservar 1GB RAM
```

---

## 📊 MONITOREO Y LOGS

### Logs centralizados
```bash
# Ver todos los logs
docker-compose logs -f

# Solo logs de Kalin
docker-compose logs -f kalin

# Últimas 100 líneas
docker-compose logs --tail=100 kalin
```

### Monitoreo de recursos
```bash
# Uso de CPU/Memoria en tiempo real
docker stats kalin

# Información detallada
docker inspect kalin | grep -i memory
```

### Health checks
```bash
# Estado del health check
docker inspect --format='{{.State.Health.Status}}' kalin

# Ver logs del health check
docker inspect --format='{{json .State.Health}}' kalin | jq
```

---

## 🔄 ACTUALIZACIONES

### Actualización automática con Watchtower

Agrega a `docker-compose.yml`:
```yaml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 3600 --cleanup  # Revisar cada hora
    environment:
      - WATCHTOWER_NOTIFICATIONS=email
      - WATCHTOWER_NOTIFICATION_EMAIL_FROM=tu@email.com
```

### Actualización manual
```bash
# Pull nuevo código
git pull origin main

# Reconstruir imagen
docker-compose build --no-cache

# Recrear contenedor
docker-compose up -d

# Limpiar imágenes antiguas
docker image prune -f
```

---

## 🛡️ CHECKLIST DE SEGURIDAD DOCKER

Antes de desplegar en producción:

- [ ] Usuario no-root configurado (`USER kalin`)
- [ ] Puertos restringidos a localhost (`127.0.0.1:5000:5000`)
- [ ] API keys usando Docker Secrets (NO en variables de entorno)
- [ ] Reverse proxy con HTTPS configurado
- [ ] Recursos limitados (CPU/RAM)
- [ ] Health checks activos
- [ ] Volúmenes persistentes para datos importantes
- [ ] Logs centralizados y rotativos
- [ ] Firewall configurado (solo puertos necesarios)
- [ ] Docker actualizado a última versión
- [ ] Imágenes escaneadas por vulnerabilidades (`docker scan`)

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "Permission denied"
**Solución:**
```bash
# Asegurar que archivos tengan permisos correctos
sudo chown -R $USER:$USER .
docker-compose up -d
```

### Problema: "Port already in use"
**Solución:**
```bash
# Ver qué está usando el puerto 5000
netstat -tulpn | grep 5000

# Cambiar puerto en docker-compose.yml
ports:
  - "127.0.0.1:5001:5000"
```

### Problema: "Container keeps restarting"
**Solución:**
```bash
# Ver logs
docker logs kalin

# Verificar health check
docker inspect kalin | grep -A 10 Health

# Ejecutar en modo interactivo para debug
docker run -it --rm kalin bash
python run.py
```

### Problema: "Out of memory"
**Solución:**
```yaml
# Aumentar límite de memoria en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # Aumentar de 4G a 8G
```

---

## 📚 RECURSOS ADICIONALES

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Docker Security**: https://docs.docker.com/engine/security/
- **Best Practices**: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

---

## ✅ VERIFICACIÓN FINAL

Para verificar que tu despliegue Docker es seguro:

```bash
# 1. Verificar que no corre como root
docker exec kalin whoami
# Debería mostrar: kalin

# 2. Verificar puertos expuestos
docker port kalin
# Debería mostrar: 5000/tcp -> 127.0.0.1:5000

# 3. Verificar health check
docker inspect --format='{{.State.Health.Status}}' kalin
# Debería mostrar: healthy

# 4. Ejecutar auditoría de seguridad
docker exec kalin python security_audit.py

# 5. Verificar uso de recursos
docker stats kalin --no-stream
```

---

**🐳 Kalin v3.0 - Despliegue Enterprise con Docker**

*Aislado. Seguro. Escalable.*
