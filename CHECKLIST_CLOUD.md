"""
CHECKLIST: ANTES DE SUBIR A CLOUD
==================================

Pasos necesarios para escalar de local a cloud.

✅ = Hecho
⏳ = Por hacer

PARTE 1: ARQUITECTURA LLM (HECHA)
=================================

✅ Interfaz abstracta de proveedores (BaseLLMProvider)
✅ Implementación Ollama
✅ Implementación OpenAI
✅ Implementación Anthropic
✅ Provider Manager (routing + fallbacks)
✅ Configuración centralizada (LLMConfig)
✅ Client backward compatible
✅ Estadísticas y billing
✅ Testing de múltiples providers

🎯 RESULTADO: Puedes cambiar de Ollama → OpenAI sin tocar código

PARTE 2: CONFIGURACIÓN Y SECRETS
================================

⏳ Crear .env.local (desarrollo)
⏳ Crear .env.production (cloud)
⏳ Solicitar API keys (OpenAI, Anthropic)
⏳ Configurar environment variables en cloud

Pasos:

1. Copiar .env.example a .env.local:
   cp .env.example .env.local
   
   Editar:
   KALIN_MODE=local
   OLLAMA_ENDPOINT=http://127.0.0.1:11434

2. Solicitar API keys (toma 5-10 minutos):
   
   OpenAI:
   - Ir a https://platform.openai.com/api-keys
   - Crear API key
   - Guardar en OPENAI_API_KEY
   
   Anthropic:
   - Ir a https://console.anthropic.com/
   - Crear API key
   - Guardar en ANTHROPIC_API_KEY

3. Crear .env.production:
   cp .env.example .env.production
   
   Editar:
   KALIN_MODE=cloud
   OPENAI_API_KEY=sk-proj-xxxxx
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   OLLAMA_ENDPOINT=http://internal-ollama:11434  # Si tienes

4. En cloud:
   - NO comitear .env (agregar a .gitignore)
   - Usar Secret Management (Azure Key Vault, AWS Secrets, etc.)
   - Variables de entorno en deployment

PARTE 3: TESTING LOCAL
======================

⏳ Pruebar que todo funciona offline (Ollama)
⏳ Pruebar fallbacks (simular fallos)
⏳ Pruebar costos (si habilitas OpenAI)

Pasos:

1. Verificar Ollama está corriendo:
   curl http://127.0.0.1:11434/api/tags

2. Ejecutar tests:
   python test_llm_providers.py

3. Probar generate() directamente:
   
   python -c "
   from agent.llm.client import generate
   print(generate('test', max_tokens=50))
   "

4. Ver estadísticas:
   
   python -c "
   from agent.llm.client import get_stats, get_provider_status
   print(get_provider_status())
   print(get_stats())
   "

PARTE 4: INTEGRACIÓN EN CLOUD
=============================

⏳ Documentar proceso de deployment
⏳ Crear Dockerfile (si no existe)
⏳ Crear docker-compose.yml (prod)
⏳ Crear Kubernetes manifests (si aplica)

Pasos:

1. Dockerfile:
   - Base Python 3.9+
   - COPY agent/
   - pip install -r requirements.txt
   - CMD python main.py

2. docker-compose.yml (prod):
   - Servicio agente
   - Environment variables
   - Health checks
   - Recursos límites

3. Deployment:
   - Azure Container Registry (ACR)
   - Azure App Service O Azure AKS
   - O AWS ECR + ECS
   - O Render.com / Railway.app (más simple)

PARTE 5: MONITORING Y COSTOS
============================

⏳ Configurar alertas de costos
⏳ Logging de cada generación
⏳ Dashboard de usage

Pasos:

1. Habilitar logging en cloud:
   
   .env:
   LOG_LEVEL=INFO
   LOG_COSTS=true

2. Agregar endpoint de monitoreo:
   
   GET /debug/stats → Retorna:
   {
       "total_requests": 1000,
       "total_cost": "$45.00",
       "provider_usage": {"openai": 800, "anthropic": 200},
       "uptime": 99.95%
   }

3. Configurar alertas:
   - Si costo > $100/día
   - Si uptime < 99%
   - Si errores > 1%

PARTE 6: OPTIMIZACIÓN DE COSTOS
===============================

⏳ Revisar routing por use_case
⏳ Implementar caching si necesario
⏳ A/B testing de modelos

Pasos:

1. Revisar USE_CASE_ROUTER:
   
   En config.py:
   USE_CASE_ROUTER = {
       "fix": {"primary": "openai"},      # Caro pero bueno
       "test": {"primary": "huggingface"}, # Barato
       "doc": {"primary": "huggingface"},  # Barato
   }

2. Considerar modelo más barato:
   
   OpenAI GPT-4:     $0.03/1K tokens
   OpenAI GPT-3.5:   $0.0005/1K tokens (100x más barato)
   Claude 3 Opus:    $0.015/1K tokens
   Claude 3 Haiku:   $0.00025/1K tokens (10x barato)

3. Si presupuesto es limitado:
   
   /fix, /create → GPT-3.5 (bueno y barato)
   /test, /doc → Llama 2 (muy barato)
   Fallback siempre disponible

PARTE 7: SEGURIDAD
==================

⏳ No comitear API keys
⏳ Usar Azure Key Vault / AWS Secrets Manager
⏳ Auditar acceso a logs
⏳ Rate limiting por usuario

Pasos:

1. .gitignore:
   .env
   .env.*.local
   *.log
   secrets/

2. En cloud, usar Secret Management:
   - Azure Key Vault
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets

3. Rate limiting:
   MAX_REQUESTS_PER_MINUTE=100
   MAX_REQUESTS_PER_USER=10

4. Auditing:
   - Log cada generación
   - Quién llamó (user ID)
   - Costo total
   - Resultado (éxito/fallo)

PARTE 8: TESTING EN PRODUCCIÓN
==============================

⏳ Smoke tests antes de deployment
⏳ Canary deployment (5% → 50% → 100%)
⏳ Rollback plan si falla

Pasos:

1. Smoke test:
   GET /health
   POST /chat {"mensaje": "/fix test.py"}
   GET /debug/stats

2. Gradual rollout:
   - Día 1: 5% del tráfico
   - Día 2: 25% del tráfico
   - Día 3: 100% del tráfico

3. Rollback:
   git revert <commit>
   docker push rollback-image
   Redeploy versión anterior

PARTE 9: DOCUMENTACIÓN
======================

✅ GUIA_MULTIPLES_LLMS.md (cómo usar)
✅ DEPLOYMENTS.md (cómo desplegar)
✅ ESCALABILIDAD_LLMS_RESUMEN.md (resumen)

⏳ Documentación interna del equipo
⏳ Runbook de incidentes
⏳ Guía de escalado

PARTE 10: OPERACIÓN
===================

⏳ Monitoreo 24/7 (opcional)
⏳ Alertas en Slack/Email
⏳ Backup de logs
⏳ Reporte mensual de costos

Dashboard recomendado:
- Datadog / New Relic / CloudWatch
- Métricas:
  * Requests/min
  * Latencia (p50, p95, p99)
  * Error rate
  * Costo por request
  * Provider distribution

CRONOGRAMA SUGERIDO
===================

Día 1: Parte 1-3
  - Verificar arquitectura local
  - Ejecutar tests
  - Probar offline

Día 2-3: Parte 4-5
  - Setup cloud (Azure/AWS)
  - Configurar secrets
  - Deploy staging

Día 4: Parte 6-7
  - Optimize costos
  - Security review
  - Checklist seguridad

Día 5: Parte 8-9
  - Testing en staging
  - Documentación final
  - Runbooks

Día 6: Go-live
  - Canary: 5%
  - Monitor 2 horas
  - Expand 50%
  - Monitor 2 horas
  - Expand 100%

DESPACHÉ FINAL
==============

Antes de hacer Deploy en Producción, verifica:

Arquitectura:
  ✅ Múltiples proveedores funcionan
  ✅ Fallbacks automáticos probados
  ✅ Stats y costos trackeados

Configuración:
  ✅ .env.production configurado
  ✅ API keys en Secret Management
  ✅ No hay secretos en código

Cloud:
  ✅ Dockerfile builds correctamente
  ✅ docker-compose.yml usa variables
  ✅ Health checks configurados

Testing:
  ✅ Funciona offline (Ollama)
  ✅ Funciona con OpenAI
  ✅ Funciona con fallback
  ✅ Costos dentro de budget

Seguridad:
  ✅ Rate limiting ON
  ✅ Audit logging ON
  ✅ Secrets en vault
  ✅ .gitignore completo

Monitoreo:
  ✅ Dashboard configurado
  ✅ Alertas en Slack
  ✅ Runbook de incidentes
  ✅ Escalation plan

Documentación:
  ✅ Equipo sabe cómo operar
  ✅ Runbooks actualizados
  ✅ Handoff documentation
  ✅ Incident response plan

SI TODO ESTÁ ✅: LISTO PARA PRODUCTION 🚀

PREGUNTAS COMUNES
=================

P: ¿Qué pasa si falla OpenAI?
R: Automáticamente intenta Anthropic, luego Ollama (si lo tienes).

P: ¿Cuánto cuesta?
R: Ollama $0. OpenAI ~$15/1000 requests. Anthropic ~$7.50.

P: ¿Puedo usar solo Ollama en cloud?
R: Sí, pero más lento. Recomendamos OpenAI primario + Ollama fallback.

P: ¿Necesito cambiar mi código?
R: NO. generate() funciona igual que antes.

P: ¿Cómo monitoreo costos?
R: GET /debug/stats muestra total_cost. Configura alertas.

P: ¿Qué modelo debería usar?
R: Development: deepseek-coder (Ollama)
   Production /fix: gpt-4-turbo (mejor análisis)
   Production /test: gpt-3.5 (más barato, bueno)

P: ¿Puedo usar múltiples regions?
R: Sí. Ver DEPLOYMENTS.md para multi-región setup.

RECURSOS
========

- Guía completa: GUIA_MULTIPLES_LLMS.md
- Deployments: DEPLOYMENTS.md
- Resumen: ESCALABILIDAD_LLMS_RESUMEN.md
- Testing: test_llm_providers.py

¡Listo para escalar a cloud! 🚀
"""

print(__doc__)
