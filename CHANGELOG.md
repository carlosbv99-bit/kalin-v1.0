# CHANGELOG

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [1.1.1] - 2026-05-12

### Added
- Actualización automática del preview al modificar código HTML (#130)
- Sistema de debounce (500ms) para evitar actualizaciones excesivas del preview
- Documentación completa: README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- Detección y bloqueo automático de lenguaje por sesión
- Validación estricta pre-aplicación de parches de código

### Fixed
- Preview no se sincronizaba con cambios manuales en el editor (#131)
- Pérdida de contexto al cambiar entre lenguajes de programación (#132)
- Código borrado al agregar nuevas funcionalidades (#133)
- Ventana de contexto limitada entre sesiones (#134)

### Changed
- Ampliada ventana de contexto de 2000 a 10000 caracteres (5x más)
- Aumentado historial conversacional de 20 a 50 interacciones
- Mejorado sistema de compresión de historial antiguo
- Optimizado rendimiento de renderizado de previews

### Security
- Reforzadas políticas CSP en iframes de preview
- Mejorada validación de código generado por LLMs
- Agregado bloqueo de APIs peligrosas en sandbox

---

## [1.1.0] - 2026-05-09

### Added
- Paneles redimensionables ultra-finios (1px)
- Editor de código con resaltado de sintaxis multi-lenguaje
- Sistema de pestañas para múltiples archivos
- Árbol de archivos interactivo con slide-in
- Numeración de líneas sincronizada
- Auto-indentación inteligente
- Resaltado de línea activa
- Menús desplegables superiores (Archivo, Editar, Ver)
- Soporte para WebContainers (ejecución JS en navegador)
- Sistema de deshacer/rehacer (Ctrl+Z/Ctrl+Y)
- Guías visuales de indentación

### Changed
- Arquitectura frontend modularizada (7 módulos JavaScript)
- Separación clara de responsabilidades (MVC pattern)
- Mejorado layout: Código izquierda, Preview centro, Chat derecha
- Eliminado mensaje de bienvenida automático
- Optimizado CSS con variables y transiciones

### Fixed
- Error 404 en endpoint `/chat` (corregido ruta API)
- Bordes de paneles duplicados eliminados
- Scripts legacy comentados removidos
- Problemas de cache en estilos CSS

### Removed
- Código inline monolítico de index.html (1357 líneas → módulos)
- Mensaje de bienvenida automático en chat
- Botones redundantes en editor

---

## [1.0.0] - 2026-04-15

### Added
- Primer lanzamiento estable de Kalin AI
- Chat conversacional con IA integrada
- Generación de código en Python, JavaScript, HTML, CSS, Java, C/C++
- Vista previa en tiempo real para HTML/CSS/JS
- Soporte para múltiples proveedores LLM:
  - Ollama (modelos locales)
  - Groq API
  - OpenAI GPT
  - Xiaomi MiMo
- Memoria conversacional básica
- Gestión de sesiones persistente
- Sistema de parches incremental
- Export/import de experiencia
- Descarga automática de modelos Ollama
- Creación guiada de entorno virtual
- Reconocimiento de voz (Web Speech API)

### Security
- Sandbox de iframe para previews
- Content-Security-Policy básica
- Bloqueo de navegación superior
- Sin exposición de credenciales en frontend

---

## [0.9.0-beta] - 2026-03-20

### Added
- Versión beta inicial
- Prototipo de chat con IA
- Editor de texto básico
- Integración con Ollama
- Generación de código Python simple

### Known Issues
- UI experimental
- Sin persistencia de sesiones
- Preview limitado
- Sin soporte multi-lenguaje completo

---

## Tipos de Cambios

- **Added**: Para nuevas funcionalidades
- **Changed**: Para cambios en funcionalidades existentes
- **Deprecated**: Para funcionalidades que serán removidas
- **Removed**: Para funcionalidades removidas
- **Fixed**: Para correcciones de bugs
- **Security**: Para mejoras de seguridad

---

## Enlaces

- [Releases en GitHub](https://github.com/tu-usuario/kalin/releases)
- [Issues](https://github.com/tu-usuario/kalin/issues)
- [Documentación](README.md)

---

**Nota**: Las fechas están en formato YYYY-MM-DD siguiendo ISO 8601.
