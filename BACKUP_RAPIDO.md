# Guía Rápida: Backup Limpio para GitHub

## 🎯 Objetivo

Hacer un backup limpio del proyecto a GitHub, eliminando archivos temporales y caché.

---

## 📋 Pasos Simplificados

### Opción 1: Script Automático (Recomendado)

```bash
# Ejecutar el script de backup automático
python backup_limpio.py
```

Este script hace TODO automáticamente:
1. ✅ Limpia `__pycache__` y archivos `.pyc`
2. ✅ Elimina logs antiguos
3. ✅ Agrega cambios a Git
4. ✅ Crea commit con mensaje descriptivo
5. ✅ Crea tag de versión
6. ✅ Hace push a GitHub (con confirmación)

---

### Opción 2: Manual Paso a Paso

Si prefieres control total:

#### Paso 1: Limpiar el proyecto
```bash
python prepare_for_testing.py
```

#### Paso 2: Verificar cambios
```bash
git status
```

#### Paso 3: Agregar todos los cambios
```bash
git add .
```

#### Paso 4: Crear commit
```bash
git commit -m "🔧 Mejoras en generación HTML y soporte Linux

- Aumentados tokens para HTML (800→1200)
- Timeout Ollama aumentado (30s→120s)
- Limpieza HTML más conservadora
- Scripts Linux/Mac creados (.sh)
- Validaciones relajadas para modelos locales"
```

#### Paso 5: Crear tag (opcional)
```bash
git tag -a v1.0.0-mejoras-html -m "Versión con mejoras HTML"
```

#### Paso 6: Subir a GitHub
```bash
git push origin main --tags
```

---

## 🔍 Verificar el Backup

### Después del backup, verifica:

```bash
# Ver últimos commits
git log --oneline -5

# Ver tags
git tag -l

# Ver estado
git status
```

### En GitHub:
1. Ve a tu repositorio: https://github.com/carlosbv99/kalin
2. Verifica que los últimos cambios estén subidos
3. Revisa que los archivos nuevos estén presentes:
   - `iniciar_kalin.sh`
   - `instalar_linux.sh`
   - `GUIA_LINUX_PRINCIPIANTES.md`
   - `README_LINUX.md`
   - `backup_limpio.py`

---

## 📦 Archivos que NO se suben (gitignore)

Estos archivos están excluidos automáticamente:

```
✅ __pycache__/
✅ *.pyc
✅ .venv/
✅ logs/*.log (archivos grandes)
✅ sessions/ (datos privados)
✅ cache/
✅ .env (claves API - ¡NUNCA subir!)
✅ .idea/
```

---

## ⚠️ Problemas Comunes

### Error: "No remote configured"

**Solución:**
```bash
# Agregar remoto
git remote add origin https://github.com/carlosbv99/kalin.git

# Verificar
git remote -v

# Subir
git push -u origin main --tags
```

### Error: "Authentication failed"

**Solución:**
```bash
# Usar token de GitHub en lugar de contraseña
# Generar token en: https://github.com/settings/tokens

# Luego usar:
git push https://TOKEN@github.com/carlosbv99/kalin.git main --tags
```

### Error: "Nothing to commit"

**Significa:** No hay cambios nuevos desde el último commit.

**Verificar:**
```bash
git status
```

---

## 💡 Consejos

### 1. Hacer backup antes de cambios grandes
```bash
python backup_limpio.py
```

### 2. Mensajes de commit descriptivos
```bash
# Mal
git commit -m "cambios"

# Bien
git commit -m "🔧 Aumentados tokens HTML para mejor generación de código"
```

### 3. Tags semánticos
```bash
# Formato: vMAJOR.MINOR.PATCH-descripción
git tag -a v1.0.1-fix-html -m "Corrección generación HTML"
```

### 4. Verificar antes de hacer push
```bash
# Ver qué se va a subir
git diff --cached --stat

# Ver commits pendientes
git log origin/main..HEAD --oneline
```

---

## 🚀 Flujo Recomendado

```bash
# 1. Trabajar en el proyecto
# ... haces cambios ...

# 2. Probar que todo funciona
python run.py
# ... pruebas en el navegador ...

# 3. Limpiar y hacer backup
python backup_limpio.py

# 4. Verificar en GitHub
# Abre: https://github.com/carlosbv99/kalin
```

---

## 📊 Resumen de Cambios Recientes

Los siguientes cambios están listos para backup:

### ✅ Archivos Nuevos:
- `iniciar_kalin.sh` - Script inicio Linux/Mac
- `instalar_linux.sh` - Instalador automático Linux
- `GUIA_LINUX_PRINCIPIANTES.md` - Guía completa Linux
- `README_LINUX.md` - Referencia rápida Linux
- `backup_limpio.py` - Script backup automático
- `DIAGNOSTICO_PROBLEMAS_HTML.md` - Diagnóstico técnico

### ✅ Archivos Modificados:
- `agent/actions/tools/fix_tool.py`
  - Tokens HTML: 800 → 1200
  - Limpieza comentarios más conservadora
  
- `agent/llm/providers/ollama_provider.py`
  - Timeout: 30s → 120s

### ✅ Archivos Eliminados:
- Todos los `.bat` y `.ps1` (reemplazados por Python)

---

## 🎯 Comando Rápido

Para hacer backup rápido en el futuro:

```bash
# Una línea
python backup_limpio.py

# O si ya tienes git configurado
git add . && git commit -m "Backup $(date +%Y-%m-%d)" && git push
```

---

**¡Listo! Tu proyecto está limpio y respaldado en GitHub** 🎉
