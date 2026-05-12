# Seguridad - Kalin AI

## 🛡️ Política de Seguridad

La seguridad es una prioridad fundamental en Kalin AI. Esta documentación describe nuestras prácticas de seguridad, vulnerabilidades conocidas y cómo reportar problemas de seguridad.

---

## 📋 Versiones Soportadas

| Versión | Soportada | Estado |
|---------|-----------|--------|
| 1.1.x   | ✅ Sí     | Activa |
| 1.0.x   | ⚠️ Parcial | Legacy |
| < 1.0   | ❌ No     | Obsoleta |

---

## 🔒 Medidas de Seguridad Implementadas

### 1. **Content Security Policy (CSP)**

Todas las vistas previas se renderizan con CSP estricta:

```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'unsafe-inline' 'unsafe-eval';
    style-src 'unsafe-inline';
    img-src 'self' data: https:;
    connect-src 'none';
    frame-src 'none';
    object-src 'none';
    base-uri 'self';
    form-action 'none'
">
```

**Protege contra**:
- XSS (Cross-Site Scripting)
- Inyección de scripts maliciosos
- Robo de datos mediante iframes externos

### 2. **Sandbox de Iframe**

Los previews se ejecutan en un sandbox aislado:

```html
<iframe sandbox="allow-scripts allow-same-origin"></iframe>
```

**Restricciones**:
- ❌ Sin navegación superior (`allow-top-navigation` bloqueado)
- ❌ Sin formularios (`allow-forms` bloqueado)
- ❌ Sin popups (`allow-popups` bloqueado)
- ❌ Sin plugins (`allow-plugins` bloqueado)
- ✅ Solo scripts y mismo origen permitidos

### 3. **Bloqueo de APIs Peligrosas**

Script de seguridad inyectado en cada preview:

```javascript
// Bloquear acceso a window.top (previene clickjacking)
Object.defineProperty(window, "top", { value: window });
Object.defineProperty(window, "parent", { value: window });

// Bloquear storage compartido
delete window.localStorage;
delete window.sessionStorage;
delete window.indexedDB;

// Bloquear cookies
Object.defineProperty(document, "cookie", {
    get: function() { return ""; },
    set: function() { }
});

// Bloquear navegación
window.open = function() { return null; };
window.location.replace = function() { };
window.location.assign = function() { };
```

### 4. **Validación de Input**

- Sanitización de código generado por LLM
- Validación de lenguajes permitidos
- Detección de patrones maliciosos
- Límites de tamaño de input

### 5. **Gestión Segura de Credenciales**

- API keys almacenadas en `.env` (no en código)
- `.env` excluido de Git (`.gitignore`)
- Variables de entorno para configuración sensible
- Sin hardcoding de credenciales

### 6. **Logging Seguro**

- No se loguean API keys o tokens
- Logs separados por categoría (app, errors, llm)
- Rotación automática de logs
- Sin información sensible en mensajes de error públicos

---

## 🐛 Reportar Vulnerabilidades

Si descubres una vulnerabilidad de seguridad, por favor repórtala de manera responsable:

### Proceso de Reporte

1. **NO** crees un issue público en GitHub
2. Envía un email a: **security@kalin-ai.example.com**
3. Incluye:
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir
   - Impacto potencial
   - Sugerencias de mitigación (opcional)

### Timeline Esperado

- **Confirmación de recepción**: 24-48 horas
- **Evaluación inicial**: 3-5 días hábiles
- **Patch desarrollado**: 7-14 días (dependiendo de severidad)
- **Divulgación pública**: Después de que el patch esté disponible

### Programa de Recompensas

Actualmente no tenemos un programa de bug bounty formal, pero reconocemos públicamente a los investigadores de seguridad que reporten vulnerabilidades válidas (con su permiso).

---

## ⚠️ Vulnerabilidades Conocidas

### Mitigadas en v1.1

| CVE | Severidad | Descripción | Estado |
|-----|-----------|-------------|--------|
| N/A | Media | Preview podía ejecutar scripts externos | ✅ Fixeado en v1.1 |
| N/A | Baja | Posible fuga de contexto entre sesiones | ✅ Fixeado en v1.1 |

### En Progreso

- [ ] Mejorar rate limiting en API endpoints
- [ ] Agregar validación CSRF tokens
- [ ] Implementar Content-Security-Policy reporting

---

## 🔐 Mejores Prácticas para Usuarios

### Configuración Segura

1. **Usa modelos locales cuando sea posible**
   ```bash
   # Instalar Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Usar modelo local
   ACTIVE_PROVIDER=ollama
   ```

2. **Protege tus API keys**
   ```bash
   # Nunca commitear .env
   echo ".env" >> .gitignore
   
   # Usar permisos restrictivos
   chmod 600 .env
   ```

3. **Mantén dependencias actualizadas**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Usa HTTPS en producción**
   - Configurar reverse proxy (nginx, Apache)
   - Certificado SSL/TLS válido
   - Redirección HTTP → HTTPS

### Desarrollo Seguro

```python
# ✅ Correcto: Usar variables de entorno
import os
api_key = os.getenv('GROQ_API_KEY')

# ❌ Incorrecto: Hardcodear credenciales
api_key = "sk-abc123..."
```

```javascript
// ✅ Correcto: Validar input
if (!this.isHTMLCode(code)) {
    console.warn('⚠️ Código no válido');
    return;
}

// ❌ Incorrecto: Renderizar sin validar
this.previewFrame.srcdoc = code;
```

---

## 🛠️ Auditorías de Seguridad

### Última Auditoría

**Fecha**: Mayo 2026  
**Auditor**: Equipo Kalin AI  
**Alcance**: 
- Frontend (HTML/CSS/JS)
- Backend (Flask)
- Integración con LLMs
- Gestión de sesiones

**Resultados**:
- ✅ No vulnerabilidades críticas encontradas
- ⚠️ 2 recomendaciones de mejora (implementadas)
- ℹ️ 5 sugerencias de hardening (roadmap)

**Reporte completo**: [AUDITORIA_SEGURIDAD_RESUMEN.md](AUDITORIA_SEGURIDAD_RESUMEN.md)

### Próximas Auditorías

- **Q3 2026**: Auditoría externa planificada
- **Q4 2026**: Penetration testing programado

---

## 📚 Recursos de Seguridad

### Documentación Interna

- [Política de Seguridad](SECURITY.md) - Este archivo
- [Auditoría de Seguridad](AUDITORIA_SEGURIDAD_RESUMEN.md)
- [Guía de Despliegue Seguro](DOCKER_DEPLOYMENT.md#seguridad)

### Estándares Externos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

### Herramientas Recomendadas

- **SAST**: Bandit (Python), ESLint security plugins (JS)
- **DAST**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: `pip-audit`, `npm audit`
- **Secret Detection**: GitLeaks, TruffleHog

---

## 🔄 Actualizaciones de Seguridad

### Suscribirse a Alertas

- **GitHub Security Advisories**: [Suscribirse](https://github.com/tu-usuario/kalin/security/advisories)
- **RSS Feed**: [Feed de seguridad](https://github.com/tu-usuario/kalin/security-advisories.atom)
- **Email**: Enviar request a security@kalin-ai.example.com

### Changelog de Seguridad

Ver [CHANGELOG.md](CHANGELOG.md) sección "Security" para historial completo.

---

## 🤝 Divulgación Responsable

Agradecemos a los siguientes investigadores de seguridad por sus contribuciones:

- **2026-05**: @researcher1 - Reportó problema de sandbox bypass (fixeado)
- **2026-04**: @securityteam - Auditoría voluntaria del frontend

¿Quieres ser reconocido aquí? Reporta vulnerabilidades siguiendo nuestro proceso.

---

## 📞 Contacto

- **Email de seguridad**: security@kalin-ai.example.com
- **PGP Key**: [Descargar](https://kalin-ai.example.com/pgp-key.asc)
- **Issues públicos**: [GitHub Issues](https://github.com/tu-usuario/kalin/issues) (solo para temas NO sensibles)

---

**Última actualización**: 12 de Mayo, 2026  
**Versión del documento**: 1.1
