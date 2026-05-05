"""
DEPLOYMENTS: Configuraciones predefinidas para diferentes entornos

Copy-paste según tu entorno.
"""

# ==============================================================================
# DESARROLLO LOCAL
# ==============================================================================
"""
Descripción: Máquina local, modelo Ollama, gratis, offline
Usado por: Desarrolladores, testing

Requisitos:
- Ollama instalado y corriendo
- No necesita internet
- No necesita claves API

Archivo: .env.local
"""

DEVELOPMENT_CONFIG = """
# Desarrollo
KALIN_MODE=local
OLLAMA_ENDPOINT=http://127.0.0.1:11434
OLLAMA_MODEL=deepseek-coder

# Sin conexión a providers cloud
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
"""

# ==============================================================================
# STAGING (Pruebas en servidor)
# ==============================================================================
"""
Descripción: Servidor de pruebas, múltiples LLMs, con fallbacks
Usado por: QA, testing antes de producción

Requisitos:
- OpenAI API key (para testing)
- Ollama también en el servidor (fallback)

Archivo: .env.staging
"""

STAGING_CONFIG = """
# Staging
KALIN_MODE=cloud
OPENAI_API_KEY=sk-proj-staging-key
OPENAI_MODEL=gpt-4-turbo
ANTHROPIC_API_KEY=sk-ant-staging-key
OLLAMA_ENDPOINT=http://localhost:11434  # Fallback

# Límites de costos para testing
MAX_MONTHLY_COST=100  # $100/mes máximo
"""

# ==============================================================================
# PRODUCCIÓN TIER 1 (Alto volumen, máxima calidad)
# ==============================================================================
"""
Descripción: Producción empresarial, múltiples LLMs, billing integrado
Usado por: Usuarios pagantes, aplicaciones críticas

Requisitos:
- OpenAI API key con alta cuota
- Anthropic API key como fallback
- Ollama en servidor opcional

Características:
- OpenAI primario (mejor análisis)
- Fallback a Anthropic
- Tracking detallado de costos
- Rate limiting
"""

PRODUCTION_TIER1_CONFIG = """
# Producción Tier 1
KALIN_MODE=cloud
OPENAI_API_KEY=sk-proj-prod-key
OPENAI_MODEL=gpt-4-turbo
ANTHROPIC_API_KEY=sk-ant-prod-key
ANTHROPIC_MODEL=claude-3-5-sonnet

# Fallback local si tienes servidor con Ollama
OLLAMA_ENDPOINT=http://internal-ollama:11434

# Rate limiting
MAX_REQUESTS_PER_MINUTE=100
MAX_MONTHLY_COST=10000

# Logging
LOG_LEVEL=WARNING
LOG_COSTS=true
"""

# ==============================================================================
# PRODUCCIÓN TIER 2 (Optimizado para costos)
# ==============================================================================
"""
Descripción: Producción optimizada para presupuesto
Usado por: Aplicaciones con volumen pero presupuesto limitado

Características:
- HuggingFace primario (10x más barato)
- OpenAI como fallback (mejor calidad si presupuesto lo permite)
- Ollama como último fallback
"""

PRODUCTION_TIER2_CONFIG = """
# Producción Tier 2 (cost-optimized)
KALIN_MODE=cloud
HF_API_KEY=hf_prod_key
HF_MODEL=meta-llama/Llama-2-70b-chat-hf
OPENAI_API_KEY=sk-proj-prod-key
OPENAI_MODEL=gpt-4-turbo
OLLAMA_ENDPOINT=http://internal-ollama:11434

# Presupuesto limitado
MAX_MONTHLY_COST=1000  # $1000/mes

# Log de costos
LOG_COSTS=true
"""

# ==============================================================================
# PRODUCCIÓN MULTI-REGIÓN (Global)
# ==============================================================================
"""
Descripción: Múltiples regiones para latencia baja + cumplimiento
Usado por: Aplicaciones globales con requisitos de data residency

Características:
- OpenAI USA
- Anthropic UE (GDPR)
- Ollama China/Latinoamérica (no bloqueado)
"""

PRODUCTION_MULTIREGION_CONFIG = """
# Producción Multi-región

# USA
REGION_US_PROVIDER=openai
REGION_US_API_KEY=sk-proj-us-key

# EU (GDPR)
REGION_EU_PROVIDER=anthropic
REGION_EU_API_KEY=sk-ant-eu-key

# Asia
REGION_ASIA_PROVIDER=ollama
REGION_ASIA_ENDPOINT=http://asia-ollama:11434

# Latinoamérica
REGION_LATAM_PROVIDER=ollama
REGION_LATAM_ENDPOINT=http://latam-ollama:11434

# Fallback global
FALLBACK_PROVIDER=openai
"""

# ==============================================================================
# ENTERPRISE (Máxima control, máxima seguridad)
# ==============================================================================
"""
Descripción: Enterprise con modelo privado
Usado por: Corporaciones grandes, datos sensibles

Requisitos:
- Modelo Ollama privado en servidor on-premise
- Sin enviar datos a cloud
- Cumplimiento: HIPAA, PCI-DSS, SOC2, etc.

Características:
- Solo Ollama on-premise
- Audit logging
- Air-gap capable
"""

ENTERPRISE_CONFIG = """
# Enterprise (on-premise only)
KALIN_MODE=local
OLLAMA_ENDPOINT=https://internal-ollama.corp.com:11434
OLLAMA_MODEL=custom-model-v1-7b

# Audit
AUDIT_LOG=true
AUDIT_LOG_PATH=/var/log/agente/audit.log

# Seguridad
REQUIRE_SSL=true
SSL_CERT=/etc/ssl/certs/agente.crt
SSL_KEY=/etc/ssl/private/agente.key

# Sin cloud providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
"""

# ==============================================================================
# DOCKER COMPOSE PARA LOCAL DEV
# ==============================================================================

DOCKER_COMPOSE_LOCAL = """
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      OLLAMA_MODELS: /root/.ollama/models
    command: serve

  agente:
    build: .
    ports:
      - "5000:5000"
    environment:
      KALIN_MODE: local
      OLLAMA_ENDPOINT: http://ollama:11434
    depends_on:
      - ollama
    volumes:
      - ./projects:/agente/projects

volumes:
  ollama_data:
"""

# ==============================================================================
# DOCKER COMPOSE PARA CLOUD PROD
# ==============================================================================

DOCKER_COMPOSE_PROD = """
version: '3.8'

services:
  agente:
    image: mi-registro.azurecr.io/agente:latest
    ports:
      - "5000:5000"
    environment:
      KALIN_MODE: cloud
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      LOG_LEVEL: WARNING
      LOG_COSTS: "true"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
"""

# ==============================================================================
# KUBERNETES PARA CLOUD PROD
# ==============================================================================

K8S_DEPLOYMENT = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: agente-config
data:
  agente_mode: "cloud"
  log_level: "WARNING"
  log_costs: "true"

---
apiVersion: v1
kind: Secret
metadata:
  name: agente-secrets
type: Opaque
stringData:
  openai_api_key: sk-proj-xxxxx
  anthropic_api_key: sk-ant-xxxxx

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agente
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: agente
  template:
    metadata:
      labels:
        app: agente
    spec:
      containers:
      - name: agente
        image: mi-registro.azurecr.io/agente:latest
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: agente-config
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agente-secrets
              key: openai_api_key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: agente-secrets
              key: anthropic_api_key
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: agente-service
spec:
  selector:
    app: agente
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
"""

print(__doc__)
