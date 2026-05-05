# 🧪 Guía para Ejecutar Tests en Kalin

## 📋 Resumen

Se han reparado todos los errores críticos en los tests del proyecto Kalin. Esta guía te muestra cómo ejecutarlos.

---

## 🚀 Opción 1: Ejecutar Todos los Tests (Recomendado)

### En Windows (CMD):
```cmd
run_tests.bat
```

### En Windows (PowerShell):
```powershell
.\run_tests.ps1
```

**Nota:** Si PowerShell bloquea la ejecución, ejecuta primero:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## 🔍 Opción 2: Ejecutar Tests Individualmente

### Paso 1: Verificar Reparaciones
```bash
python verify_repairs.py
```
✅ Confirma que todas las reparaciones se aplicaron correctamente

### Paso 2: Diagnosticar Imports
```bash
python diagnose_imports.py
```
✅ Verifica que todos los módulos se pueden importar

### Paso 3: Tests Funcionales
```bash
python test_funcional.py
```
✅ Prueba: Brain, State Manager, Web App, Orchestrator

### Paso 4: Tests de Proveedores LLM
```bash
python test_llm_providers.py
```
✅ Prueba: Configuración LLM, Provider Manager, estadísticas

### Paso 5: Tests de Nueva Arquitectura
```bash
python test_new_architecture.py
```
✅ Prueba: StateManager, RetryEngine, ProjectAnalyzer, Strategies

### Paso 6: Tests de Componentes v2.0
```bash
python test_new_components.py
```
✅ Prueba: Logger, Conversation Manager, Security, Cache, Commands

### Paso 7: Tests de Endpoints (Requiere Servidor)
Primero inicia el servidor en otra terminal:
```bash
python run.py
```

Luego en otra terminal:
```bash
python test_endpoints.py
```
✅ Prueba: Health check, LLM status, comandos via HTTP

---

## 📊 Qué Esperar

### ✅ Si Todo Sale Bien:
```
========================================
RESUMEN FINAL
========================================
Todos los tests han sido ejecutados.
¡Todos los tests pasaron correctamente!
========================================
```

### ⚠️ Si Hay Errores Menores:
Algunos tests pueden fallar si:
- **Ollama no está corriendo**: Los tests de LLM mostrarán advertencias (normal)
- **No hay API keys configuradas**: Algunos proveedores LLM no estarán disponibles (normal)
- **El servidor no está activo**: test_endpoints.py se saltará automáticamente

### ❌ Si Hay Errores Críticos:
Si `verify_repairs.py` o `diagnose_imports.py` fallan:
1. Revisa el error mostrado
2. Asegúrate de tener Python instalado
3. Instala dependencias: `pip install -r requirements.txt`
4. Vuelve a intentar

---

## 🛠️ Requisitos Previos

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

Paquetes clave instalados:
- flask>=2.3.0
- flask-cors>=4.0.0
- requests>=2.31.0
- python-dotenv>=1.0.0

### 2. (Opcional) Configurar Ollama para Tests LLM
Si quieres probar con Ollama local:
```bash
# Instalar Ollama desde https://ollama.com
ollama serve
ollama pull deepseek-coder:6.7b
```

### 3. (Opcional) Configurar Variables de Entorno
Crea un archivo `.env` basado en `.env.example`:
```env
KALIN_MODE=local
OLLAMA_ENDPOINT=http://127.0.0.1:11434
# OPENAI_API_KEY=sk-... (opcional)
# ANTHROPIC_API_KEY=sk-ant-... (opcional)
```

---

## 📝 Archivos de Test Disponibles

| Archivo | Descripción | Requiere Servidor |
|---------|-------------|-------------------|
| `verify_repairs.py` | Verifica reparaciones aplicadas | ❌ No |
| `diagnose_imports.py` | Diagnóstico de imports | ❌ No |
| `test_funcional.py` | Tests funcionales básicos | ❌ No |
| `test_llm_providers.py` | Tests de proveedores LLM | ❌ No |
| `test_new_architecture.py` | Tests arquitectura v2.0 | ❌ No |
| `test_new_components.py` | Tests componentes v2.0 | ❌ No |
| `test_endpoints.py` | Tests de endpoints REST | ✅ Sí |

---

## 🔧 Problemas Comunes y Soluciones

### Problema: "ModuleNotFoundError: No module named 'flask'"
**Solución:**
```bash
pip install flask flask-cors
```

### Problema: "test_endpoints.py falla"
**Causa:** El servidor no está corriendo
**Solución:**
```bash
# Terminal 1
python run.py

# Terminal 2
python test_endpoints.py
```

### Problema: Los tests de LLM muestran "No hay proveedor disponible"
**Causa:** Ollama no está corriendo o no hay API keys configuradas
**Solución:** Esto es normal en desarrollo. Los otros tests seguirán funcionando.

### Problema: "Permission denied" en PowerShell
**Solución:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run_tests.ps1
```

---

## 📈 Interpretación de Resultados

### ✅ Test Pasó:
- El componente funciona correctamente
- No hay errores de importación
- La lógica es válida

### ⚠️ Test con Advertencias:
- Funciona pero con limitaciones (ej: sin LLM disponible)
- Puede mejorar con configuración adicional

### ❌ Test Falló:
- Error crítico que debe corregirse
- Revisa el mensaje de error específico
- Consulta los logs en la carpeta `logs/`

---

## 🎯 Próximos Pasos Después de los Tests

1. **Si todos los tests pasan:**
   ```bash
   python run.py
   ```
   Inicia el servidor web y accede a http://127.0.0.1:5000

2. **Si algunos tests fallan:**
   - Revisa los mensajes de error
   - Consulta los logs en `logs/kalin_errors.log`
   - Ejecuta `python verify_repairs.py` para confirmar reparaciones

3. **Para desarrollo continuo:**
   - Los tests se pueden ejecutar antes de cada commit
   - Usa `python diagnose_imports.py` después de agregar nuevos módulos

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa `REPARACIONES_TESTS.md` para ver qué se reparó
2. Consulta los logs en `logs/`
3. Ejecuta `python verify_repairs.py` para diagnóstico rápido

---

**Última actualización:** 2026-05-05
**Estado:** ✅ Todos los tests reparados y listos para ejecutar
