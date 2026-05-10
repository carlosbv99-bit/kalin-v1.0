# 🤖 Kalin v3.0 - Agente Autónomo de Desarrollo con IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Supported-green.svg)](https://ollama.ai/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

> **Sistema autónomo de desarrollo de software con inteligencia artificial multi-LLM, aprendizaje experiencial y validación inteligente de código.**

---

## ⚡ Quick Start

```bash
# Clonar repositorio
git clone https://github.com/carlosbv99/kalin.git
cd kalin

# Instalar dependencias
pip install -r requirements.txt

# Configurar Ollama
ollama pull deepseek-coder:latest
ollama serve

# Ejecutar Kalin
python run.py
```

Accede a: **http://localhost:5000**

---

## 📚 Documentación Completa

**Para documentación detallada, ver:**
- **[README_PROFESSIONAL.md](README_PROFESSIONAL.md)** - Documentación completa del proyecto
- **[GUIA_USUARIO.md](GUIA_USUARIO.md)** - Guía de usuario

---

## 🔍 Evaluación Técnica

Este proyecto está preparado para evaluación técnica profesional.

**Documentos para evaluadores:**
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Visión general y arquitectura
- **[PREPARACION_EVALUACION.md](PREPARACION_EVALUACION.md)** - Guía de preparación
- **[CHECKLIST_EVALUACION.txt](CHECKLIST_EVALUACION.txt)** - Checklist imprimible
- **[EVALUACION_COMPLETADA.md](EVALUACION_COMPLETADA.md)** - Resumen de preparación

**Ejecutar script de preparación:**
```bash
python prepare_for_review.py
```

---

## ✨ Características Principales

- 💻 **Generación de código** desde lenguaje natural
- 🔧 **Reparación automática** de errores
- 📊 **Análisis de proyectos** completos
- 🧠 **Aprendizaje experiencial** continuo
- 🌐 **Multi-LLM**: Ollama, OpenAI, Anthropic, Azure, HuggingFace
- 🔒 **Privacy-first**: Ejecución 100% local opcional

---

## 🛠️ Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/create` | Generar código nuevo |
| `/fix` | Reparar archivo |
| `/scan` | Escanear proyecto |
| `/analyze` | Analizar archivo |
| `/setpath` | Configurar ruta |
| `/experience` | Ver estadísticas |
| `/learn` | Ver patrones |

---

## 📊 Estado del Proyecto

| Componente | Estado |
|------------|--------|
| Core Engine | ✅ Stable |
| LLM Integration | ✅ Stable |
| Experience Memory | ✅ Stable |
| Web Interface | ✅ Stable |
| Tests | ✅ Complete |
| CI/CD | ❌ Pending |

---

## 📁 Estructura del Proyecto

```
kalin/
├── agent/              # Núcleo del agente IA
│   ├── core/           # Componentes principales
│   ├── llm/            # Integraciones con LLMs
│   ├── actions/        # Acciones y herramientas
│   └── templates/      # Plantillas de prompts
├── app/                # Aplicación Android (Flutter)
├── static/             # Archivos estáticos web
├── templates/          # Plantillas HTML
├── tests/              # Suite de pruebas
├── .env.example        # Variables de entorno de ejemplo
├── requirements.txt    # Dependencias Python
├── run.py             # Punto de entrada principal
└── web.py             # Servidor Flask
```

---

## 🔒 Seguridad

- ✅ No se incluyen credenciales en el repositorio
- ✅ Archivo `.env` excluido vía `.gitignore`
- ✅ Variables de entorno para configuración sensible
- ✅ Auditoría de seguridad implementada

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

<div align="center">

**Hecho con ❤️ para la comunidad de desarrolladores**

[⬆ Volver arriba](#-kalin-v30---agente-autónomo-de-desarrollo-con-ia)

</div>