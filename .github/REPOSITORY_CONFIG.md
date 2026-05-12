# Configuración de Repository para GitHub
# Este archivo documenta la configuración recomendada para el repositorio

## 📋 Configuración de Página Principal

### Descripción del Repositorio (GitHub Description)
```
Kalin AI - IDE inteligente con asistente de código basado en IA. Genera, modifica y visualiza código en tiempo real mediante chat conversacional. Soporta Python, JavaScript, HTML/CSS, Java y más. Multi-proveedor LLM (Ollama, Groq, OpenAI).
```

### Website (opcional)
```
https://kalin-ai.example.com
```

### Topics/Tags
```
python, javascript, html, css, ide, artificial-intelligence, llm, code-editor, chatbot, ollama, flask, web-development, developer-tools, code-generation, real-time-preview, syntax-highlighting, multi-language
```

---

## 🏷️ Labels Recomendados

Crear los siguientes labels en GitHub Issues:

### Tipos
- `bug` - #d73a4a - Algo no funciona correctamente
- `enhancement` - #a2eeef - Nueva funcionalidad o mejora
- `documentation` - #0075ca - Mejoras en documentación
- `question` - #d876e3 - Pregunta o discusión
- `good first issue` - #7057ff - Bueno para principiantes

### Prioridad
- `priority: high` - #b60205 - Crítico, bloqueante
- `priority: medium` - #fbca04 - Importante
- `priority: low` - #0e8a16 - Nice to have

### Estado
- `status: needs-review` - #c2e0c6 - Esperando review
- `status: in-progress` - #fef2c0 - En desarrollo
- `status: blocked` - #e99695 - Bloqueado por algo

### Área
- `area: frontend` - #006b75 - UI/UX, JavaScript, CSS
- `area: backend` - #1d76db - Python, Flask, API
- `area: ai-ml` - #5319e7 - LLM, modelos, prompts
- `area: security` - #d93f0b - Seguridad, CSP, sandbox
- `area: performance` - #0052cc - Optimización, rendimiento

---

## 🛡️ Branch Protection Rules

### Branch: main

**Protecciones requeridas:**
- ✅ Require pull request reviews before merging
  - Required approvals: 1
  - Dismiss stale pull request approvals: ✅
  - Require review from Code Owners: ✅

- ✅ Require status checks to pass before merging
  - Status checks: ["tests", "lint"]
  
- ✅ Require conversation resolution before merging
- ✅ Include administrators: ✅
- ✅ Allow force pushes: ❌
- ✅ Allow deletions: ❌

---

## 📝 Issue Templates

### .github/ISSUE_TEMPLATE/bug_report.md
```markdown
---
name: Reporte de Bug
about: Crea un reporte para ayudarnos a mejorar
title: '[BUG] '
labels: bug
assignees: ''
---

**Descripción del Bug**
Una descripción clara y concisa del bug.

**Pasos para Reproducir**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Comportamiento Esperado**
Una descripción clara de lo que esperabas que sucediera.

**Capturas de Pantalla**
Si aplica, agrega capturas para explicar el problema.

**Environment:**
 - OS: [e.g. Windows 11, Ubuntu 22.04]
 - Python Version: [e.g. 3.9]
 - Browser: [e.g. Chrome 120, Firefox 119]
 - Kalin Version: [e.g. v1.1.1]

**Logs**
Si aplica, incluye logs relevantes.

**Contexto Adicional**
Agrega cualquier otro contexto sobre el problema.
```

### .github/ISSUE_TEMPLATE/feature_request.md
```markdown
---
name: Solicitud de Funcionalidad
about: Sugiere una idea para este proyecto
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor describe.**
Una descripción clara del problema. Ej: Siempre me frustro cuando [...]

**Describe la solución que te gustaría**
Una descripción clara de lo que quieres que suceda.

**Describe alternativas que has considerado**
Una descripción clara de soluciones o features alternativas que has considerado.

**Contexto Adicional**
Agrega cualquier otro contexto o capturas sobre la solicitud.
```

---

## 🤖 GitHub Actions Workflows

### .github/workflows/tests.yml
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=agent --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### .github/workflows/lint.yml
```yaml
name: Lint

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black pylint
    
    - name: Run flake8
      run: |
        flake8 agent/ --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Run black check
      run: |
        black --check agent/
    
    - name: Run pylint
      run: |
        pylint agent/ --fail-under=7.0
```

---

## 📊 Badges para README

Agregar al inicio de README.md:

```markdown
[![Tests](https://github.com/tu-usuario/kalin/actions/workflows/tests.yml/badge.svg)](https://github.com/tu-usuario/kalin/actions/workflows/tests.yml)
[![Lint](https://github.com/tu-usuario/kalin/actions/workflows/lint.yml/badge.svg)](https://github.com/tu-usuario/kalin/actions/workflows/lint.yml)
[![Coverage](https://codecov.io/gh/tu-usuario/kalin/branch/main/graph/badge.svg)](https://codecov.io/gh/tu-usuario/kalin)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v1.1-orange.svg)]()
[![Contributors](https://img.shields.io/github/contributors/tu-usuario/kalin)](https://github.com/tu-usuario/kalin/graphs/contributors)
[![Issues](https://img.shields.io/github/issues/tu-usuario/kalin)](https://github.com/tu-usuario/kalin/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
```

---

## 🔍 SEO Optimization

### Meta Tags para GitHub (automáticos)
GitHub genera automáticamente meta tags basados en:
- README.md (primera sección)
- Descripción del repositorio
- Topics/tags

### Preview Card
La preview card mostrará:
- Nombre: Kalin AI
- Descripción: Primera línea de la descripción
- Language: Python (detectado automáticamente)
- Stars, Forks, Issues count

---

## 📈 Analytics

### Opciones de Tracking

1. **GitHub Insights** (built-in)
   - Traffic graphs
   - Referrers
   - Popular content
   - Clone traffic

2. **External Analytics** (opcional)
   - Google Analytics en website
   - Plausible.io (privacy-focused)
   - Fathom Analytics

---

## ✅ Checklist Final de Configuración

- [x] README.md completo y descriptivo
- [x] DESCRIPTION configurado
- [x] TOPICS agregados
- [x] LICENSE presente (MIT)
- [x] CONTRIBUTING.md creado
- [x] CODE_OF_CONDUCT.md creado
- [x] SECURITY.md creado
- [x] CHANGELOG.md creado
- [ ] Labels creados en GitHub
- [ ] Branch protection rules configuradas
- [ ] Issue templates creadas
- [ ] GitHub Actions workflows activados
- [ ] Badges actualizados con URLs correctas
- [ ] Website URL configurado (si aplica)

---

**Última actualización**: 12 de Mayo, 2026
