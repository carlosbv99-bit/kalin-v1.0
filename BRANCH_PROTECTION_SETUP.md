# Configuración de Branch Protection - Kalin AI

## 🛡️ Proteger Rama Principal

Para asegurar la calidad del código, configura **Branch Protection Rules** en GitHub.

---

## 📋 Pasos para Configurar

### 1. Ir a Settings del Repositorio

1. Ve a tu repositorio en GitHub
2. Click en **Settings** (pestaña superior)
3. En el menú lateral izquierdo, click en **Branches**
4. Click en **Add rule** o **Add branch protection rule**

### 2. Configurar Reglas para `main`

**Branch name pattern:**
```
main
```

**Activar las siguientes opciones:**

#### ✅ Require a pull request before merging
- [x] Require approvals: **1**
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require review from Code Owners (opcional)

#### ✅ Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- **Status checks requeridos:**
  - [x] `test (3.11)`
  - [x] `test (3.12)`
  - [x] `lint`
  - [x] `security`
  - [x] `build`

#### ✅ Require conversation resolution before merging
- [x] Todos los comentarios deben resolverse antes de merge

#### ✅ Include administrators
- [x] Aplicar reglas también a administradores (recomendado)

#### ✅ Restrict who can push to matching branches
- [ ] Opcional: Restringir push solo a maintainers

### 3. Guardar Cambios

Click en **Create** o **Save changes**

---

## 🔒 Reglas Adicionales Recomendadas

### Para Rama `develop` (si existe)

Repite el proceso para `develop` con las mismas reglas, excepto:
- Require approvals: **0** (más flexible en develop)
- Status checks: mismos que main

### Para Tags/Releases

**Branch name pattern:**
```
v*.*.*
```

**Reglas:**
- [x] Require a pull request before merging
- [x] Require status checks to pass
- [x] Include administrators

---

## 📊 Verificar Configuración

Después de configurar:

1. Intenta hacer push directo a main:
   ```bash
   git push origin main
   ```
   
   Deberías recibir error:
   ```
   remote: Protected branch update failed
   ```

2. Crea un PR y verifica que:
   - CI/CD se ejecuta automáticamente
   - No puedes hacer merge hasta que todos los checks pasen
   - Requiere al menos 1 aprobación (si configuraste)

---

## 🎯 Beneficios de Branch Protection

### Seguridad
- ❌ No se puede hacer push directo a main
- ✅ Todo cambio pasa por revisión
- ✅ Tests deben pasar obligatoriamente

### Calidad
- ✅ Código revisado por pares
- ✅ CI/CD valida cada cambio
- ✅ Sin merges rotos

### Trazabilidad
- ✅ Historial claro de cambios
- ✅ Reviews documentadas
- ✅ Checks visibles

---

## ⚙️ Configuración Avanzada (Opcional)

### CODEOWNERS File

Crea `.github/CODEOWNERS` para asignar reviewers automáticos:

```gitignore
# Archivo: .github/CODEOWNERS

# Default owners para todo el repo
*       @carlosbv99

# Agent core requiere revisión específica
agent/core/    @carlosbv99

# Frontend
static/        @carlosbv99
templates/     @carlosbv99

# CI/CD
.github/       @carlosbv99
```

### Required Reviewers

En settings del repositorio:
1. Settings → Branches → Branch protection rules
2. Edit regla de main
3. Activar: **Require review from Code Owners**

Ahora los archivos definidos en CODEOWNERS requerirán revisión automática.

---

## 🚨 Solución de Problemas

### Error: "Required status check 'test (3.11)' is expected"

**Causa**: El workflow no ha corrido aún o falló.

**Solución**:
1. Revisa Actions tab en GitHub
2. Espera a que termine el workflow
3. Si falló, corrige errores y haz push nuevamente

### Error: "At least 1 approving review is required"

**Causa**: No hay aprobaciones en el PR.

**Solución**:
1. Pide a otro developer que revise
2. O desactiva temporalmente "Require approvals" para testing

### No puedo hacer merge aunque todo pasó

**Causa**: Conversation resolution requerida.

**Solución**:
1. Revisa todos los comentarios en el PR
2. Resuelve conversaciones pendientes (click "Resolve conversation")
3. Intenta merge nuevamente

---

## 📝 Ejemplo de Flujo de Trabajo con Protection

```bash
# 1. Crear rama feature
git checkout -b feature/new-feature

# 2. Hacer cambios y commit
git add .
git commit -m "Add new feature with tests"

# 3. Push a GitHub
git push origin feature/new-feature

# 4. Crear Pull Request en GitHub UI
#    - Título descriptivo
#    - Descripción de cambios
#    - Link a issues relacionados

# 5. Esperar CI/CD (automático)
#    - Tests corren
#    - Linting verifica
#    - Security scan

# 6. Obtener approval de reviewer

# 7. Merge (botón habilitado cuando todo esté verde)

# 8. Borrar rama feature (GitHub lo sugiere)
```

---

## 🔗 Recursos

- **GitHub Docs**: [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- **Best Practices**: [Branching strategies](https://www.atlassian.com/git/tutorials/comparing-workflows)

---

**Configuración recomendada para**: Kalin AI v3.0+  
**Nivel de protección**: Alto (producción)
