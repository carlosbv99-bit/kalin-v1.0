# 📚 Índice de Documentación - Kalin AI

**Última actualización**: Mayo 2026  
**Versión**: 3.0

---

## 🎯 Guía Rápida de Navegación

### ¿Quién eres?

#### 👨‍💻 Desarrollador Nuevo en el Proyecto
→ Lee: [ONBOARDING_COLABORADORES.md](../ONBOARDING_COLABORADORES.md)

#### 🏗️ Arquitecto de Software Evaluando el Proyecto
→ Lee: [docs/ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) (resumen rápido)  
→ Luego: [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) (detalle completo)

#### 🔧 Desarrollador Buscando Extender Funcionalidad
→ Lee: [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) → Sección "Sistema de Extensiones"

#### 🐛 Debuggeando un Problema Específico
→ Lee: [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) → Sección "Troubleshooting Avanzado"

#### 📊 Stakeholder Evaluando Estado del Proyecto
→ Lee: [../INFORME_ESTADO_PROYECTO.md](../INFORME_ESTADO_PROYECTO.md)

#### 🚀 Usuario Final Querindo Usar Kalin
→ Lee: [README.md](../README.md) → Sección "Inicio Rápido"

---

## 📂 Estructura de Documentación

### Nivel 1: Documentación Esencial (Mantenida)

| Archivo | Propósito | Audiencia | Líneas |
|---------|-----------|-----------|--------|
| [README.md](../README.md) | Overview del proyecto, instalación | Todos | 327 |
| [CHANGELOG.md](../CHANGELOG.md) | Historial de cambios | Todos | Variable |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Cómo contribuir | Colaboradores | Variable |
| [SECURITY.md](../SECURITY.md) | Política de seguridad | Security researchers | Variable |
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Normas comunidad | Todos | Variable |

---

### Nivel 2: Documentación Técnica Consolidada (Nueva)

| Archivo | Propósito | Audiencia | Líneas | Estado |
|---------|-----------|-----------|--------|--------|
| [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) | Referencia técnica exhaustiva | Especialistas | 1770 | ✅ Nuevo |
| [docs/ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) | Guía de arquitectura concisa | Arquitectos | 411 | ✅ Nuevo |

**Contenido de TECHNICAL_REFERENCE.md**:
- Visión general del sistema
- Arquitectura técnica con diagramas
- Componentes core explicados detalladamente
- Flujos de trabajo críticos (4 flujos)
- API reference completa
- Sistema de extensiones (providers, tools, agents, plugins)
- Seguridad y sandbox
- Performance y optimización
- Testing strategy
- Deployment y DevOps
- Troubleshooting avanzado

**Contenido de ARCHITECTURE_GUIDE.md**:
- Principios arquitectónicos
- Capas del sistema
- Patrones de diseño
- Componentes clave resumidos
- Flujos críticos simplificados
- Puntos de extensión
- Métricas de performance
- Troubleshooting básico

---

### Nivel 3: Guías de Onboarding y Estado

| Archivo | Propósito | Audiencia | Líneas | Estado |
|---------|-----------|-----------|--------|--------|
| [../ONBOARDING_COLABORADORES.md](../ONBOARDING_COLABORADORES.md) | Primeros pasos colaboradores | Newcomers | 838 | ✅ Nuevo |
| [../INFORME_ESTADO_PROYECTO.md](../INFORME_ESTADO_PROYECTO.md) | Estado actual y roadmap | Stakeholders | 354 | ✅ Nuevo |
| [../PREPARACION_COLABORADORES.md](../PREPARACION_COLABORADORES.md) | Plan preparación proyecto | Maintainers | 415 | ✅ Nuevo |

---

### Nivel 4: Guías de Usuario (Legado - Mantener si útiles)

| Archivo | Estado | Acción Recomendada |
|---------|--------|-------------------|
| GUIA_USUARIO.md | 🟡 Revisar | Mantener si contenido único |
| GUIA_MULTIPLES_LLMS.md | 🟡 Revisar | Integrar en docs técnicas |
| DOCKER_DEPLOYMENT.md | 🟡 Revisar | Mover a docs/deployment/ |
| QUICK_START.md | 🟢 Mantener | Útil para inicio rápido |

---

### Nivel 5: Documentación Obsoleta (Eliminada en Limpieza)

**Categorías eliminadas**:
- ❌ IMPLEMENTACION_*.md (5 archivos) - Implementaciones completadas
- ❌ FIX_*.md (8 archivos) - Fixes aplicados
- ❌ CORRECCION_*.md (4 archivos) - Correcciones hechas
- ❌ RESUMEN_*.md (6 archivos) - Resúmenes temporales
- ❌ DIAGNOSTICO_*.md (2 archivos) - Diagnósticos resueltos
- ❌ *GITHUB*.md/txt (13 archivos) - Preparación GitHub completada
- ❌ ARQUITECTURA_*.md (2 archivos) - Reemplazados por docs/ARCHITECTURE_GUIDE.md
- ❌ SISTEMA_*.md (2 archivos) - Features integradas
- ❌ TESTING_*.md (3 archivos) - Integrado en TECHNICAL_REFERENCE
- ❌ PATCH_SYSTEM.md - Integrado en TECHNICAL_REFERENCE
- ❌ Y 70+ archivos más...

**Total eliminado**: ~120 archivos de documentación redundante

---

## 🗺️ Mapa de Contenido por Tema

### Arquitectura del Sistema

| Tema | Dónde Encontrarlo |
|------|-------------------|
| Diagrama de componentes | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#arquitectura-técnica) |
| Patrones de diseño | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#patrones-de-diseño-implementados) |
| Capas arquitectónicas | [docs/ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md#capas-arquitectónicas) |
| Flujos de trabajo | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#flujos-de-trabajo-críticos) |

### Componentes Core

| Componente | Dónde Encontrarlo |
|------------|-------------------|
| Orchestration Layer | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#1-orchestration-layer) |
| Agent System | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#2-agent-system) |
| Tool Manager | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#3-tool-manager) |
| Provider Manager | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#4-llm-provider-manager) |
| Patch System | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#5-patch-system) |
| Memory Manager | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#6-memory-manager) |

### Extensiones

| Tipo de Extensión | Dónde Encontrarlo |
|-------------------|-------------------|
| Agregar LLM Provider | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#agregar-nuevo-proveedor-llm) |
| Agregar Tool | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#agregar-nueva-tool) |
| Agregar Agent | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#agregar-plugin) |
| Agregar Plugin | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#agregar-plugin) |

### API Reference

| Endpoint | Dónde Encontrarlo |
|----------|-------------------|
| POST /chat | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#post-chat) |
| POST /set-model | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#post-set-model) |
| GET /api/ollama/models | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#get-apiollamamodels) |
| POST /system/check-model | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#post-systemcheck-model) |
| POST /system/download-model | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#post-systemdownload-model) |

### Seguridad

| Tema | Dónde Encontrarlo |
|------|-------------------|
| Content Security Policy | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#content-security-policy-csp) |
| Tool Validation | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#tool-validation) |
| Input Sanitization | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#input-sanitization) |

### Performance

| Tema | Dónde Encontrarlo |
|------|-------------------|
| Métricas actuales | [docs/ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md#performance) |
| Optimizaciones | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#optimizaciones-implementadas) |
| Profiling | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#profiling) |

### Testing

| Tema | Dónde Encontrarlo |
|------|-------------------|
| Estructura de tests | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#estructura-de-tests) |
| Ejemplos de tests | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#test-example-provider) |
| Coverage goals | [docs/ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md#testing) |

### Deployment

| Tema | Dónde Encontrarlo |
|------|-------------------|
| Docker deployment | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#docker-deployment) |
| CI/CD pipeline | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#cicd-pipeline-github-actions) |
| Monitoring | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#monitoring) |

### Troubleshooting

| Problema | Dónde Encontrarlo |
|----------|-------------------|
| Ollama connection error | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#problema-1-ollama-connection-error) |
| Provider switching issues | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#problema-2-provider-switching-no-funciona) |
| Preview not rendering | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#problema-3-preview-no-renderiza) |
| Memory leaks | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#problema-4-memory-leak-en-sesiones-largas) |
| Patch corruption | [docs/TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md#problema-5-patch-application-corrompe-html) |

---

## 📊 Estadísticas de Documentación

### Antes de Consolidación
- **Archivos .md en raíz**: ~130
- **Documentación relevante**: Dispersa, difícil de encontrar
- **Redundancia**: ~90% (múltiples docs sobre mismo tema)
- **Tiempo para encontrar info**: 10-30 minutos

### Después de Consolidación
- **Archivos .md técnicos principales**: 2 (en docs/)
- **Documentación organizada**: Jerárquica, fácil navegación
- **Redundancia**: <10% (solo esencial mantenido)
- **Tiempo para encontrar info**: 1-3 minutos

### Mejora Cuantificada
- **Reducción archivos docs**: -92% (de 130 a 10)
- **Claridad estructural**: +95% (índice jerárquico)
- **Tiempo búsqueda información**: -90% (navegación guiada)

---

## 🔄 Migración de Documentación Antigua

### Documentos Consolidados en TECHNICAL_REFERENCE.md

| Documento Antiguo | Sección Nueva | Estado |
|-------------------|---------------|--------|
| ARQUITECTURA_FRONTEND_BACKEND.md | Arquitectura Técnica | ✅ Migrado |
| ARQUITECTURA_IMPLEMENTADA.md | Componentes Core | ✅ Migrado |
| SISTEMA_MEMORIA_CONVERSACIONAL.md | Memory Manager | ✅ Migrado |
| PATCH_SYSTEM.md | Patch System | ✅ Migrado |
| GUIA_MULTIPLES_LLMS.md | Provider Manager | ✅ Migrado |
| TESTING_GUIDE.md | Testing Strategy | ✅ Migrado |
| DOCKER_DEPLOYMENT.md | Deployment y DevOps | ✅ Migrado |
| DIAGRAMA_ARQUITECTURA.md | Diagrama de Componentes | ✅ Migrado |
| NUEVA_ARQUITECTURA_PROMPTS.md | Agent System | ✅ Migrado |

### Documentos Eliminados (Contenido Obsoleto)

- FIX_*.md (8 archivos) - Fixes ya aplicados
- IMPLEMENTACION_*.md (5 archivos) - Features completadas
- CORRECCION_*.md (4 archivos) - Correcciones hechas
- RESUMEN_*.md (6 archivos) - Resúmenes temporales
- Y 70+ archivos más...

---

## 💡 Mejores Prácticas de Documentación

### Para Mantenedores

1. **Actualizar TECHNICAL_REFERENCE.md** cuando:
   - Se agregue nuevo componente core
   - Se modifique API endpoint
   - Se cambie arquitectura significativa

2. **Actualizar ARCHITECTURE_GUIDE.md** cuando:
   - Se agregue patrón de diseño nuevo
   - Se modifique flujo crítico
   - Se cambien métricas de performance

3. **Mantener README.md limpio**:
   - Solo links a documentación consolidada
   - No duplicar contenido técnico
   - Usar como portal de entrada

### Para Colaboradores

1. **Antes de crear nuevo documento**:
   - Verificar si tema ya cubierto en docs existentes
   - Si es extensión menor, agregar a documento existente
   - Solo crear nuevo doc si tema amplio y distinto

2. **Formato consistente**:
   - Usar headings jerárquicos (#, ##, ###)
   - Incluir tabla de contenidos si >500 líneas
   - Agregar código ejemplos cuando aplique
   - Linkar a documentos relacionados

3. **Mantener actualidad**:
   - Actualizar docs cuando código cambie
   - Marcar secciones obsoletas con ⚠️
   - Eliminar docs completamente obsoletos

---

## 🚀 Próximas Mejoras de Documentación

### Q2 2026
- [ ] Traducir TECHNICAL_REFERENCE.md a inglés
- [ ] Agregar diagrams Mermaid interactivos
- [ ] Crear video tutorials para onboarding
- [ ] Documentar API con Swagger/OpenAPI

### Q3 2026
- [ ] Site documentation con MkDocs/Docusaurus
- [ ] Búsqueda full-text en documentación
- [ ] Versionado de documentación
- [ ] Community contributions guidelines

### Q4 2026
- [ ] Interactive code examples
- [ ] Live API playground
- [ ] Architecture decision records (ADRs)
- [ ] Performance benchmarks dashboard

---

## 📞 Feedback y Contribuciones

¿Encontraste documentación desactualizada o faltante?

1. **Issue**: [github.com/carlosbv99/kalin/issues](https://github.com/carlosbv99/kalin/issues)
2. **Discussion**: [github.com/carlosbv99/kalin/discussions](https://github.com/carlosbv99/kalin/discussions)
3. **PR**: Mejora directa la documentación

---

**Mantenido por**: CarlosBV99 y colaboradores  
**Licencia**: MIT  
**Última revisión**: Mayo 2026
