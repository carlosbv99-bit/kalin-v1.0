# 📋 Instrucciones para Crear Copia Limpia de Kalin

## Método 1: Script Batch (Recomendado para Windows)

### Pasos:

1. **Abre una ventana de Command Prompt (CMD)**
   - Presiona `Win + R`
   - Escribe `cmd` y presiona Enter

2. **Navega al directorio de Kalin:**
   ```batch
   cd E:\kalin
   ```

3. **Ejecuta el script de copia limpia:**
   ```batch
   clean_copy_project.bat
   ```

4. **Espera a que termine**
   - El script creará una carpeta en `E:\kalin_clean_FECHA_HORA`
   - Solo copiará archivos esenciales
   - Excluirá: backups, __pycache__, logs, .gradle, etc.

5. **¡Listo!** La copia estará en una nueva carpeta con timestamp

---

## Método 2: Script Python

### Pasos:

1. **Abre PowerShell o CMD**

2. **Navega al directorio:**
   ```batch
   cd E:\kalin
   ```

3. **Ejecuta el script Python:**
   ```batch
   python clean_copy_project.py
   ```

4. **Sigue las instrucciones en pantalla**

---

## ¿Qué se incluye en la copia limpia?

### ✅ Archivos Incluidos:

#### Carpetas Esenciales:
- `agent/` - Núcleo del sistema Kalin
- `app/` - Aplicación Android
- `static/` - Archivos estáticos (CSS, JS, imágenes)
- `templates/` - Plantillas HTML
- `plugins/` - Plugins del sistema
- `gradle/` - Configuración de Gradle

#### Archivos Principales:
- `.env` - Configuración de entorno (con tus API keys)
- `.env.example` - Ejemplo de configuración
- `.gitignore` - Reglas de Git
- `requirements.txt` - Dependencias Python
- `web.py` - Servidor web principal
- `main.py` - Punto de entrada alternativo
- `run.py` - Script de ejecución
- `agent.py` - Lógica del agente
- `cli.py` - Interfaz de línea de comandos
- `README.md` - Documentación
- `SECURITY.md` - Políticas de seguridad
- `Dockerfile` - Configuración Docker
- `docker-compose.yml` - Docker Compose
- Archivos de Gradle (*.kts, *.properties)
- Scripts de Gradle (gradlew, gradlew.bat)

### ❌ Archivos Excluidos:

- `__pycache__/` - Caché de Python
- `.gradle/` - Caché de Gradle
- `.idea/` - Configuración de IDE
- `.kotlin/` - Caché de Kotlin
- `backups/` - Copias de seguridad antiguas
- `logs/` - Archivos de log
- `experience_memory/` - Memoria de experiencias
- `sessions/` - Sesiones temporales
- `*.log` - Archivos de log
- `*.pyc`, `*.pyo` - Bytecode de Python
- `node_modules/` - Módulos Node.js
- `.env.backup` - Backups de .env
- Archivos temporales (*.tmp, *.temp)

---

## Después de la Copia

### Para iniciar Kalin en la copia limpia:

```batch
cd E:\kalin_clean_YYYYMMDD_HHMMSS
python web.py
```

### Verificar que todo funcione:

1. Abre tu navegador en `http://localhost:5000`
2. Prueba los botones del menú de configuración
3. Verifica la conexión con Ollama
4. Revisa que no haya errores en la consola

---

## Ventajas de la Copia Limpia

✅ **Menor tamaño** - Sin archivos innecesarios  
✅ **Más rápida** - Sin cachés antiguos  
✅ **Portátil** - Fácil de compartir o respaldar  
✅ **Limpia** - Solo archivos esenciales  
✅ **Segura** - Sin datos temporales sensibles  

---

## Tamaño Estimado

- **Proyecto original:** ~500 MB - 2 GB (con backups y cachés)
- **Copia limpia:** ~50 - 150 MB (solo archivos esenciales)

**Reducción:** ~80-90% de espacio ahorrado

---

## Solución de Problemas

### Error: "No se encuentra el archivo"
- Verifica que estás en el directorio correcto: `cd E:\kalin`
- Asegúrate de que los scripts existen

### Error: "Acceso denegado"
- Ejecuta CMD como administrador
- Cierra cualquier proceso de Kalin que esté corriendo

### La copia no incluye mis modelos de Ollama
- Los modelos de Ollama están en otra ubicación (`~/.ollama/models`)
- Debes descargarlos nuevamente en la nueva instalación
- O copiar manualmente la carpeta de modelos de Ollama

### Error al iniciar Kalin en la copia
- Instala las dependencias: `pip install -r requirements.txt`
- Verifica que Ollama esté corriendo: `ollama serve`
- Revisa el archivo `.env` tenga la configuración correcta

---

## Notas Importantes

⚠️ **El archivo `.env` se copia tal cual** - Contiene tus API keys y configuraciones personales

⚠️ **Los modelos de Ollama NO se copian** - Debes descargarlos nuevamente o copiarlos manualmente desde `C:\Users\TU_USUARIO\.ollama\models`

⚠️ **Las sesiones y memoria conversacional NO se copian** - Empiezas con una instalación limpia

---

## Contacto

Si tienes problemas con la copia limpia, revisa:
- [SOLUCION_PROBLEMAS_OLLAMA.md](SOLUCION_PROBLEMAS_OLLAMA.md)
- [README.md](README.md)

---

**Última actualización:** Mayo 10, 2026  
**Versión:** Kalin v1.1+
