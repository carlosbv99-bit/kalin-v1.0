# Guía Completa para Principiantes - Kalin AI en Linux

## 📚 Tabla de Contenidos

1. [¿Qué es Kalin AI?](#qué-es-kalin-ai)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Primeros Pasos](#primeros-pasos)
5. [Uso Básico](#uso-básico)
6. [Solución de Problemas](#solución-de-problemas)
7. [Comandos Útiles](#comandos-útiles)

---

## ¿Qué es Kalin AI?

Kalin AI es un **asistente de programación inteligente** que te ayuda a:
- Escribir código más rápido
- Analizar y entender proyectos
- Corregir errores automáticamente
- Generar documentación
- Hacer backup de tu código a GitHub

Funciona como una aplicación web que corre en tu computadora, así que puedes usarla desde cualquier navegador.

---

## Requisitos del Sistema

### Hardware Mínimo
- **Procesador**: Dual-core 2GHz o superior
- **RAM**: 4GB (8GB recomendado)
- **Disco**: 2GB de espacio libre
- **Internet**: Necesario para las funciones de IA

### Software Necesario
- **Sistema Operativo**: Linux (Ubuntu, Fedora, Arch, etc.)
- **Python 3.8 o superior**
- **Git** (para backups)
- **Navegador web**: Chrome, Firefox, Edge, etc.

---

## Instalación Paso a Paso

### Paso 1: Abrir la Terminal

Presiona `Ctrl + Alt + T` o busca "Terminal" en el menú de aplicaciones.

### Paso 2: Verificar si tienes Python instalado

Escribe este comando y presiona Enter:

```bash
python3 --version
```

**Si ves algo como `Python 3.10.12`**, ¡perfecto! Pasa al Paso 3.

**Si dice "comando no encontrado"**, necesitas instalar Python:

#### Para Ubuntu/Debian/Linux Mint:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

#### Para Fedora:
```bash
sudo dnf install python3 python3-pip git
```

#### Para Arch Linux/Manjaro:
```bash
sudo pacman -S python python-pip git
```

### Paso 3: Descargar Kalin AI

Ve a la página de GitHub del proyecto y descarga el código:

```bash
# Navega a donde quieras guardar Kalin (ejemplo: carpeta Descargas)
cd ~/Descargas

# Clona el repositorio (cambia la URL por la correcta)
git clone https://github.com/carlosbv99/kalin.git

# Entra en la carpeta
cd kalin
```

**Opción alternativa**: Si descargaste un archivo ZIP:
```bash
# Descomprime el archivo
unzip kalin-main.zip
cd kalin-main
```

### Paso 4: Crear Entorno Virtual (Recomendado)

Un entorno virtual mantiene las dependencias de Kalin separadas de tu sistema:

```bash
python3 -m venv .venv
```

Esto crea una carpeta llamada `.venv` con todo lo necesario.

### Paso 5: Activar el Entorno Virtual

```bash
source .venv/bin/activate
```

Verás que aparece `(.venv)` al inicio de tu terminal. ¡Significa que está activo!

### Paso 6: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto puede tardar unos minutos. Espera a que termine completamente.

### Paso 7: Configurar Variables de Entorno

Crea un archivo `.env` con tus claves API:

```bash
nano .env
```

Agrega estas líneas (reemplaza con tus claves reales):

```env
# Elige UNO de estos proveedores de IA:
OPENAI_API_KEY=tu_clave_de_openai_aqui
# O
ANTHROPIC_API_KEY=tu_clave_de_anthropic_aqui
# O
QWEN_API_KEY=tu_clave_de_qwen_aqui

# Puerto del servidor (puedes dejarlo así)
PORT=5000
```

Guarda con `Ctrl + O`, presiona Enter, y sal con `Ctrl + X`.

**¿No tienes clave API?** Puedes obtener una gratuita en:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Qwen: https://help.aliyun.com/

### Paso 8: ¡Iniciar Kalin!

#### Opción A: Usando el script (Fácil)

Primero, haz el script ejecutable:
```bash
chmod +x iniciar_kalin.sh
```

Luego ejecútalo:
```bash
./iniciar_kalin.sh
```

#### Opción B: Usando Python directamente

```bash
python3 iniciar_kalin.py
```

### Paso 9: Abrir en el Navegador

Cuando veas el mensaje "Abre tu navegador en: http://localhost:5000":

1. Abre tu navegador (Chrome, Firefox, etc.)
2. Escribe en la barra de direcciones: `http://localhost:5000`
3. ¡Listo! Verás la interfaz de Kalin AI

---

## Primeros Pasos

### Tu Primera Conversación con Kalin

1. En la interfaz web, verás un cuadro de chat
2. Escribe algo como: `"Hola Kalin, ayúdame a crear un programa en Python"`
3. Kalin responderá y te guiará

### Ejemplos de Comandos

Puedes pedirle a Kalin que:

```
📝 "Crea un archivo llamado hola.py que imprima 'Hola Mundo'"
🔍 "Analiza mi proyecto y dime qué mejoras puedo hacer"
🐛 "Encuentra errores en mi código Python"
📊 "Genera documentación para mi proyecto"
💾 "Haz backup de mis cambios a GitHub"
```

### Trabajar con Archivos Existentes

Para que Kalin trabaje con tus archivos:

1. Coloca tus archivos en la carpeta de Kalin
2. En el chat, escribe: `"Analiza el archivo mi_archivo.py"`
3. Kalin leerá el archivo y te dará sugerencias

---

## Uso Básico

### Iniciar Kalin (cada vez que lo uses)

```bash
cd ~/Descargas/kalin          # Navega a la carpeta
source .venv/bin/activate     # Activa el entorno virtual
./iniciar_kalin.sh            # Inicia Kalin
```

### Detener Kalin

En la terminal donde está corriendo Kalin, presiona:
```
Ctrl + C
```

### Actualizar Kalin

Si hay nuevas versiones:

```bash
cd ~/Descargas/kalin
git pull                      # Descarga actualizaciones
pip install -r requirements.txt  # Actualiza dependencias
```

### Hacer Backup a GitHub

```bash
python3 backup_github.py
```

Te preguntará si quieres subir los cambios a GitHub.

---

## Solución de Problemas

### ❌ Error: "Permission denied" al ejecutar el script

**Solución:**
```bash
chmod +x iniciar_kalin.sh
./iniciar_kalin.sh
```

### ❌ Error: "ModuleNotFoundError: No module named 'flask'"

**Solución:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### ❌ Error: "Address already in use"

**Solución:** Alguien más está usando el puerto 5000.
```bash
# Encuentra el proceso
lsof -i :5000

# Mata el proceso (cambia PID por el número que veas)
kill -9 PID

# O usa otro puerto
export PORT=5001
python3 iniciar_kalin.py
```

### ❌ Kalin no responde o es muy lento

**Posibles causas:**
1. **Sin conexión a internet** - Verifica tu conexión
2. **Clave API incorrecta** - Revisa tu archivo `.env`
3. **Poco RAM** - Cierra otras aplicaciones

**Solución:**
```bash
# Verifica tu archivo .env
cat .env

# Revisa los logs para ver errores
cat logs/kalin.log
```

### ❌ Error de Git al hacer backup

**Solución:**
```bash
# Configura tu nombre y email
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Inicializa el repositorio si no existe
git init

# Agrega el remoto de GitHub
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
```

### ❌ El entorno virtual no se activa

**Solución:**
```bash
# Verifica que existe
ls -la .venv/bin/activate

# Si no existe, créalo de nuevo
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### ❌ Python versión antigua

Kalin necesita Python 3.8 o superior.

**Verifica tu versión:**
```bash
python3 --version
```

**Si es menor a 3.8**, instala una versión más nueva:
```bash
# Ubuntu
sudo apt install python3.10 python3.10-venv python3.10-pip
python3.10 -m venv .venv

# O usa pyenv para múltiples versiones
curl https://pyenv.run | bash
pyenv install 3.10.12
pyenv local 3.10.12
```

---

## Comandos Útiles

### Gestión del Entorno Virtual

```bash
# Activar
source .venv/bin/activate

# Desactivar
deactivate

# Ver paquetes instalados
pip list

# Instalar un paquete nuevo
pip install nombre_paquete
```

### Git Básico

```bash
# Ver estado de archivos
git status

# Agregar todos los cambios
git add .

# Crear commit
git commit -m "Descripción de los cambios"

# Subir a GitHub
git push origin main

# Ver historial
git log --oneline
```

### Sistema de Archivos

```bash
# Ver contenido de carpeta
ls -la

# Navegar a carpeta
cd nombre_carpeta

# Volver atrás
cd ..

# Ir a tu home
cd ~

# Crear carpeta
mkdir nombre_carpeta

# Copiar archivo
cp archivo_origen archivo_destino

# Mover/renombrar archivo
mv archivo_viejo archivo_nuevo

# Eliminar archivo (¡cuidado!)
rm nombre_archivo
```

### Monitoreo del Sistema

```bash
# Ver procesos de Python
ps aux | grep python

# Ver uso de memoria
free -h

# Ver espacio en disco
df -h

# Ver puertos en uso
netstat -tulpn | grep 5000
```

### Logs de Kalin

```bash
# Ver logs recientes
tail -f logs/kalin.log

# Ver últimos 50 mensajes
tail -n 50 logs/kalin.log

# Buscar errores
grep ERROR logs/kalin.log
```

---

## Consejos para Principiantes

### 💡 Tip 1: Mantén Kalin Actualizado
```bash
# Una vez al mes, actualiza
cd ~/Descargas/kalin
git pull
pip install -r requirements.txt
```

### 💡 Tip 2: Usa Entornos Virtuales
Siempre activa el entorno virtual antes de usar Kalin:
```bash
source .venv/bin/activate
```

### 💡 Tip 3: Haz Backups Regulares
```bash
# Cada vez que hagas cambios importantes
python3 backup_github.py
```

### 💡 Tip 4: Lee los Logs si Hay Problemas
```bash
# Los logs te dicen qué está pasando
cat logs/kalin.log
```

### 💡 Tip 5: Usa Atajos de Terminal
- `Tab` - Autocompletar comandos
- `Ctrl + R` - Buscar comandos anteriores
- `Ctrl + C` - Cancelar comando actual
- `Ctrl + L` - Limpiar pantalla
- Flechas arriba/abajo - Historial de comandos

### 💡 Tip 6: Documenta Tus Cambios
Cuando uses Git, escribe mensajes claros:
```bash
# Mal
git commit -m "cambios"

# Bien
git commit -m "Agregué función de análisis de código Python"
```

### 💡 Tip 7: Explora la Documentación
```bash
# Lee los archivos de ayuda
ls *.md
cat README.md
cat GUIA_DE_USO.md
```

---

## Recursos Adicionales

### Documentación de Kalin
- `README.md` - Información general del proyecto
- `GUIA_DE_USO.md` - Cómo usar los scripts
- `TESTING_GUIDE.md` - Guía de testing
- `CAMBIOS_SEGURIDAD_SCRIPTS.md` - Cambios recientes

### Aprender Más
- **Python**: https://docs.python.org/es/3/tutorial/
- **Git**: https://git-scm.com/book/es/v2
- **Linux básico**: https://ubuntu.com/tutorials/command-line-for-beginners

### Comunidad
- **GitHub Issues**: Reporta bugs o pide características
- **Stack Overflow**: Preguntas técnicas sobre Python/Git
- **Foros de Linux**: Ayuda específica de tu distribución

---

## Soporte

Si tienes problemas:

1. **Revisa los logs**: `cat logs/kalin.log`
2. **Busca en la documentación**: Los archivos `.md` tienen mucha información
3. **Reporta el problema**: Crea un issue en GitHub con:
   - Tu sistema operativo y versión
   - Versión de Python (`python3 --version`)
   - El mensaje de error completo
   - Qué estabas haciendo cuando ocurrió

---

## Resumen Rápido

```bash
# Instalación inicial (una sola vez)
git clone https://github.com/carlosbv99/kalin.git
cd kalin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
nano .env  # Agrega tu clave API

# Uso diario
cd ~/Descargas/kalin
source .venv/bin/activate
./iniciar_kalin.sh
# Abre http://localhost:5000 en tu navegador

# Backup
python3 backup_github.py
```

---

**¡Feliz programación con Kalin AI! 🚀**

Si esta guía te fue útil, considera contribuir al proyecto o compartirlo con otros desarrolladores.
