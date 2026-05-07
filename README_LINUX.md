# Kalin AI - Guía Rápida para Linux

## 🚀 Inicio Rápido (3 pasos)

### 1. Instalación Automática

```bash
# Descarga o clona el repositorio
git clone https://github.com/carlosbv99/kalin.git
cd kalin

# Ejecuta el instalador automático
chmod +x instalar_linux.sh
./instalar_linux.sh
```

El script hará todo por ti:
- ✅ Instala Python y dependencias del sistema
- ✅ Crea entorno virtual
- ✅ Instala paquetes de Python
- ✅ Configura archivo .env
- ✅ Te guía para agregar tu clave API

### 2. Iniciar Kalin

```bash
./iniciar_kalin.sh
```

O alternativamente:
```bash
source .venv/bin/activate
python3 iniciar_kalin.py
```

### 3. Abrir en el Navegador

Abre: **http://localhost:5000**

---

## 📋 Requisitos

- **Python 3.8+** (el instalador lo verifica)
- **Git** (para backups)
- **2GB espacio en disco**
- **Conexión a internet** (para IA)

### Distribuciones Soportadas

✅ Ubuntu / Debian / Linux Mint  
✅ Fedora  
✅ Arch Linux / Manjaro  
✅ Cualquier distro con Python 3.8+

---

## 📚 Documentación Completa

Para una guía detallada paso a paso, consulta:

👉 **[GUIA_LINUX_PRINCIPIANTES.md](GUIA_LINUX_PRINCIPIANTES.md)**

Incluye:
- Instalación manual paso a paso
- Solución de problemas comunes
- Comandos útiles de Linux
- Consejos para principiantes
- Uso básico de Git y Python

---

## 🔧 Comandos Principales

### Instalación
```bash
./instalar_linux.sh              # Instalación automática completa
```

### Uso Diario
```bash
./iniciar_kalin.sh               # Iniciar Kalin
python3 backup_github.py         # Backup a GitHub
python3 run_tests.py             # Ejecutar tests
```

### Gestión del Entorno
```bash
source .venv/bin/activate        # Activar entorno virtual
deactivate                       # Desactivar entorno virtual
pip install -r requirements.txt  # Instalar dependencias
```

### Actualización
```bash
git pull                         # Descargar actualizaciones
pip install -r requirements.txt  # Actualizar dependencias
```

---

## ⚙️ Configuración

### Agregar Clave API

Edita el archivo `.env`:
```bash
nano .env
```

Descomenta y agrega tu clave:
```env
OPENAI_API_KEY=sk-tu_clave_aqui
# O
ANTHROPIC_API_KEY=sk-ant-tu_clave_aqui
# O
QWEN_API_KEY=tu_clave_aqui
```

**Obtén claves gratuitas:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Qwen: https://help.aliyun.com/

---

## ❓ Problemas Comunes

### Error: "Permission denied"
```bash
chmod +x iniciar_kalin.sh
chmod +x instalar_linux.sh
```

### Error: "Module not found"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Usa otro puerto
export PORT=5001
python3 iniciar_kalin.py
```

### Python versión antigua
```bash
# Ubuntu
sudo apt install python3.10 python3.10-venv

# O usa pyenv
curl https://pyenv.run | bash
pyenv install 3.10.12
```

---

## 📁 Estructura de Archivos

```
kalin/
├── instalar_linux.sh          # Instalador automático
├── iniciar_kalin.sh           # Script de inicio
├── iniciar_kalin.py           # Script de inicio (Python)
├── backup_github.py           # Backup a GitHub
├── run_tests.py               # Ejecutar tests
├── GUIA_LINUX_PRINCIPIANTES.md # Guía completa
├── README_LINUX.md            # Este archivo
├── requirements.txt           # Dependencias Python
├── .env                       # Configuración (crear)
└── .venv/                     # Entorno virtual (auto-generado)
```

---

## 💡 Consejos

1. **Siempre activa el entorno virtual** antes de usar Kalin
2. **Haz backups regulares** con `python3 backup_github.py`
3. **Mantén Kalin actualizado** con `git pull`
4. **Revisa los logs** si hay errores: `cat logs/kalin.log`
5. **Lee la documentación** completa en `GUIA_LINUX_PRINCIPIANTES.md`

---

## 🆘 Obtener Ayuda

1. **Revisa la guía**: `GUIA_LINUX_PRINCIPIANTES.md`
2. **Ver logs**: `tail -f logs/kalin.log`
3. **Reportar issues**: https://github.com/carlosbv99/kalin/issues

---

## 🎯 Flujo de Trabajo Típico

```bash
# Al empezar a trabajar
cd ~/proyectos/kalin
source .venv/bin/activate
./iniciar_kalin.sh

# En el navegador: http://localhost:5000
# Trabaja con Kalin AI...

# Cuando termines: Ctrl+C en la terminal

# Hacer backup de cambios
python3 backup_github.py

# Cuando vuelvas a trabajar, repite desde arriba
```

---

## 🌟 Características

- ✅ Asistente de programación con IA
- ✅ Análisis de código inteligente
- ✅ Generación automática de código
- ✅ Detección y corrección de errores
- ✅ Backup automático a GitHub
- ✅ Soporte multi-idioma
- ✅ Interfaz web intuitiva
- ✅ Multiplataforma (Linux, macOS, Windows)

---

## 📖 Más Información

- **README.md** - Documentación principal del proyecto
- **GUIA_DE_USO.md** - Guía de uso de scripts
- **TESTING_GUIDE.md** - Guía de testing
- **Web oficial**: (agregar URL cuando esté disponible)

---

**¡Disfruta programando con Kalin AI! 🚀**

*Hecho con ❤️ para la comunidad Linux*
