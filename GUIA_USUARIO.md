# 📚 GUÍA COMPLETA PARA USUARIOS - KALIN v3.0

## 👋 ¿Qué es Kalin?

Kalin es un **asistente de programación inteligente** que puede:
- 🔧 Reparar errores en tu código automáticamente
- 📊 Analizar proyectos completos
- 💡 Sugerir mejoras y optimizaciones
- 🤝 Conversar sobre desarrollo de software

**No necesitas ser experto en tecnología para usarlo.**

---

## 🚀 INSTALACIÓN PASO A PASO (5 minutos)

### Paso 1: Instalar Python
1. Ve a https://www.python.org/downloads/
2. Descarga la última versión de Python
3. Ejecuta el instalador
4. ✅ Marca la casilla **"Add Python to PATH"**
5. Click en **"Install Now"**

### Paso 2: Descargar Kalin
```bash
# Opción A: Si tienes Git instalado
git clone https://github.com/tu-usuario/kalin.git
cd kalin

# Opción B: Descargar ZIP desde GitHub
# 1. Ve al repositorio en GitHub
# 2. Click en "Code" → "Download ZIP"
# 3. Extrae el archivo ZIP
# 4. Abre la carpeta extraída
```

### Paso 3: Instalar dependencias
```bash
# Abre una terminal en la carpeta de Kalin
pip install flask requests python-dotenv jinja2 pytest
```

### Paso 4: Configurar Kalin
```bash
# Copiar archivo de configuración de ejemplo
copy .env.example .env

# Editar .env con tu editor de texto favorito
notepad .env
```

**Configuración recomendada para principiantes:**
```env
KALIN_MODE=local
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=1
```

### Paso 5: Instalar Ollama (para IA local gratuita)
1. Ve a https://ollama.ai
2. Descarga e instala Ollama
3. Abre una terminal y ejecuta:
```bash
ollama pull deepseek-coder
ollama serve
```

### Paso 6: ¡Iniciar Kalin!
```bash
python run.py
```

Abre tu navegador y ve a: **http://localhost:5000**

¡Listo! 🎉

---

## 💬 CÓMO USAR KALIN

### Interfaz Web
Cuando abras http://localhost:5000 verás:
- 💬 Un chat vacío (como ChatGPT)
- ⌨️ Un campo de texto abajo para escribir
- 🎤 Un botón de micrófono para hablar (opcional)

### Comandos Básicos

#### 1. Configurar tu proyecto
```
/setpath E:\MiProyecto
```
Esto le dice a Kalin dónde está tu código.

#### 2. Reparar un archivo
```
/fix main.py
```
Kalin analizará el archivo y sugerirá correcciones.

#### 3. Aplicar cambios
```
/apply
```
Aplica las correcciones sugeridas.

#### 4. Escanear proyecto completo
```
/scan
```
Analiza todos los archivos de tu proyecto.

#### 5. Analizar un archivo específico
```
/analyze utils.py
```

### Conversación Natural
También puedes hablar con Kalin naturalmente:

```
"hola, tengo un error en mi código"
"¿puedes revisar el archivo main.py?"
"necesito ayuda con Python"
"explica este código"
```

---

## ❓ PREGUNTAS FRECUENTES

### ¿Es gratis?
✅ **Sí**, si usas Ollama (IA local). Es completamente gratuito y funciona sin internet.

Si quieres usar OpenAI o Anthropic, necesitas una cuenta paga.

### ¿Necesito internet?
- Con Ollama: **No**, funciona offline
- Con OpenAI/Anthropic: **Sí**, requiere conexión

### ¿Es seguro?
✅ **Sí**, Kalin incluye:
- Protección contra ataques maliciosos
- Validación de todas las operaciones
- No expone tus API keys
- Funciona en tu computadora local

### ¿Puede borrar mis archivos?
⚠️ Kalin tiene un **modo seguro** activado por defecto:
- Siempre muestra los cambios antes de aplicarlos
- Tú decides si aceptar o rechazar
- Crea backups automáticos

### ¿Qué lenguajes soporta?
Python, JavaScript, TypeScript, Java, Kotlin, Dart, Go, Rust, C, C++, C#, Ruby, PHP, HTML, CSS, y más.

### ¿Funciona en Windows/Mac/Linux?
✅ Sí, en los tres sistemas operativos.

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### Problema: "No se pudo conectar a Ollama"
**Solución:**
1. Verifica que Ollama esté corriendo:
   ```bash
   ollama serve
   ```
2. En otra terminal, verifica:
   ```bash
   ollama list
   ```
3. Deberías ver `deepseek-coder` en la lista

### Problema: "Error al iniciar servidor"
**Solución:**
1. Verifica que el puerto 5000 no esté en uso
2. Cambia el puerto en `.env`:
   ```env
   FLASK_PORT=5001
   ```
3. Reinicia Kalin

### Problema: "API key inválida"
**Solución:**
1. Verifica que tu API key sea correcta
2. No copies espacios al final
3. Usa modo local si no tienes API key:
   ```env
   KALIN_MODE=local
   ```

### Problema: "Muy lento"
**Solución:**
1. Cierra otras aplicaciones para liberar RAM
2. Usa modelos más pequeños en Ollama
3. Habilita caché (ya viene activado por defecto)

---

## 🔒 SEGURIDAD - LO QUE DEBES SABER

### ✅ Kalin es seguro porque:
1. **Funciona en tu computadora** - No envía datos a servidores externos (con Ollama)
2. **Modo seguro activado** - Siempre pregunta antes de cambiar archivos
3. **Protección contra ataques** - Bloquea comandos maliciosos automáticamente
4. **API keys protegidas** - Nunca muestra tus claves en logs o errores

### ⚠️ Precauciones importantes:
1. **NUNCA compartas tu archivo `.env`** - Contiene tus API keys
2. **NO expongas Kalin a internet** - Úsalo solo en localhost
3. **Revisa los cambios antes de aplicar** - Kalin sugiere, tú decides
4. **Mantén Kalin actualizado** - Las actualizaciones incluyen parches de seguridad

---

## 📖 GLOSARIO (Términos Técnicos Explicados)

**API Key**: Una contraseña especial que permite a Kalin usar servicios de IA como OpenAI.

**Localhost**: Tu propia computadora. Cuando decimos "localhost:5000", significa "en tu computadora, puerto 5000".

**Ollama**: Un programa gratuito que ejecuta IA en tu computadora sin necesidad de internet.

**Terminal/Consola**: Una ventana donde escribes comandos. En Windows se llama "PowerShell" o "CMD".

**Port/Puerto**: Una "puerta digital" en tu computadora. Kalin usa el puerto 5000 por defecto.

**Cache**: Memoria temporal que hace que Kalin sea más rápido al recordar resultados anteriores.

**Plugin**: Un módulo adicional que agrega funcionalidades a Kalin (como integración con Git).

---

## 🎯 PRIMEROS PASOS RECOMENDADOS

### Día 1: Familiarización
1. Instala Kalin siguiendo la guía arriba
2. Explora la interfaz web
3. Prueba saludar: "hola"
4. Configura tu proyecto: `/setpath C:\MiProyecto`

### Día 2: Primeras reparaciones
1. Identifica un archivo con errores
2. Ejecuta: `/fix nombre_archivo.py`
3. Revisa los cambios sugeridos
4. Si te gustan: `/apply`

### Día 3: Análisis de proyecto
1. Ejecuta: `/scan`
2. Revisa el resumen de tu proyecto
3. Pregunta sobre archivos específicos
4. Experimenta con diferentes comandos

### Semana 1: Uso avanzado
1. Prueba conversación natural
2. Usa el botón de micrófono
3. Explora plugins disponibles
4. Lee la documentación técnica si te interesa

---

## 📞 SOPORTE

### ¿Necesitas ayuda?
1. **Documentación**: Lee este archivo y `README_KALIN_V3.md`
2. **Logs**: Revisa `logs/kalin.log` para ver qué está pasando
3. **Health Check**: Visita http://localhost:5000/health para ver el estado del sistema
4. **GitHub Issues**: Reporta bugs en el repositorio

### Recursos adicionales:
- `SECURITY.md` - Documentación de seguridad completa
- `README_KALIN_V3.md` - Guía técnica detallada
- `AUDITORIA_SEGURIDAD_RESUMEN.md` - Resumen de auditorías

---

## ✅ CHECKLIST DE CONFIGURACIÓN

Antes de empezar, verifica:

- [ ] Python instalado (versión 3.8+)
- [ ] Kalin descargado
- [ ] Dependencias instaladas (`pip install ...`)
- [ ] Archivo `.env` configurado
- [ ] Ollama instalado y corriendo (si usas modo local)
- [ ] Servidor iniciado (`python run.py`)
- [ ] Navegador abierto en http://localhost:5000
- [ ] Proyecto configurado (`/setpath <ruta>`)

---

## 🌟 CONSEJOS PRO

1. **Usa conversaciones naturales**: Kalin entiende lenguaje cotidiano
2. **Sé específico**: "revisa main.py" es mejor que "revisa mi código"
3. **Revisa siempre los cambios**: Modo seguro te protege de errores
4. **Mantén proyectos organizados**: Kalin funciona mejor con código bien estructurado
5. **Actualiza regularmente**: `git pull` para obtener mejoras y parches de seguridad

---

**¡Disfruta programando con Kalin!** 🚀

*Tu asistente de programación inteligente, seguro y fácil de usar.*
