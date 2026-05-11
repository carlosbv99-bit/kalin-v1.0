# Guía de CI/CD y Testing - Kalin AI

Esta guía explica el sistema completo de CI/CD (Integración Continua / Despliegue Continuo) y testing implementado en Kalin AI.

## 📋 Tabla de Contenidos

1. [Tests Unitarios](#tests-unitarios)
2. [CI/CD Pipeline](#cicd-pipeline)
3. [Ejecutar Tests Localmente](#ejecutar-tests-localmente)
4. [Cobertura de Código](#cobertura-de-código)
5. [Licencia](#licencia)

---

## 🧪 Tests Unitarios

### Estructura de Tests

Los tests están organizados por módulo en la carpeta `tests/`:

```
tests/
├── test_patch_manager.py       # Tests del sistema de parches
├── test_orchestration_layer.py # Tests de la capa de orquestación
├── test_memory_manager.py      # Tests del gestor de memoria
└── ... (otros tests existentes)
```

### Ejecutar Todos los Tests

```bash
# Opción 1: Usar pytest directamente
pytest tests/ -v

# Opción 2: Usar script especializado
python run_all_tests.py

# Opción 3: Con cobertura
python run_all_tests.py --coverage --html-report
```

### Ejecutar Tests Específicos

```bash
# Solo tests unitarios del core
python run_all_tests.py --unit

# Un archivo específico
python run_all_tests.py --test test_patch_manager.py

# Modo verbose
python run_all_tests.py --verbose
```

### Tests Implementados

#### 1. **test_patch_manager.py** (15 tests)
- ✅ Crear snapshots
- ✅ Aplicar parches (INSERT, DELETE, REPLACE, APPEND)
- ✅ Revertir a snapshots anteriores
- ✅ Historial de parches
- ✅ Generar diffs
- ✅ Validación de regiones protegidas
- ✅ Múltiples parches secuenciales
- ✅ Manejo de errores

#### 2. **test_orchestration_layer.py** (25 tests)
- ✅ Inicialización
- ✅ Detección de intenciones (chat, create, fix, etc.)
- ✅ Detección de lenguaje (HTML, Python, JavaScript, Java, C)
- ✅ Extracción de código de respuestas
- ✅ Formateo de respuestas
- ✅ Bloqueo de lenguaje por sesión
- ✅ Revertir cambios
- ✅ Historial de cambios
- ✅ Estadísticas

#### 3. **test_memory_manager.py** (20 tests)
- ✅ Almacenar mensajes
- ✅ Historial con límites
- ✅ Limpieza de sesiones
- ✅ Estadísticas de sesión
- ✅ Metadata en mensajes
- ✅ Seguimiento de contexto
- ✅ Persistencia
- ✅ Sesiones concurrentes

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflows

El proyecto incluye 2 workflows automáticos:

#### 1. **ci-cd.yml** - Pipeline Principal

Se ejecuta en:
- Push a `main` o `develop`
- Pull requests a `main`

**Jobs incluidos:**

1. **test** - Ejecuta tests unitarios
   - Python 3.11 y 3.12
   - Genera reporte de cobertura
   - Sube a Codecov

2. **lint** - Análisis de código estático
   - Flake8 (errores críticos)
   - Black (formato)
   - Pylint (calidad)
   - MyPy (type checking)

3. **security** - Escaneo de seguridad
   - Bandit (vulnerabilidades en código)
   - Safety (dependencias vulnerables)

4. **build** - Validación de build
   - Verifica que la app inicia
   - Confirma archivos críticos

5. **docker** - Construcción de imagen Docker
   - Solo en push a main
   - Sube a Docker Hub (si está configurado)

6. **deploy** - Notificación de despliegue
   - Placeholder para despliegue real

#### 2. **auto-label.yml** - Etiquetado Automático

Aplica labels automáticamente según archivos modificados:
- `tests/` → label "tests"
- `*.md` → label "documentation"
- `static/`, `templates/` → label "frontend"
- `agent/`, `web.py` → label "backend"
- `.github/workflows/` → label "ci-cd"

### Configurar Secrets (Opcional)

Para habilitar todas las funcionalidades, configura estos secrets en GitHub:

1. Ve a: **Settings → Secrets and variables → Actions**
2. Agrega:

```
DOCKER_USERNAME=tu_usuario_docker
DOCKER_PASSWORD=tu_password_docker
SERVER_HOST=tu_servidor.com
SERVER_USER=ubuntu
SSH_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----...
```

---

## 💻 Ejecutar Tests Localmente

### Instalación de Dependencias

```bash
pip install pytest pytest-cov pytest-asyncio flake8 black pylint mypy
```

### Comandos Rápidos

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Solo tests del core
pytest tests/test_patch_manager.py tests/test_orchestration_layer.py tests/test_memory_manager.py -v

# Con cobertura
pytest tests/ --cov=agent --cov-report=html

# Abrir reporte HTML
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### Script Completo

```bash
python run_all_tests.py --coverage --html-report
```

Esto:
1. Instala dependencias si faltan
2. Ejecuta todos los tests
3. Genera reporte de cobertura
4. Abre el reporte en tu navegador

---

## 📊 Cobertura de Código

### Ver Cobertura Actual

```bash
# Terminal
pytest tests/ --cov=agent --cov-report=term-missing

# HTML interactivo
pytest tests/ --cov=agent --cov-report=html
start htmlcov/index.html
```

### Meta de Cobertura

- **Mínimo aceptable**: 70%
- **Objetivo**: 85%
- **Excelente**: 90%+

### Archivos Críticos a Cubrir

- ✅ `agent/core/patch_manager.py` - Sistema de parches
- ✅ `agent/core/orchestration_layer.py` - Orquestación
- ✅ `agent/core/memory_manager.py` - Memoria conversacional
- ⏳ `agent/core/tool_manager.py` - Gestión de tools
- ⏳ `agent/llm/client.py` - Cliente LLM

---

## 📄 Licencia

### Tipo: MIT License

El proyecto utiliza la licencia MIT, que permite:

✅ **Uso comercial**
✅ **Modificación**
✅ **Distribución**
✅ **Uso privado**

**Requisitos:**
- Incluir aviso de copyright original
- Incluir copia de la licencia

**Limitaciones:**
- Sin garantía
- Sin responsabilidad del autor

### Archivo: LICENSE

La licencia completa está en el archivo `LICENSE` en la raíz del proyecto.

---

## 🔍 Troubleshooting

### Error: "ModuleNotFoundError"

```bash
# Instalar dependencias
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Error: Tests fallan por dependencias externas

Algunos tests pueden requerir:
- API keys configuradas
- Servidores LLM disponibles
- Base de datos

**Solución:** Usa mocks o salta esos tests:
```bash
pytest tests/ -k "not llm and not integration"
```

### Error: Cobertura no se genera

```bash
# Instalar plugin
pip install pytest-cov

# Verificar versión
pytest --version
```

### GitHub Actions falla

1. Revisa logs en: **Actions → Job fallido → Logs**
2. Verifica que `requirements.txt` esté actualizado
3. Confirma que todos los imports son correctos

---

## 📈 Mejores Prácticas

### Para Developers

1. **Ejecutar tests antes de commit**
   ```bash
   python run_all_tests.py --unit
   ```

2. **Verificar cobertura de nuevos código**
   ```bash
   pytest tests/ --cov=agent/core/nuevo_modulo
   ```

3. **No commitear si tests fallan**
   - Corrige errores primero
   - Asegúrate de no romper tests existentes

### Para Maintainers

1. **Revisar CI/CD en cada PR**
   - Verifica que todos los jobs pasen
   - Revisa cobertura de código nueva

2. **Mantener tests actualizados**
   - Agrega tests para nuevas features
   - Actualiza tests cuando cambies APIs

3. **Monitorear métricas**
   - Cobertura de código
   - Tiempo de ejecución de tests
   - Número de tests passing/failing

---

## 🎯 Roadmap de Testing

### Pendiente

- [ ] Tests de integración completos
- [ ] Tests end-to-end (E2E)
- [ ] Tests de performance
- [ ] Tests de seguridad automatizados
- [ ] Mocks para proveedores LLM
- [ ] Tests de frontend (JavaScript)

### En Progreso

- [x] Tests unitarios del core ✅
- [x] CI/CD pipeline básico ✅
- [x] Licencia formal ✅
- [x] Reportes de cobertura ✅

---

## 📞 Soporte

¿Problemas con tests o CI/CD?

1. Revisa logs de error
2. Busca issues similares en GitHub
3. Crea un nuevo issue con:
   - Mensaje de error completo
   - Pasos para reproducir
   - Output de `pytest --version`

---

**Última actualización**: Mayo 2026
**Versión**: Kalin AI v3.0
