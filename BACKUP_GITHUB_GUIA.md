# 📦 Guía de Backup Versionado en GitHub - Kalin

## 🎯 Objetivo

Crear un backup versionado del proyecto Kalin en GitHub con todas las reparaciones de tests realizadas.

---

## 🚀 Opción 1: Backup Automático (Recomendado)

### En Windows (PowerShell):
```powershell
.\backup_github.ps1
```

### En Windows (CMD):
```cmd
backup_github.bat
```

**El script automáticamente:**
1. ✅ Inicializa repositorio Git (si no existe)
2. ✅ Configura usuario Git
3. ✅ Crea/verifica .gitignore
4. ✅ Agrega todos los archivos
5. ✅ Crea commit descriptivo
6. ✅ Crea tag de versión
7. ✅ Ofrece hacer push a GitHub

---

## 🔧 Opción 2: Backup Manual Paso a Paso

### Paso 1: Inicializar Repositorio (si no existe)
```bash
cd E:\kalin
git init
```

### Paso 2: Configurar Usuario Git
```bash
git config user.name "Tu Nombre"
git config user.email "tu@email.com"
```

### Paso 3: Verificar .gitignore
El archivo `.gitignore` ya está creado y configurado para excluir:
- Archivos temporales de Python (`__pycache__/`, `*.pyc`)
- Entornos virtuales (`venv/`, `.venv/`)
- Logs (`logs/`)
- Cache (`cache/`)
- Sesiones (`sessions/`)
- Variables de entorno (`.env`)
- Archivos de IDE (`.idea/`, `.vscode/`)

### Paso 4: Agregar Archivos
```bash
git add .
```

### Paso 5: Crear Commit
```bash
git commit -m "🔧 Reparaciones de tests y mejoras del sistema

Reparaciones realizadas:
- ✅ requirements.txt: Agregadas dependencias Flask y flask-cors
- ✅ test_funcional.py: Corregido test del Orchestrator
- ✅ agent/core/retry_engine.py: Corregido método _heuristic
- ✅ agent/core/cache.py: Corregida llamada a load_from_disk()
- ✅ test_endpoints.py: Agregada validación de servidor

Nuevos archivos:
- Scripts de ejecución automática de tests
- Documentación completa de reparaciones
- Guías de uso

Estado: Todos los tests reparados y listos para ejecutar"
```

### Paso 6: Crear Tag de Versión
```bash
# Formato: v1.0.0-tests-fixed-YYYYMMDD-HHMM
git tag -a v1.0.0-tests-fixed-20260505-2300 -m "Versión con todos los tests reparados"
```

### Paso 7: Configurar Remoto GitHub (Primera vez)
```bash
# Reemplaza con tu URL de repositorio
git remote add origin https://github.com/TU_USUARIO/kalin.git
```

### Paso 8: Push a GitHub
```bash
git push -u origin main --tags
```

Si tu rama principal se llama `master`:
```bash
git push -u origin master --tags
```

---

## 📋 Archivos Incluidos en el Backup

### 📝 Código Principal
- `agent/` - Todo el código del agente IA
- `web.py` - Aplicación web Flask
- `run.py` - Script de inicio
- `main.py` - Entry point

### 🧪 Tests y Verificación
- `test_funcional.py`
- `test_llm_providers.py`
- `test_new_architecture.py`
- `test_new_components.py`
- `test_endpoints.py`
- `verify_repairs.py`
- `diagnose_imports.py`
- `run_all_tests.py`

### 📚 Documentación
- `README_KALIN_V3.md`
- `GUIA_TESTS.md`
- `REPARACIONES_TESTS.md`
- `GUIA_USUARIO.md`
- `QUICK_START.md`
- Y más documentos...

### ⚙️ Configuración
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `Dockerfile`
- `docker-compose.yml`

### 🛠️ Scripts de Utilidad
- `run_tests.bat`
- `run_tests.ps1`
- `backup_github.bat`
- `backup_github.ps1`

---

## 🏷️ Sistema de Versionado

### Tags Automáticos
Los scripts crean tags con el formato:
```
v1.0.0-tests-fixed-YYYYMMDD-HHMM
```

Ejemplo:
```
v1.0.0-tests-fixed-20260505-2300
```

### Ver Tags Existentes
```bash
git tag -l
```

### Ver Detalles de un Tag
```bash
git show v1.0.0-tests-fixed-20260505-2300
```

---

## 🔄 Flujo de Trabajo Recomendado

### Antes de Hacer Cambios
```bash
# 1. Verificar estado
git status

# 2. Traer últimos cambios (si trabajas en equipo)
git pull origin main
```

### Después de Hacer Cambios
```bash
# 1. Agregar cambios
git add .

# 2. Crear commit descriptivo
git commit -m "✨ Descripción del cambio"

# 3. Push a GitHub
git push origin main
```

### Para Releases Importantes
```bash
# Crear tag semántico
git tag -a v1.1.0 -m "Nueva versión con feature X"

# Push con tags
git push origin main --tags
```

---

## 🌐 Configurar Repositorio GitHub

### Si No Tienes Repositorio Creado:

1. **Crear repositorio en GitHub:**
   - Ve a https://github.com/new
   - Nombre: `kalin`
   - Descripción: "Agente IA autónomo para reparación y generación de código"
   - Privado o Público (según prefieras)
   - NO inicializar con README, .gitignore o license

2. **Agregar remoto local:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/kalin.git
   ```

3. **Renombrar rama (opcional):**
   ```bash
   git branch -M main
   ```

4. **Push inicial:**
   ```bash
   git push -u origin main --tags
   ```

### Si Ya Tienes Repositorio:
```bash
# Solo agrega el remoto y haz push
git remote add origin https://github.com/TU_USUARIO/kalin.git
git push -u origin main --tags
```

---

## 🔐 Autenticación GitHub

### Opción 1: HTTPS con Personal Access Token (PAT)
1. Generar token en: https://github.com/settings/tokens
2. Usar el token como contraseña al hacer push

### Opción 2: SSH (Recomendado)
```bash
# Generar clave SSH
ssh-keygen -t ed25519 -C "tu@email.com"

# Agregar clave a GitHub
# Copiar contenido de ~/.ssh/id_ed25519.pub
# Pegar en: https://github.com/settings/keys

# Cambiar remoto a SSH
git remote set-url origin git@github.com:TU_USUARIO/kalin.git
```

---

## 📊 Ver Estado del Repositorio

### Ver Historial de Commits
```bash
git log --oneline
```

### Ver Cambios Pendientes
```bash
git status
```

### Ver Diferencias
```bash
git diff
```

### Ver Tags
```bash
git tag -l
```

### Ver Remotos
```bash
git remote -v
```

---

## 🚨 Solución de Problemas

### Problema: "fatal: remote origin already exists"
**Solución:**
```bash
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/kalin.git
```

### Problema: "failed to push some refs"
**Solución:**
```bash
git pull origin main --rebase
git push origin main --tags
```

### Problema: "tag already exists"
**Solución:**
```bash
# Borrar tag local
git tag -d v1.0.0-tests-fixed-20260505-2300

# Crear nuevo tag con timestamp diferente
git tag -a v1.0.0-tests-fixed-20260505-2301 -m "Nuevo tag"
```

### Problema: "permission denied"
**Solución:**
- Verifica que tienes acceso al repositorio
- Regenera tu Personal Access Token
- O configura autenticación SSH

---

## 📁 Estructura del Repositorio

```
kalin/
├── .git/                    # Repositorio Git
├── .gitignore              # Archivos ignorados
├── agent/                  # Código del agente
│   ├── core/              # Componentes principales
│   ├── llm/               # Proveedores LLM
│   └── actions/           # Acciones y comandos
├── tests/                 # Tests (archivos sueltos)
├── logs/                  # Logs (ignorados)
├── cache/                 # Cache (ignorado)
├── sessions/              # Sesiones (ignoradas)
├── docs/                  # Documentación
├── scripts/               # Scripts de utilidad
└── README.md              # Documentación principal
```

---

## 🎯 Mejores Prácticas

### 1. Commits Atómicos
```bash
# ✅ Bien: Un cambio por commit
git add requirements.txt
git commit -m "📦 Agregadas dependencias Flask"

git add test_funcional.py
git commit -m "🧪 Corregido test del orchestrator"
```

### 2. Mensajes Descriptivos
```bash
# ❌ Mal
git commit -m "fix"

# ✅ Bien
git commit -m "🔧 Corregido método _heuristic en RetryEngine

El método ahora retorna el código incluso sin modificaciones,
evitando que código válido sea descartado."
```

### 3. Tags Semánticos
```bash
# Versión mayor.minor.patch
v1.0.0  # Release inicial
v1.1.0  # Nueva funcionalidad
v1.1.1  # Bug fix
v2.0.0  # Cambio breaking
```

### 4. Branches para Features
```bash
# Crear rama para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# Trabajar en la rama
# ...

# Merge a main
git checkout main
git merge feature/nueva-funcionalidad
```

---

## 📈 Estadísticas del Repositorio

### Ver Tamaño del Repositorio
```bash
git count-objects -vH
```

### Ver Contribuidores (futuro)
```bash
git shortlog -sn --all
```

### Ver Líneas de Código
```bash
git ls-files | xargs wc -l
```

---

## 🔄 Backup Periódico

### Crear Alias para Backup Rápido
```bash
# Agregar a ~/.bashrc o perfil de PowerShell
function kalin-backup {
    cd E:\kalin
    git add .
    git commit -m "💾 Backup automático - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
    git push origin main
}
```

### Usar:
```bash
kalin-backup
```

---

## 📞 Soporte

Si tienes problemas:
1. Verifica que Git esté instalado: `git --version`
2. Verifica conexión a GitHub: `ping github.com`
3. Revisa credenciales: `git config --list`
4. Consulta logs: `.git/logs/`

---

**Última actualización:** 2026-05-05  
**Estado:** ✅ Scripts de backup creados y listos para usar
