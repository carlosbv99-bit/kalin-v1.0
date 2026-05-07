# Guía de Uso - Kalin AI

## Scripts Disponibles

Todos los scripts ahora están escritos en **Python** para mayor seguridad y compatibilidad multiplataforma. Los archivos `.bat` y `.ps1` han sido eliminados para evitar alertas de antivirus.

### 1. Iniciar Kalin

```bash
python iniciar_kalin.py
```

Este script:
- Verifica que Python esté instalado
- Activa el entorno virtual (si existe)
- Inicia el servidor de Kalin en http://localhost:5000

### 2. Backup a GitHub

```bash
python backup_github.py
```

O con mensaje personalizado:

```bash
python backup_github.py -m "Mi mensaje de commit"
```

Este script:
- Verifica e inicializa el repositorio Git
- Configura el usuario de Git
- Crea/verifica el archivo .gitignore
- Agrega todos los archivos al staging
- Crea un commit con timestamp
- Crea un tag de versión
- Opción de hacer push a GitHub

### 3. Ejecutar Tests

```bash
python run_tests.py
```

Este script:
- Limpia el proyecto
- Ejecuta la suite completa de tests
- Si los tests pasan, inicia el servidor automáticamente

## ¿Por qué se eliminaron los archivos .bat y .ps1?

Los archivos batch (.bat) y PowerShell (.ps1) pueden generar **falsos positivos** en los antivirus porque:

1. Son scripts ejecutables que los antivirus monitorean de cerca
2. Contienen comandos del sistema que pueden parecer sospechosos
3. Muchos usuarios desconfían al descargar repositorios con estos archivos
4. No son multiplataforma (solo funcionan en Windows)

## Ventajas de los scripts Python

✅ **Multiplataforma**: Funcionan en Windows, macOS y Linux  
✅ **Sin alertas de antivirus**: Python es considerado seguro  
✅ **Más flexibles**: Fácil de modificar y extender  
✅ **Mismo funcionalidad**: Reemplazan exactamente las funciones anteriores  

## Comandos Alternativos Directos

Si prefieres usar comandos directos de Git:

```bash
# Verificar estado
git status

# Agregar cambios
git add .

# Crear commit
git commit -m "Tu mensaje"

# Crear tag
git tag -a v1.0.0 -m "Versión 1.0.0"

# Push a GitHub
git push origin main --tags
```

## Solución de Problemas

### Error: "Python no encontrado"
Instala Python desde: https://www.python.org/downloads/

### Error: "Git no encontrado"
Instala Git desde: https://git-scm.com/downloads

### Error: "No module named 'flask'"
Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Soporte

Para más información, consulta:
- `README.md` - Documentación principal
- `GUIA_USUARIO.md` - Guía completa del usuario
- `TESTING_GUIDE.md` - Guía de testing
