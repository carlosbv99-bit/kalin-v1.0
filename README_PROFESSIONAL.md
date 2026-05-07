# 🤖 Kalin v3.0 - Agente Autónomo de Desarrollo con IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Supported-green.svg)](https://ollama.ai/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

> **Sistema autónomo de desarrollo de software con inteligencia artificial multi-LLM, aprendizaje experiencial y validación inteligente de código.**

---

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Características Principales](#-características-principales)
- [Arquitectura](#-arquitectura)
- [Instalación Rápida](#-instalación-rápida)
- [Uso Básico](#-uso-básico)
- [Documentación Técnica](#-documentación-técnica)
- [Evaluación Técnica](#-evaluación-técnica)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🎯 Visión General

**Kalin** es un agente de desarrollo de software que combina la potencia de modelos de lenguaje locales (Ollama) con capacidades avanzadas de generación, reparación y análisis de código. Diseñado con un enfoque "privacy-first", permite ejecutar toda la inteligencia artificial en tu máquina local sin enviar datos a la nube.

### ¿Qué hace Kalin?

- 💻 **Genera código** desde descripciones en lenguaje natural
- 🔧 **Repara errores** automáticamente analizando y corrigiendo código
- 📊 **Analiza proyectos** completos identificando patrones y estructura
- 🧠 **Aprende de la experiencia** mejorando continuamente sus recomendaciones
- 🌐 **Soporta múltiples LLMs**: Ollama (local), OpenAI, Anthropic, Azure, HuggingFace

---

## ✨ Características Principales

### 1. Generación Inteligente de Código

```python
# Usuario escribe:
"ayúdame a crear un calendario en Python"

# Kalin genera:
import calendar
from datetime import date

def generar_calendario(anio=None, mes=None):
    if anio is None:
        anio = date.today().year
    if mes is None:
        mes = date.today().month
    cal = calendar.TextCalendar(firstweekday=6)
    return cal.formatmonth(anio, mes)

if __name__ == "__main__":
    print(generar_calendario())
```

**Características:**
- ✅ Detección automática del lenguaje solicitado
- ✅ Validación de calidad multi-capa
- ✅ Limpieza automática de comentarios innecesarios
- ✅ Reintentos inteligentes hasta obtener código válido
- ✅ Soporte para Python, HTML, JavaScript, TypeScript, Java, C++, y más

### 2. Reparación Automática de Errores

```bash
$ kalin /fix main.py
🔍 Analizando errores...
🛠️ Generando fix...
✅ Fix aplicado exitosamente
```

**Características:**
- Análisis profundo de errores de sintaxis y lógica
- Generación de diffs válidos (formato unificado)
- Aplicación segura de cambios
- Validación post-fix

### 3. Sistema de Aprendizaje Experiencial

```bash
$ kalin /experience
🧠 Memoria de Aprendizaje

📊 Experiencias totales: 47
✅ Éxitos: 35
❌ Fallos: 12
📈 Tasa de éxito global: 74.5%

🎯 Por tipo de tarea:
• create: 80.0% éxito (20 intentos)
• fix: 70.0% éxito (10 intentos)
• analyze: 88.9% éxito (9 intentos)

💡 Insights:
• Los fixes en archivos Python tienen mayor tasa de éxito
• La generación de HTML requiere más reintentos
```

**Características:**
- Almacenamiento persistente de todas las experiencias
- Detección automática de patrones exitosos/fallidos
- Recomendaciones basadas en historial
- Mejora continua con el uso

### 4. Debugging Profesional

```bash
$ export KALIN_DEBUG=1
$ python run.py

📤 [PROVIDER_MANAGER] PROMPT ENVIADO A OLLAMA:
================================================================================
Modelo: deepseek-coder:latest
Max tokens: 4000
Temperature: 0.2
Use case: create
--------------------------------------------------------------------------------
ROL: GENERADOR DE CÓDIGO PROFESIONAL...
```

**Características:**
- Modo debug configurable via variable de entorno
- Logging estructurado con timestamps
- Visibilidad completa de prompts y respuestas
- Performance tracking por request

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│          Frontend (Flask Web UI)            │
│         http://localhost:5000               │
└──────────────┬──────────────────────────────┘
               │ REST API
┌──────────────▼──────────────────────────────┐
│         Orchestrator / Executor             │
│   - Routing de intenciones                  │
│   - Gestión de estrategias                  │
│   - Coordinación de acciones                │
└──┬──────────┬──────────┬────────────────────┘
   │          │          │
┌──▼───┐  ┌──▼────┐  ┌──▼──────────┐
│Brain │  │Tools  │  │Strategies   │
│      │  │       │  │             │
│- Chat│  │- Fix  │  │- Python     │
│- Fix │  │- Scan │  │- Project    │
│- Create│ │- Apply│  │- Flutter    │
└──────┘  └───────┘  └─────────────┘
   │
┌──▼──────────────────────────────────┐
│        LLM Provider Manager         │
│  - Router inteligente               │
│  - Fallback dinámico                │
│  - Temperaturas por caso de uso     │
└──┬──────────┬──────────┬────────────┘
   │          │          │
┌──▼───┐  ┌──▼────┐  ┌──▼────────┐
│Ollama│  │OpenAI │  │Anthropic  │
│Local │  │Cloud  │  │Cloud      │
└──────┘  └───────┘  └───────────┘
```

### Componentes Clave

| Componente | Responsabilidad | Ubicación |
|------------|----------------|-----------|
| **Brain** | Detección de intenciones del usuario | `agent/core/brain.py` |
| **Executor** | Ejecución de acciones y routing | `agent/actions/executor.py` |
| **ProviderManager** | Gestión de proveedores LLM | `agent/llm/provider_manager.py` |
| **StateManager** | Persistencia de estado | `agent/core/state_manager.py` |
| **ExperienceMemory** | Sistema de aprendizaje | `agent/core/experience_memory.py` |
| **FixTool** | Generación y reparación de código | `agent/actions/tools/fix_tool.py` |

---

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.8 o superior
- Ollama instalado (para modo local): https://ollama.ai/
- Git

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/carlosbv99/kalin.git
cd kalin
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Ollama

```bash
# Descargar modelo recomendado
ollama pull deepseek-coder:latest

# Iniciar servidor Ollama
ollama serve
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tu configuración
nano .env
```

**.env mínimo requerido:**
```env
OLLAMA_MODEL=deepseek-coder:latest
KALIN_MODE=local
```

### Paso 5: Ejecutar Kalin

```bash
python run.py
```

Accede a la interfaz web en: **http://localhost:5000**

---

## 💻 Uso Básico

### Interfaz Web

Una vez iniciado el servidor, abre tu navegador en `http://localhost:5000` y comienza a chatear con Kalin.

### Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/create` | Generar código nuevo | `/create calendario en Python` |
| `/fix` | Reparar archivo | `/fix main.py` |
| `/scan` | Escanear proyecto | `/scan` |
| `/analyze` | Analizar archivo | `/analyze utils.py` |
| `/setpath` | Configurar ruta proyecto | `/setpath /mi/proyecto` |
| `/experience` | Ver estadísticas aprendizaje | `/experience` |
| `/learn` | Ver patrones aprendidos | `/learn` |

### Ejemplos de Uso

#### Generar Código

```
Usuario: ayúdame a crear una función que calcule Fibonacci
Kalin: [Genera código Python limpio y validado]
```

#### Reparar Errores

```
Usuario: /fix app.py
Kalin: 🔍 Analizando app.py...
       🛠️ Generando fix...
       ✅ Fix aplicado: 3 errores corregidos
```

#### Ver Experiencia

```
Usuario: /experience
Kalin: 🧠 Memoria de Aprendizaje
       📊 47 experiencias, 74.5% tasa de éxito
       💡 Insight: Fixes en Python tienen 85% éxito
```

---

## 📚 Documentación Técnica

### Guías Principales

- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Resumen ejecutivo del proyecto
- **[PREPARACION_EVALUACION.md](PREPARACION_EVALUACION.md)** - Guía completa para evaluación técnica
- **[CHECKLIST_EVALUACION.txt](CHECKLIST_EVALUACION.txt)** - Checklist imprimible para evaluadores
- **[GUIA_USUARIO.md](GUIA_USUARIO.md)** - Guía detallada de usuario
- **[ARQUITECTURA_IMPLEMENTADA.md](ARQUITECTURA_IMPLEMENTADA.md)** - Documentación de arquitectura
- **[TEMPERATURAS_POR_CASO_DE_USO.md](TEMPERATURAS_POR_CASO_DE_USO.md)** - Sistema de temperaturas LLM

### Documentación Adicional

- **[DEPLOYMENTS.md](DEPLOYMENTS.md)** - Guía de despliegue
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Despliegue con Docker
- **[GUIA_MULTIPLES_LLMS.md](GUIA_MULTIPLES_LLMS.md)** - Configuración multi-LLM
- **[SECURITY.md](SECURITY.md)** - Consideraciones de seguridad

---

## 🔍 Evaluación Técnica

Este proyecto está preparado para evaluación técnica por especialistas. Se han generado los siguientes documentos:

### 📄 Para Evaluadores

1. **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)**
   - Visión general del proyecto
   - Arquitectura y decisiones de diseño
   - Métricas y estado actual
   - Roadmap y próximos pasos

2. **[PREPARACION_EVALUACION.md](PREPARACION_EVALUACION.md)**
   - Checklist de preparación completado
   - Áreas para revisión profunda
   - Fortalezas y debilidades conocidas
   - Notas contextuales para evaluadores

3. **[CHECKLIST_EVALUACION.txt](CHECKLIST_EVALUACION.txt)**
   - Checklist imprimible de 10 secciones
   - Evaluación de arquitectura, código, seguridad, performance
   - Espacio para comentarios y calificaciones
   - Formato profesional para firma

### 🧪 Ejecutar Script de Preparación

```bash
python prepare_for_review.py
```

Este script:
- ✅ Verifica sintaxis de todos los módulos principales
- ✅ Genera estadísticas del proyecto
- ✅ Identifica áreas de mejora
- ✅ Confirma que el proyecto está listo para evaluación

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines detalladas.

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crea** una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la branch (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

### Áreas que Necesitan Ayuda

- 🔴 **Tests Unitarios**: Implementar pytest con cobertura >80%
- 🟡 **CI/CD Pipeline**: GitHub Actions para tests automáticos
- 🟡 **API Documentation**: Swagger/OpenAPI specs
- 🟢 **Performance**: Optimizar tiempos de respuesta
- 🟢 **Security**: Implementar authentication y rate limiting

---

## 📊 Estado del Proyecto

| Componente | Estado | Completado |
|------------|--------|------------|
| Core Engine | ✅ Stable | 95% |
| LLM Integration | ✅ Stable | 90% |
| Experience Memory | ✅ Stable | 85% |
| Web Interface | ✅ Stable | 80% |
| Tests | ⚠️ In Progress | 40% |
| CI/CD | ❌ Pending | 0% |
| API Docs | ❌ Pending | 0% |
| Security Hardening | ⚠️ In Progress | 50% |

---

## 📄 Licencia

Distribuido bajo la MIT License. Ver [LICENSE](LICENSE) para más información.

---

## 🙏 Agradecimientos

- **[Ollama](https://ollama.ai/)** - Framework para ejecutar LLMs localmente
- **[DeepSeek](https://deepseek.ai/)** - Modelo de código de alta calidad
- **[Flask](https://flask.palletsprojects.com/)** - Framework web ligero
- **Comunidad Open Source** - Por herramientas y bibliotecas increíbles

---

## 📞 Contacto

- **GitHub**: [@carlosbv99](https://github.com/carlosbv99)
- **Issues**: [Reportar bugs](https://github.com/carlosbv99/kalin/issues)
- **Discussions**: [Preguntas y ideas](https://github.com/carlosbv99/kalin/discussions)

---

<div align="center">

**Hecho con ❤️ para la comunidad de desarrolladores**

[⬆ Volver arriba](#-kalin-v30---agente-autónomo-de-desarrollo-con-ia)

</div>
