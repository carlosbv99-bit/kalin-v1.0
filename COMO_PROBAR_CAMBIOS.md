# 🧪 Cómo Probar los Cambios - Guía Rápida

## Resumen Ejecutivo

Hemos implementado 4 mejoras principales:
1. ✅ **Modelo único**: Solo deepseek-coder (ahorra ~7GB RAM)
2. ✅ **Debug completo**: Ver prompts y respuestas del LLM
3. ✅ **Experience Memory**: Kalin aprende de la experiencia
4. ✅ **Limpieza de disco**: Script automático para liberar espacio

---

## 🚀 Prueba Rápida (5 minutos)

### Paso 1: Ejecutar Suite Completa de Tests

```bash
cd E:\kalin
python test_all_changes.py
```

**Esto verifica automáticamente:**
- ✅ Configuración del modelo único
- ✅ Sistema de debug
- ✅ Experience Memory
- ✅ Nuevos comandos (/experience, /learn)
- ✅ Script de limpieza
- ✅ Documentación

**Resultado esperado:**
```
🎉 ¡EXCELENTE! Todas las pruebas pasaron.

✨ Cambios implementados exitosamente:
   1. ✅ Modelo único: deepseek-coder para todo
   2. ✅ Sistema de debug completo
   3. ✅ Experience Memory funcional
   4. ✅ Nuevos comandos /experience y /learn
   5. ✅ Script de limpieza de disco
   6. ✅ Documentación completa
```

---

## 📋 Pruebas Individuales

### Prueba 1: Verificar Configuración del Modelo

```bash
python test_configuracion.py
```

**Qué verifica:**
- OLLAMA_CHAT eliminado
- Solo usa deepseek-coder
- Variables de entorno correctas

---

### Prueba 2: Probar Modo Debug

#### Activar Debug
Edita `.env`:
```env
KALIN_DEBUG=1
```

#### Iniciar Servidor
```bash
python run.py
```

#### Ver Logs Detallados
Ahora cuando uses `/fix archivo.py`, verás en consola:

```
================================================================================
🔍 [ANALYZER] PROMPT ENVIADO AL LLM:
================================================================================
Eres un experto en programación.
Analiza este código...
================================================================================

================================================================================
📥 [ANALYZER] RESPUESTA RECIBIDA DEL LLM:
================================================================================
El código tiene un error...
================================================================================

================================================================================
🛠️ [FIX_TOOL] PROMPT DE GENERACIÓN:
================================================================================
...
================================================================================

================================================================================
📥 [FIX_TOOL] RESPUESTA RAW DEL MODELO:
================================================================================
Longitud: 245 chars
Primeros 500 chars:
...
================================================================================

================================================================================
✅ [FIX_TOOL] CÓDIGO FINAL PARSEADO:
================================================================================
def hello():
    print("world")
================================================================================
```

---

### Prueba 3: Probar Experience Memory

#### Desde la Interfaz Web

1. Inicia el servidor:
   ```bash
   python run.py
   ```

2. Abre: http://localhost:5000

3. Usa comandos de fix varias veces:
   ```
   /fix main.py
   /fix utils.py
   ```

4. Consulta la experiencia:
   ```
   /experience
   ```

**Respuesta esperada:**
```
🧠 Memoria de Aprendizaje

📊 Experiencias totales: 5
✅ Éxitos: 4
❌ Fallos: 1
📈 Tasa de éxito global: 80.0%

🎯 Por tipo de tarea:
• fix: 80.0% éxito (5 intentos)

💡 Insights:
• Mejor estrategia: smart (85% éxito)
• Tarea más exitosa: fix (80% éxito)
```

5. Consulta patrones aprendidos:
   ```
   /learn
   ```

#### Desde API

```bash
# Ver resumen de experiencia
curl http://localhost:5000/experience

# Ver patrones detectados
curl http://localhost:5000/experience/patterns
```

---

### Prueba 4: Probar Limpieza de Disco

#### Ejecutar Script Interactivo

```bash
python clean_disk_space.py
```

**Te preguntará qué quieres limpiar:**
- Logs antiguos (>7 días)
- Sesiones antiguas (>30 días)
- Cache de Python
- Archivos .bak
- Caché de Gradle

#### Limpieza de Modelos Ollama (Libera 5-15 GB)

```bash
# Ver modelos instalados
ollama list

# Eliminar modelos que NO usas
ollama rm qwen2.5:7b        # Libera ~4 GB
ollama rm llama3.2          # Libera ~2 GB
ollama rm codellama:7b      # Libera ~3.8 GB

# Mantén SOLO este:
ollama pull deepseek-coder:latest
```

---

## 🔍 Pruebas Manuales en la Interfaz

### Test 1: Comando /fix con Debug

1. Asegúrate que `KALIN_DEBUG=1` en `.env`
2. Inicia servidor: `python run.py`
3. En la web, ejecuta: `/fix algun_archivo.py`
4. Revisa la consola donde corre Flask
5. Deberías ver todos los prompts y respuestas detalladas

### Test 2: Comandos de Experiencia

En la interfaz web prueba:

```
/experience
```
Debe mostrar estadísticas de aprendizaje

```
/learn
```
Debe mostrar patrones detectados

```
muéstrame tu experiencia
```
Debe funcionar en lenguaje natural

```
qué patrones has aprendido
```
También debe funcionar

### Test 3: Verificar Uso de Memoria

Antes (con 2 modelos):
```bash
# Ver procesos de Ollama
tasklist | findstr ollama
# Deberías ver 2+ procesos usando ~14GB RAM
```

Después (con 1 modelo):
```bash
# Reinicia Ollama
ollama serve

# Ver procesos
tasklist | findstr ollama
# Deberías ver 1 proceso usando ~7GB RAM
```

---

## 📊 Verificación de Espacio Liberado

### Antes y Después

```powershell
# Ver espacio libre en disco
Get-PSDrive C | Select-Object Used,Free

# Ver tamaño de la carpeta Kalin
Get-ChildItem E:\kalin -Recurse | Measure-Object -Property Length -Sum
```

### Espacio Esperado Liberado

| Concepto | Espacio |
|----------|---------|
| Un modelo Ollama menos | ~7 GB RAM |
| Models no usados eliminados | 5-15 GB disco |
| Limpieza proyecto | 200-900 MB |
| **Total potencial** | **~12-22 GB** |

---

## ✅ Checklist de Verificación

### Configuración
- [ ] `.env` tiene `OLLAMA_MODEL=deepseek-coder:latest`
- [ ] `.env` tiene `OLLAMA_CHAT_MODEL=deepseek-coder:latest`
- [ ] `.env` tiene `KALIN_DEBUG=1` (para testing)
- [ ] No hay referencia a `llama3.2` en ningún lado

### Código
- [ ] `agent/llm/config.py` no tiene `ProviderType.OLLAMA_CHAT`
- [ ] `agent/llm/provider_manager.py` solo inicializa 3 providers
- [ ] `agent/analyzer.py` tiene código de debug
- [ ] `agent/actions/tools/fix_tool.py` tiene código de debug
- [ ] `agent/llm/provider_manager.py` tiene código de debug

### Funcionalidad
- [ ] `python test_all_changes.py` pasa todas las pruebas
- [ ] `/experience` funciona en la web
- [ ] `/learn` funciona en la web
- [ ] Debug muestra prompts en consola
- [ ] Debug muestra respuestas en consola

### Archivos
- [ ] Existe `clean_disk_space.py`
- [ ] Existe `EXPERIENCE_MEMORY_GUIDE.md`
- [ ] Existe `DEBUG_GUIDE.md`
- [ ] Existe `LIMPIEZA_DISCO.md`
- [ ] Existe `CAMBIOS_MODELO_UNICO.md`

---

## 🐛 Solución de Problemas

### Problema: "OLLAMA_CHAT still exists"

**Solución:**
```bash
# Verifica el archivo config.py
grep -n "OLLAMA_CHAT" agent/llm/config.py

# Si existe, elimina la sección manualmente
# Busca entre líneas 38-45 y elimina el bloque OLLAMA_CHAT
```

### Problema: Debug no muestra nada

**Solución:**
```bash
# Verifica que KALIN_DEBUG=1
cat .env | grep DEBUG

# Reinicia el servidor
# Ctrl+C para detener
python run.py
```

### Problema: Experience Memory no registra

**Solución:**
```bash
# Verifica que la carpeta existe
ls experience_memory/

# Si no existe, crea manualmente
mkdir experience_memory

# Reinicia el servidor
```

### Problema: Script de limpieza falla

**Solución:**
```bash
# Ejecuta con permisos de administrador
# Windows: Click derecho en PowerShell > Ejecutar como administrador
python clean_disk_space.py
```

---

## 📝 Pruebas Avanzadas

### Test de Rendimiento

```python
# Crear archivo test_performance.py
import time
from agent.llm.client import generate

start = time.time()
response = generate("Escribe una función simple en Python", max_tokens=100)
end = time.time()

print(f"Tiempo de respuesta: {end - start:.2f} segundos")
print(f"Longitud respuesta: {len(response)} caracteres")
```

### Test de Memory Leak

```bash
# Monitorea uso de RAM mientras usas Kalin
# Windows Task Manager > Performance > Memory

# Usa Kalin intensivamente por 10 minutos
# El uso de RAM debería mantenerse estable (~7GB para Ollama)
```

---

## 🎯 Próximos Pasos Después de Probar

1. **Si todo funciona:**
   - Desactiva debug para producción: `KALIN_DEBUG=0`
   - Elimina modelos Ollama no usados
   - Ejecuta limpieza de disco completa

2. **Monitoreo continuo:**
   - Revisa `/experience` semanalmente
   - Ejecuta `clean_disk_space.py` mensualmente
   - Monitorea uso de RAM

3. **Optimización adicional:**
   - Considera SSD si usas HDD
   - Amplía RAM si tienes <16GB
   - Usa Docker para aislamiento

---

## 📞 ¿Necesitas Ayuda?

Si algo no funciona:

1. Revisa los logs en `logs/kalin.log`
2. Ejecuta `python test_all_changes.py` para diagnóstico
3. Verifica que Ollama esté corriendo: `ollama list`
4. Revisa esta guía paso a paso

---

## ✨ Resumen

Para probar TODO rápidamente:

```bash
# 1. Ejecutar tests automáticos
python test_all_changes.py

# 2. Iniciar servidor con debug
python run.py

# 3. En otra terminal, probar comandos
curl http://localhost:5000/experience
curl http://localhost:5000/experience/patterns

# 4. Limpiar disco
python clean_disk_space.py

# 5. Eliminar modelos Ollama viejos
ollama rm qwen2.5:7b
ollama rm llama3.2
```

**¡Listo! Tu Kalin está optimizado y funcionando** 🎉
