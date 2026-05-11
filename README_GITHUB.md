# Kalin AI - Asistente de Programación Conversacional

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/carlosbv99/kalin/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/carlosbv99/kalin/actions/workflows/ci-cd.yml)
[![Tests](https://img.shields.io/badge/Tests-60%20unitarios-brightgreen.svg)](tests/)

Kalin AI es un **IDE conversacional** que permite generar, modificar y gestionar código mediante chat natural. Utiliza un sistema avanzado de parches incrementales para mantener la integridad del código mientras evoluciona el proyecto.

## ✨ Características Principales

### 🤖 Interfaz Conversacional
- Chat natural para crear y modificar código
- Soporte multi-lenguaje (HTML, CSS, Python, JavaScript, Java, C/C++)
- Preview en tiempo real para código web
- Terminal integrado para ejecución de comandos

### 🔧 Sistema de Parches Inteligente
- Modificaciones incrementales sin regenerar archivos completos
- Versionado interno con snapshots automáticos
- Undo/Redo completo de cambios
- Historial detallado de todas las modificaciones
- Regiones protegidas (locks semánticos)

### 🎯 Bloqueo de Lenguaje por Sesión
- Mantiene consistencia de lenguaje durante toda la sesión
- Prevención automática de cambios de lenguaje no deseados
- Detección inteligente de contexto

### 🛡️ Seguridad y Estabilidad
- Sandbox seguro para ejecución de código
- Validación de inputs y sanitización
- Health monitoring automático
- Manejo robusto de errores

### 💾 Gestión de Memoria
- Memoria conversacional persistente
- Contexto selectivo optimizado
- Experiencia acumulativa (aprendizaje continuo)

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.11 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/carlosbv99/kalin.git
cd kalin
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tu configuración (API keys, modelo, etc.)
```

4. **Ejecutar Kalin:**
```bash
python main.py
```

5. **Abrir navegador:**
```
http://127.0.0.1:5000
```

## 📖 Uso Básico

### Crear Código
```
Usuario: "crea un cuadrado rojo en html"
Kalin: [Genera código HTML]
```

### Modificar Código
```
Usuario: "agrega un círculo amarillo a la derecha"
Kalin: [Aplica parche manteniendo código anterior]
```

### Deshacer Cambios
- Menú **Herramientas** → **Deshacer último cambio** (Ctrl+Z)

### Ver Historial
- Menú **Ver** → **Visualizador de diffs**

## 🏗️ Arquitectura

```
kalin/
├── agent/                  # Núcleo del agente
│   ├── core/              # Componentes principales
│   │   ├── orchestration_layer.py  # Capa de orquestación
│   │   ├── patch_manager.py        # Sistema de parches
│   │   ├── memory_manager.py       # Gestión de memoria
│   │   └── ...
│   ├── llm/               # Clientes de LLM
│   └── actions/           # Acciones del agente
├── static/                # Frontend (JS, CSS)
├── templates/             # Templates HTML
├── tests/                 # Tests unitarios
├── main.py               # Punto de entrada
└── web.py                # Servidor Flask
```

## 🔌 Proveedores LLM Soportados

- **Groq** (recomendado) - Llama 3.1, Mixtral
- **Ollama** - Modelos locales (DeepSeek, CodeLlama)
- **OpenAI** - GPT-3.5, GPT-4
- **Anthropic** - Claude

Configura el proveedor activo en `.env`:
```env
ACTIVE_PROVIDER=groq
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

## 📊 Características Técnicas

### Sistema de Parches
- **Operaciones**: INSERT, DELETE, REPLACE, APPEND, PREPEND
- **Ubicación inteligente**: Anchor text, regex patterns, line numbers
- **Validación**: Regiones protegidas, detección de conflictos
- **Snapshots**: Versionado automático antes de cada cambio

### Optimización de Tokens
- Generación incremental (solo fragmentos nuevos)
- Contexto selectivo (solo archivos relevantes)
- Prompts dinámicos adaptados a la intención
- **Ahorro**: ~90% menos tokens vs regeneración completa

### Trazabilidad Completa
- Historial de todos los cambios
- Metadata rica (timestamp, descripción, operación)
- Reversión instantánea a cualquier punto
- Auditoría completa del proyecto

## 🧪 Testing

### Suite Completa de Tests

El proyecto incluye **60 tests unitarios** que cubren el core del agente:

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con script especializado (recomendado)
python run_all_tests.py --coverage --html-report
```

### Tests Disponibles

- ✅ `test_patch_manager.py` - Sistema de parches (15 tests)
- ✅ `test_orchestration_layer.py` - Capa de orquestación (25 tests)
- ✅ `test_memory_manager.py` - Gestor de memoria (20 tests)
- ✅ `test_general_workflow.py` - Flujo completo
- ✅ `test_memoria_contextual.py` - Memoria conversacional
- ✅ `test_flow_and_functionality.py` - Funcionalidades básicas

### CI/CD Automatizado

Cada push o pull request ejecuta automáticamente:
- 🧪 Tests unitarios (Python 3.11 y 3.12)
- 🔍 Análisis estático (Flake8, Black, Pylint, MyPy)
- 🛡️ Escaneo de seguridad (Bandit, Safety)
- 📊 Reporte de cobertura (Codecov)
- 🐳 Build Docker (en main)

Ver `.github/workflows/ci-cd.yml` para detalles.

## 🐳 Docker (Opcional)

```bash
docker-compose up -d
```

Acceder a `http://localhost:5000`

## 📝 Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Punto de entrada principal |
| `web.py` | Servidor Flask y endpoints API |
| `requirements.txt` | Dependencias Python |
| `.env.example` | Template de configuración |
| `README_GITHUB.md` | Esta documentación |

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👤 Autor

**Carlos BV**
- GitHub: [@carlosbv99](https://github.com/carlosbv99)

## 🙏 Agradecimientos

- Groq por el acceso a modelos LLM de alta velocidad
- Flask por el framework web
- La comunidad open source

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/carlosbv99/kalin/issues)
- **Email**: carlosbv99@example.com

---

⭐ **Si este proyecto te fue útil, considera darle una estrella!**
