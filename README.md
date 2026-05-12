# 🤖 Kalin AI - IDE Inteligente con Asistente de Código

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v1.1-orange.svg)]()

## 📋 Descripción

**Kalin AI** es un entorno de desarrollo integrado (IDE) inteligente basado en web que combina un editor de código avanzado con un asistente de IA conversacional. Permite a los desarrolladores generar, modificar y visualizar código en tiempo real mediante interacciones naturales en lenguaje humano.

### ✨ Características Principales

- **🧠 Asistente de IA Conversacional**: Chat integrado que entiende contexto y genera código automáticamente
- **📝 Editor de Código Avanzado**: Resaltado de sintaxis, numeración de líneas, auto-indentación y múltiples pestañas
- **👁️ Vista Previa en Tiempo Real**: Renderizado instantáneo de HTML/CSS/JavaScript con sandbox seguro
- **🔄 Paneles Redimensionables**: Layout flexible con paneles arrastrables ultra-finios (1px)
- **💾 Gestión de Archivos**: Árbol de archivos interactivo con soporte multi-lenguaje
- **🎯 Detección Inteligente de Lenguajes**: Bloqueo automático de contexto por lenguaje
- **🔒 Seguridad**: CSP estricta, sandbox de iframe, validación de contenido
- **🌐 Multi-Proveedor LLM**: Soporte para Ollama, Groq, OpenAI, Xiaomi MiMo y más
- **💭 Memoria Contextual**: Historial conversacional persistente con compresión inteligente
- **⚡ Parches Incrementales**: Sistema de aplicación de cambios sin regenerar código completo

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8 o superior
- Navegador web moderno (Chrome, Firefox, Edge)
- (Opcional) Ollama para modelos locales

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/kalin.git
cd kalin

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env con tus API keys si usas modelos en la nube

# 4. Iniciar el servidor
python run.py

# 5. Abrir en navegador
# http://localhost:5000
```

### Uso Básico

1. **Generar código**: Escribe en el chat "crea una página web sencilla"
2. **Modificar código**: "cambia el título a 'Mi Página'"
3. **Editar manualmente**: Haz clic en el editor y escribe directamente
4. **Ver preview**: El panel central muestra el resultado automáticamente

---

## 🏗️ Arquitectura del Proyecto

```
kalin/
├── agent/                  # Núcleo del agente de IA
│   ├── core/              # Componentes principales
│   │   ├── orchestration_layer.py    # Orquestación de intenciones
│   │   ├── conversation_memory.py    # Memoria conversacional
│   │   ├── conversation_manager.py   # Gestión de sesiones
│   │   ├── context_manager.py        # Contexto del proyecto
│   │   └── patch_manager.py          # Sistema de parches
│   ├── llm/               # Proveedores de modelos
│   │   ├── ollama_provider.py
│   │   ├── groq_provider.py
│   │   └── openai_provider.py
│   └── actions/           # Acciones ejecutables
├── static/                # Recursos frontend
│   ├── js/                # Módulos JavaScript
│   │   ├── app.js                 # Aplicación principal
│   │   ├── code-editor.js         # Editor de código
│   │   ├── chat.js                # Sistema de chat
│   │   ├── preview.js             # Renderizado de preview
│   │   ├── resizable-panels.js    # Paneles redimensionables
│   │   └── sidebar-functions.js   # Funciones del sidebar
│   └── css/               # Estilos CSS
├── templates/             # Plantillas HTML
│   └── index.html         # Interfaz principal
├── sessions/              # Persistencia de sesiones
├── logs/                  # Logs del sistema
├── experience_memory/     # Memoria de experiencias
├── tests/                 # Suite de pruebas
├── plugins/               # Plugins extensibles
├── run.py                 # Punto de entrada principal
├── web.py                 # Servidor Flask
├── requirements.txt       # Dependencias Python
└── README.md              # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+**: Lenguaje principal
- **Flask 2.0+**: Framework web ligero
- **Requests**: Cliente HTTP para APIs
- **Logging**: Sistema de logs estructurado

### Frontend
- **HTML5/CSS3**: Estructura y estilos
- **JavaScript (Vanilla)**: Lógica del cliente (sin frameworks)
- **Iframe Sandbox**: Renderizado seguro de previews

### IA/LLM
- **Ollama**: Modelos locales (Qwen2.5-Coder, Llama, etc.)
- **Groq API**: Inferencia rápida en la nube
- **OpenAI GPT**: Modelos propietarios
- **Xiaomi MiMo**: Modelo alternativo gratuito

### Almacenamiento
- **JSON**: Persistencia de sesiones y memoria
- **LocalStorage**: Preferencias del usuario (paneles, tema)

---

## 📖 Documentación

### 📘 Para Especialistas Técnicos

- **[Referencia Técnica Completa](docs/TECHNICAL_REFERENCE.md)** - Documentación exhaustiva (1770 líneas)
  - Arquitectura detallada con diagramas
  - Componentes core explicados línea por línea
  - API reference completa
  - Flujos de trabajo críticos
  - Sistema de extensiones (providers, tools, agents, plugins)
  - Seguridad y sandbox
  - Performance y optimización
  - Testing strategy
  - Deployment y DevOps
  - Troubleshooting avanzado

- **[Guía de Arquitectura](docs/ARCHITECTURE_GUIDE.md)** - Visión general concisa (411 líneas)
  - Principios arquitectónicos
  - Capas del sistema
  - Patrones de diseño implementados
  - Puntos de extensión
  - Métricas de performance

### 🚀 Para Nuevos Colaboradores

- **[Guía de Onboarding](ONBOARDING_COLABORADORES.md)** - Primeros pasos completos
- **[Informe de Estado](INFORME_ESTADO_PROYECTO.md)** - Estado actual y roadmap
- **[Contributing Guide](CONTRIBUTING.md)** - Cómo contribuir
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Normas de comunidad

### 📚 Guías de Usuario

- [Guía de Usuario Completa](GUIA_USUARIO.md)
- [Configuración de Múltiples LLMs](GUIA_MULTIPLES_LLMS.md)
- [Despliegue con Docker](DOCKER_DEPLOYMENT.md)

---

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# Proveedor activo (ollama, groq, openai, mimo)
ACTIVE_PROVIDER=ollama

# Configuración Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b

# Configuración Groq
GROQ_API_KEY=tu-api-key-aqui
GROQ_MODEL=llama-3.1-70b-versatile

# Configuración OpenAI
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-4

# Configuración Xiaomi MiMo
MIMO_API_KEY=tu-api-key-aqui
MIMO_BASE_URL=https://api.mimo.ai/v1
```

### Modelos Recomendados

| Proveedor | Modelo | Uso | Gratuito |
|-----------|--------|-----|----------|
| Ollama | qwen2.5-coder:7b | General | ✅ Sí |
| Ollama | codellama:13b | Código | ✅ Sí |
| Groq | llama-3.1-70b | Rápido | ❌ API Key |
| OpenAI | gpt-4 | Premium | ❌ API Key |
| MiMo | mimo-v1 | Alternativo | ✅ Sí |

---

## 🧪 Testing

### Ejecutar Suite de Pruebas

```bash
# Todas las pruebas
python run_all_tests.py

# Prueba rápida
python test_quick.py

# Prueba específica
python tests/test_conversation_memory.py
```

### Cobertura de Pruebas

- ✅ Memoria conversacional
- ✅ Gestión de sesiones
- ✅ Detección de lenguajes
- ✅ Sistema de parches
- ✅ Validación de seguridad
- ✅ Integración con LLMs

---

## 🔒 Seguridad

### Medidas Implementadas

1. **CSP Estricta**: Content-Security-Policy en todos los iframes
2. **Sandbox Aislado**: `allow-scripts allow-same-origin` únicamente
3. **Bloqueo de APIs Peligrosas**: localStorage, cookies, window.top
4. **Validación de Input**: Sanitización de código generado
5. **Sin Ejecución Remota**: Todo el código se ejecuta localmente
6. **Logs Seguros**: No se exponen credenciales en logs

### Auditoría de Seguridad

Ver [AUDITORIA_SEGURIDAD_RESUMEN.md](AUDITORIA_SEGURIDAD_RESUMEN.md) para detalles completos.

---

## 📊 Estado del Proyecto

### Versión Actual: v1.1

#### ✅ Completado
- [x] Editor de código con resaltado de sintaxis
- [x] Chat conversacional con IA
- [x] Preview en tiempo real
- [x] Paneles redimensionables
- [x] Multi-proveedor LLM
- [x] Memoria contextual persistente
- [x] Sistema de parches incremental
- [x] Detección y bloqueo de lenguajes
- [x] Seguridad CSP y sandbox
- [x] Documentación completa

#### 🚧 En Desarrollo
- [ ] Soporte para WebContainers (ejecución JS backend)
- [ ] Autocompletado inteligente
- [ ] Refactorización automática
- [ ] Tests E2E completos
- [ ] Plugin system avanzado

#### 📅 Roadmap
- **v1.2**: Mejoras de rendimiento y UX
- **v1.3**: Soporte para proyectos multi-archivo
- **v2.0**: Arquitectura de microservicios

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. **Fork** el repositorio
2. **Crea** una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'feat: agrega nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### Guía de Contribución

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre:
- Estándares de código
- Proceso de review
- Convenciones de commits
- Testing requerido

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para detalles.

---

## 👥 Equipo

- **Desarrollador Principal**: Kalin AI Team
- **Contribuidores**: [Ver lista de contribuidores](https://github.com/tu-usuario/kalin/graphs/contributors)

---

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai/) - Modelos locales de IA
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Qwen](https://github.com/QwenLM/Qwen) - Modelo de código abierto
- [Groq](https://groq.com/) - Inferencia ultra-rápida

---

## 📞 Contacto

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/kalin/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/kalin/discussions)
- **Email**: kalin-ai@example.com

---

## 📈 Métricas del Proyecto

![GitHub stars](https://img.shields.io/github/stars/tu-usuario/kalin?style=social)
![GitHub forks](https://img.shields.io/github/forks/tu-usuario/kalin?style=social)
![GitHub issues](https://img.shields.io/github/issues/tu-usuario/kalin)
![GitHub pull requests](https://img.shields.io/github/issues-pr/tu-usuario/kalin)
![Last commit](https://img.shields.io/github/last-commit/tu-usuario/kalin)

---

**Hecho con ❤️ por la comunidad Kalin AI**
