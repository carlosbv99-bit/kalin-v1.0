# 🤝 Guía de Contribución a Kalin AI

¡Gracias por tu interés en contribuir a Kalin AI! Esta guía te ayudará a entender cómo puedes participar en el desarrollo del proyecto.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Estándares de Código](#estándares-de-código)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Testing](#testing)
- [Documentación](#documentación)

---

## 🌟 Código de Conducta

### Nuestros Compromisos

En el interés de fomentar un entorno abierto y acogedor, nosotros como contribuidores y mantenedores nos comprometemos a hacer de la participación en nuestro proyecto una experiencia libre de acoso para todos, independientemente de:

- Edad
- Discapacidad
- Etnia
- Identidad y expresión de género
- Nivel de experiencia
- Nacionalidad
- Apariencia personal
- Raza
- Religión
- Identidad y orientación sexual

### Comportamiento Aceptable

- Usar lenguaje inclusivo y respetuoso
- Ser respetuoso con diferentes puntos de vista
- Aceptar críticas constructivas de buena fe
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros miembros

### Comportamiento Inaceptable

- Uso de lenguaje o imágenes sexualizadas
- Trolling, insultos o comentarios despectivos
- Acoso público o privado
- Publicar información privada de otros sin permiso
- Otras conductas que podrían considerarse inapropiadas

---

## 🚀 Cómo Contribuir

### 1. Reportar Bugs

Los bugs se rastrean como **GitHub Issues**. Al crear un issue:

**Título claro**: Describe el problema brevemente
```
❌ Mal: "No funciona"
✅ Bien: "Preview no se actualiza al modificar código HTML"
```

**Descripción detallada**:
- Pasos para reproducir el error
- Comportamiento esperado vs actual
- Logs de error (si aplica)
- Versión de Python y navegador
- Capturas de pantalla (si es relevante)

**Ejemplo**:
```markdown
### Descripción
El preview no se actualiza automáticamente cuando modifico código HTML en el editor.

### Pasos para reproducir
1. Generar código HTML con "crea una página web"
2. Pedir modificación: "cambia el título"
3. Observar que el editor se actualiza pero el preview no

### Comportamiento esperado
El preview debería actualizarse automáticamente después de aplicar el cambio.

### Comportamiento actual
El preview muestra el código antiguo hasta recargar la página.

### Environment
- Python: 3.9
- Navegador: Chrome 120
- OS: Windows 11
```

### 2. Sugerir Mejoras

Las sugerencias también van como **Issues** con label `enhancement`.

Incluye:
- Caso de uso específico
- Beneficio propuesto
- Posibles alternativas consideradas

### 3. Contribuir Código

#### Flujo de Trabajo

```bash
# 1. Fork el repositorio
# Haz clic en "Fork" en GitHub

# 2. Clona tu fork
git clone https://github.com/tu-usuario/kalin.git
cd kalin

# 3. Agrega upstream
git remote add upstream https://github.com/original/kalin.git

# 4. Crea rama feature
git checkout -b feature/nombre-funcionalidad

# 5. Desarrolla y prueba
# ... tus cambios ...

# 6. Commit siguiendo convenciones
git commit -m "feat: agrega actualización automática de preview"

# 7. Push a tu fork
git push origin feature/nombre-funcionalidad

# 8. Abre Pull Request desde GitHub
```

#### Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<alcance>): <descripción>

[cuerpo opcional]

[pie opcional]
```

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato (espacios, punto y coma, etc.)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos**:
```bash
git commit -m "feat(preview): agregar actualización automática con debounce"
git commit -m "fix(memory): corregir pérdida de contexto entre sesiones"
git commit -m "docs(readme): actualizar sección de instalación"
git commit -m "refactor(editor): simplificar lógica de resaltado de sintaxis"
```

---

## 💻 Estándares de Código

### Python

#### Estilo
- Seguir [PEP 8](https://peps.python.org/pep-0008/)
- Indentación: 4 espacios
- Líneas máximo: 100 caracteres
- Docstrings: Google style

```python
def detect_language(code: str) -> str:
    """
    Detecta el lenguaje de programación del código proporcionado.
    
    Args:
        code: String conteniendo el código a analizar
        
    Returns:
        Nombre del lenguaje detectado ('python', 'javascript', 'html', etc.)
        Retorna 'unknown' si no se puede determinar
        
    Raises:
        ValueError: Si el código está vacío
    """
    if not code:
        raise ValueError("El código no puede estar vacío")
    
    # Lógica de detección
    ...
```

#### Naming
- Variables: `snake_case`
- Constantes: `UPPER_CASE`
- Clases: `PascalCase`
- Métodos privados: `_prefijo_underscore`

```python
MAX_HISTORY_LENGTH = 50
conversation_memory = ConversationMemory()
_session_id = "abc123"
```

#### Imports
```python
# Estándar library primero
import os
import sys
from datetime import datetime

# Third-party libraries
import flask
import requests

# Local application/library specific imports
from agent.core.conversation_memory import ConversationMemory
```

### JavaScript

#### Estilo
- Sin framework (Vanilla JS)
- ES6+ features permitidas
- Indentación: 4 espacios
- Semicolons opcionales (ser consistente)

```javascript
/**
 * Gestiona el renderizado seguro de código HTML/CSS/JS
 */
class PreviewManager {
    constructor() {
        this.enabled = true;
        this.previewFrame = null;
        this.initialized = false;
    }

    /**
     * Renderiza código en el iframe sandbox
     * @param {string} code - Código HTML a renderizar
     */
    render(code) {
        if (!this.isHTMLCode(code)) {
            console.warn('⚠️ Código no es HTML');
            return;
        }
        
        // Implementación
        this.previewFrame.srcdoc = this.prepareSecureHTML(code);
    }
}
```

#### Naming
- Variables: `camelCase`
- Clases: `PascalCase`
- Constantes: `UPPER_CASE`
- Privado: `_prefijoUnderscore`

#### Async/Await
```javascript
// ✅ Preferido
async function sendMessage(message) {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// ❌ Evitar callbacks anidados
sendMessage(message, function(response) {
    // Callback hell
});
```

### HTML/CSS

#### HTML Semántico
```html
<!-- ✅ Correcto -->
<header class="header">
    <nav aria-label="Navegación principal">
        ...
    </nav>
</header>

<main class="main-layout">
    <section class="code-area" role="region" aria-label="Editor de código">
        ...
    </section>
</main>

<!-- ❌ Evitar divs genéricos -->
<div class="header">
    <div class="nav">...</div>
</div>
```

#### CSS
- Mobile-first approach
- BEM naming para clases complejas
- Variables CSS para colores/tamaños

```css
/* Variables globales */
:root {
    --color-primary: #0066ff;
    --spacing-sm: 8px;
    --font-mono: 'Fira Code', monospace;
}

/* BEM */
.chat-message {
    padding: var(--spacing-sm);
}

.chat-message--user {
    background-color: #e3f2fd;
}

.chat-message__content {
    font-size: 14px;
}
```

---

## 🔀 Proceso de Pull Request

### Checklist Antes de Enviar

- [ ] Código sigue estándares del proyecto
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Commits siguen convención Conventional Commits
- [ ] No hay conflictos con branch main
- [ ] Revisado linting/formatting

### Proceso de Review

1. **Automated Checks**: CI ejecuta tests y linting
2. **Review Técnico**: Mantenedor revisa código
3. **Feedback**: Comentarios y sugerencias
4. **Ajustes**: Contributor hace cambios solicitados
5. **Aprobación**: Maintainer aprueba PR
6. **Merge**: Se integra a main

### Timeline Esperado

- **Review inicial**: 2-3 días hábiles
- **Feedback loop**: 1-2 días por iteración
- **Merge**: Dentro de 1 semana si todo está bien

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Suite completa
python run_all_tests.py

# Test específico
python tests/test_conversation_memory.py

# Con coverage
pytest --cov=agent tests/
```

### Escribir Tests

```python
import unittest
from agent.core.conversation_memory import ConversationMemory

class TestConversationMemory(unittest.TestCase):
    
    def setUp(self):
        self.memory = ConversationMemory(session_id="test_123")
    
    def test_save_message(self):
        """Test que guarda mensaje correctamente"""
        self.memory.add_message("user", "Hola")
        self.assertEqual(len(self.memory.conversation_history), 1)
    
    def test_compress_history(self):
        """Test compresión de historial"""
        # Agregar 60 mensajes
        for i in range(60):
            self.memory.add_message("user", f"Mensaje {i}")
        
        # Comprimir
        self.memory.compress_old_entries(keep_recent=10)
        
        # Verificar que se comprimieron
        self.assertLess(len(self.memory.conversation_history), 60)
    
    def tearDown(self):
        # Limpieza
        pass

if __name__ == '__main__':
    unittest.main()
```

### Coverage Mínimo

-新功能: ≥80% coverage
- Bug fixes: Test que reproduce el bug + fix
- Refactoring: No reducir coverage existente

---

## 📚 Documentación

### Actualizar README

Si tu cambio afecta:
- Instalación → Actualizar sección "Inicio Rápido"
- Configuración → Actualizar sección "Configuración"
- Features → Actualizar "Características Principales"

### Documentar Código

```python
def apply_patch(existing_code: str, new_fragment: str, language: str) -> str:
    """
    Aplica un parche incremental al código existente.
    
    Este método inserta inteligentemente el nuevo fragmento sin reemplazar
    el código completo, preservando funcionalidades existentes.
    
    Args:
        existing_code: Código actual en el editor
        new_fragment: Fragmento generado por el LLM
        language: Lenguaje de programación detectado
        
    Returns:
        Código combinado con el parche aplicado
        
    Raises:
        PatchError: Si el parche no se puede aplicar
        
    Example:
        >>> existing = "def foo():\n    pass"
        >>> new = "def bar():\n    pass"
        >>> result = apply_patch(existing, new, "python")
        >>> print(result)
        def foo():
            pass
        
        def bar():
            pass
    """
    # Implementación
    ...
```

### CHANGELOG

Agregar entrada en `CHANGELOG.md`:

```markdown
## [1.1.1] - 2026-05-12

### Added
- Actualización automática de preview al modificar código (#123)
- Debounce de 500ms para evitar actualizaciones excesivas

### Fixed
- Preview no se sincronizaba con cambios manuales (#124)
- Pérdida de contexto al cambiar de lenguaje (#125)

### Changed
- Mejorado sistema de detección de lenguajes
- Optimizado rendimiento de renderizado
```

---

## 🏷️ Labels de GitHub

Usamos labels para categorizar issues y PRs:

### Tipos
- `bug`: Algo no funciona correctamente
- `enhancement`: Nueva funcionalidad o mejora
- `documentation`: Mejoras en docs
- `question`: Pregunta o discusión
- `good first issue`: Bueno para principiantes

### Prioridad
- `priority: high`: Crítico, bloqueante
- `priority: medium`: Importante
- `priority: low`: Nice to have

### Estado
- `status: needs-review`: Esperando review
- `status: in-progress`: En desarrollo
- `status: blocked`: Bloqueado por algo

---

## 🎯 Áreas que Necesitan Ayuda

### Alta Prioridad
- [ ] Tests E2E con Selenium/Playwright
- [ ] Soporte para TypeScript
- [ ] Sistema de plugins documentado
- [ ] Internacionalización (i18n)

### Media Prioridad
- [ ] Temas personalizables (dark/light mode)
- [ ] Atajos de teclado configurables
- [ ] Autocompletado inteligente
- [ ] Integración con Git

### Baja Prioridad
- [ ] Extensiones VS Code
- [ ] App móvil
- [ ] Colaboración en tiempo real

---

## 📞 Contacto

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/kalin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/kalin/discussions)
- **Email**: kalin-ai@example.com

---

## 🙏 Reconocimiento

Los contribuidores son reconocidos en:
- README.md (sección Equipo)
- RELEASE notes
- GitHub Contributors graph

¡Gracias por hacer Kalin AI mejor! 🚀
