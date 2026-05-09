# 🏗️ Kalin Frontend - Arquitectura Modular

## 📋 Descripción

El frontend de Kalin AI ha sido refactorizado para ser **altamente escalable y modular**, permitiendo fácil mantenimiento y extensión de funcionalidades.

---

## 📁 Estructura de Archivos

```
static/js/
├── config.js           # Configuración centralizada
├── preview.js          # Módulo de renderizado/preview
├── chat.js             # Módulo de chat y comunicación
├── android-utils.js    # Utilidades específicas para Android
├── app.js              # Punto de entrada principal
└── README.md           # Esta documentación
```

---

## 🧩 Módulos

### 1. **config.js** - Configuración Centralizada
**Responsabilidad**: Centralizar todas las configuraciones del frontend.

**Características**:
- URLs y endpoints de API
- Configuración de UI (tamaños, límites)
- Patrones de detección de código
- Tipos de componentes Android soportados
- Lenguajes soportados
- Configuración de logging

**Uso**:
```javascript
// Acceder desde cualquier módulo
const apiUrl = window.AppConfig.API.SEND_MESSAGE;
const maxMessages = window.AppConfig.UI.MAX_CHAT_MESSAGES;
```

**Ventajas**:
- ✅ Un solo lugar para cambiar configuraciones
- ✅ Fácil de mantener
- ✅ Evita hardcoding en múltiples archivos

---

### 2. **preview.js** - PreviewManager
**Responsabilidad**: Renderizar código HTML/CSS/JS de forma segura en iframe sandbox.

**Características**:
- Toggle activar/desactivar preview
- Detección automática de código HTML
- CSP (Content Security Policy) estricta
- Bloqueo de APIs peligrosas (localStorage, cookies, etc.)
- Prevención de clickjacking
- Mensajes informativos cuando no hay preview

**Métodos Públicos**:
```javascript
window.PreviewManager.initialize()    // Inicializar
window.PreviewManager.toggle()         // Activar/desactivar
window.PreviewManager.render(code)     // Renderizar código
window.PreviewManager.isHTMLCode(code) // Verificar si es HTML
```

**Seguridad**:
- ✅ iframe sandbox con atributos restrictivos
- ✅ CSP que bloquea navegación externa
- ✅ Bloqueo de storage compartido
- ✅ Bloqueo de acceso a window.top/parent

---

### 3. **chat.js** - ChatManager
**Responsabilidad**: Manejar interfaz de chat, envío/recepción de mensajes.

**Características**:
- Envío de mensajes al backend
- Recepción y procesamiento de respuestas
- Indicador de typing
- Auto-scroll inteligente
- Límite de mensajes en historial
- Detección y extracción de código
- Integración con PreviewManager

**Métodos Públicos**:
```javascript
window.ChatManager.initialize()           // Inicializar
window.ChatManager.sendMessage()          // Enviar mensaje
window.ChatManager.addMessage(text, sender) // Agregar mensaje
window.ChatManager.displayCodeInMainArea(code) // Mostrar código
```

**Flujo**:
```
Usuario escribe → sendMessage() → Backend → processResponse() 
→ addMessage() → displayCodeInMainArea() → PreviewManager.render()
```

---

### 4. **android-utils.js** - AndroidUtils
**Responsabilidad**: Funciones utilitarias específicas para desarrollo Android.

**Características**:
- Detección de solicitudes de componentes Android
- Extracción de nombres de componentes
- Formateo de reportes de validación
- Detección de tipo de archivo Android
- Verificación de código Android
- Syntax highlighting básico

**Métodos Públicos**:
```javascript
window.AndroidUtils.detectAndroidComponentRequest(message) // Detectar solicitud
window.AndroidUtils.formatValidationReport(report)         // Formatear reporte
window.AndroidUtils.isAndroidCode(code)                    // Verificar código
window.AndroidUtils.getComponentIcon(type)                 // Obtener icono
```

**Patrones Detectados**:
- "crea una Activity llamada X"
- "genera un Fragment para Y"
- "haz un adapter para Z"
- etc.

---

### 5. **app.js** - KalinApp (Punto de Entrada)
**Responsabilidad**: Inicializar y coordinar todos los módulos.

**Características**:
- Inicialización secuencial de módulos
- Verificación de dependencias
- Event listeners globales
- Manejo de errores
- Mensaje de bienvenida
- Estado de la aplicación

**Métodos Públicos**:
```javascript
window.KalinApp.initialize()      // Inicializar app
window.KalinApp.getStatus()       // Obtener estado
```

**Flujo de Inicialización**:
```
1. Verificar AppConfig disponible
2. Inicializar PreviewManager
3. Inicializar ChatManager
4. Cargar AndroidUtils
5. Configurar event listeners globales
6. Mostrar mensaje de bienvenida
```

---

## 🔄 Comunicación entre Módulos

```
┌─────────────┐
│   app.js    │ ← Coordinador principal
└──────┬──────┘
       │
       ├──────────┐
       │          │
┌──────▼──────┐ ┌─▼────────────┐
│  chat.js    │ │ preview.js   │
└──────┬──────┘ └──────────────┘
       │
       │ (detecta código HTML)
       │
       ▼
┌──────────────┐
│ preview.js   │ ← Renderiza automáticamente
└──────────────┘

┌──────────────┐
│android-utils │ ← Disponible para todos
└──────────────┘
```

**Ejemplo de integración**:
```javascript
// En chat.js, después de recibir respuesta
if (window.PreviewManager && code) {
    if (window.PreviewManager.isHTMLCode(code)) {
        window.PreviewManager.render(code);
    }
}
```

---

## 🚀 Cómo Extender

### Agregar Nuevo Módulo

1. **Crear archivo** en `static/js/nuevo-modulo.js`:
```javascript
class NuevoModulo {
    constructor() {
        this.initialized = false;
    }

    initialize() {
        if (this.initialized) return;
        // Lógica de inicialización
        this.initialized = true;
        console.log('✅ NuevoModulo inicializado');
    }

    // Métodos públicos
    hacerAlgo() {
        console.log('Haciendo algo...');
    }
}

const nuevoModulo = new NuevoModulo();
window.NuevoModulo = nuevoModulo;
export default nuevoModulo;
```

2. **Agregar a config.js** (si necesita configuración):
```javascript
const AppConfig = {
    // ... existing config
    NUEVO_MODULO: {
        OPCION_1: 'valor',
        OPCION_2: 42
    }
};
```

3. **Registrar en app.js**:
```javascript
async initializeModules() {
    // ... existing modules
    
    if (window.NuevoModulo) {
        window.NuevoModulo.initialize();
        this.modules.nuevo = window.NuevoModulo;
        console.log('✅ NuevoModulo inicializado');
    }
}
```

4. **Incluir en index.html**:
```html
<script src="/static/js/nuevo-modulo.js"></script>
```

---

### Agregar Nueva Funcionalidad Android

1. **Actualizar config.js**:
```javascript
ANDROID_COMPONENTS: {
    // ... existing components
    NEW_COMPONENT: 'new_component'
}
```

2. **Agregar patrón en android-utils.js**:
```javascript
const componentPatterns = {
    // ... existing patterns
    'new_component': ['keyword1', 'keyword2']
};
```

3. **Agregar template en backend** (`android_boilerplate.py`):
```python
def _generate_new_component_template(self, name: str, **kwargs):
    # Generar código
    return {f"{name}.java": codigo}
```

---

## 🎨 Estilos CSS Modulares

Los estilos también están organizados por sección en `index.html`:

```css
/* ===== Layout Principal ===== */
.main-layout { ... }
.code-area { ... }
.preview-area { ... }
.chat-sidebar { ... }

/* ===== Preview ===== */
.preview-header { ... }
.preview-content { ... }

/* ===== Chat ===== */
.chat-messages { ... }
.message { ... }

/* ===== Código ===== */
.code-block { ... }
```

**Para agregar nuevos estilos**:
1. Identificar la sección correspondiente
2. Agregar comentarios descriptivos
3. Usar naming consistente (BEM recomendado)

---

## 🧪 Testing

### Probar Módulos Individualmente

```javascript
// En consola del navegador

// Verificar configuración
console.log(window.AppConfig);

// Probar Preview
window.PreviewManager.render('<h1>Test</h1>');

// Probar Chat
window.ChatManager.addMessage('Test message', 'user');

// Probar Android Utils
const result = window.AndroidUtils.detectAndroidComponentRequest(
    'crea una Activity llamada LoginScreen'
);
console.log(result);

// Verificar estado de app
console.log(window.KalinApp.getStatus());
```

---

## 📊 Métricas de Escalabilidad

### Antes (Monolítico):
- ❌ 2384 líneas en un solo archivo
- ❌ Difícil de mantener
- ❌ Acoplamiento fuerte
- ❌ Testing complicado

### Después (Modular):
- ✅ ~300 líneas por módulo
- ✅ Fácil mantenimiento
- ✅ Bajo acoplamiento
- ✅ Testing individual posible
- ✅ Reutilización de código
- ✅ Extensibilidad simple

---

## 🔧 Mejoras Futuras

### Corto Plazo:
- [ ] Agregar TypeScript para type safety
- [ ] Implementar unit tests (Jest)
- [ ] Agregar sistema de plugins
- [ ] Mejorar syntax highlighting (Prism.js)

### Mediano Plazo:
- [ ] Migrar a framework (React/Vue)
- [ ] Implementar state management (Redux/Pinia)
- [ ] Agregar PWA support
- [ ] Offline mode

### Largo Plazo:
- [ ] Micro-frontends architecture
- [ ] Web Components reutilizables
- [ ] Real-time collaboration
- [ ] Plugin marketplace

---

## 📚 Recursos

- [MDN Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components)
- [JavaScript Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [iframe Sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#sandbox)

---

## 👥 Contribuir

1. Seguir estructura modular existente
2. Documentar cambios en este README
3. Agregar tests para nueva funcionalidad
4. Mantener configuración en config.js
5. Usar nombres descriptivos para variables/funciones

---

**Última actualización**: Mayo 2026  
**Versión**: 2.0.0 (Arquitectura Modular)
