#!/bin/bash
# Kalin AI - Script de instalación automática para Linux
# Este script instala todo lo necesario para ejecutar Kalin

set -e  # Salir si hay errores

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  KALIN AI - INSTALACION AUTOMATICA PARA LINUX${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Detectar distribución
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo -e "${RED}No se pudo detectar la distribucion de Linux${NC}"
    exit 1
fi

echo -e "${YELLOW}Distribucion detectada: $DISTRO${NC}"
echo ""

# Paso 1: Verificar dependencias del sistema
echo -e "${CYAN}[Paso 1/5] Verificando dependencias del sistema...${NC}"

NEED_INSTALL=false

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python3 no encontrado${NC}"
    NEED_INSTALL=true
else
    echo -e "${GREEN}✓ Python3 instalado: $(python3 --version)${NC}"
fi

if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}pip3 no encontrado${NC}"
    NEED_INSTALL=true
else
    echo -e "${GREEN}✓ pip3 instalado${NC}"
fi

if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git no encontrado${NC}"
    NEED_INSTALL=true
else
    echo -e "${GREEN}✓ Git instalado: $(git --version)${NC}"
fi

if ! command -v python3-venv &> /dev/null && ! python3 -c "import venv" &> /dev/null; then
    echo -e "${YELLOW}python3-venv no encontrado${NC}"
    NEED_INSTALL=true
else
    echo -e "${GREEN}✓ python3-venv disponible${NC}"
fi

echo ""

# Instalar dependencias si faltan
if [ "$NEED_INSTALL" = true ]; then
    echo -e "${YELLOW}Instalando dependencias faltantes...${NC}"
    echo ""
    
    case $DISTRO in
        ubuntu|debian|linuxmint)
            echo -e "${CYAN}Usando apt (Ubuntu/Debian)...${NC}"
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git
            ;;
        fedora)
            echo -e "${CYAN}Usando dnf (Fedora)...${NC}"
            sudo dnf install -y python3 python3-pip git
            ;;
        arch|manjaro)
            echo -e "${CYAN}Usando pacman (Arch)...${NC}"
            sudo pacman -Sy --noconfirm python python-pip git
            ;;
        *)
            echo -e "${RED}Distribucion no soportada automaticamente: $DISTRO${NC}"
            echo "Por favor instala manualmente:"
            echo "  - Python 3.8 o superior"
            echo "  - pip3"
            echo "  - git"
            echo "  - python3-venv"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✓ Dependencias instaladas${NC}"
    echo ""
fi

# Paso 2: Crear entorno virtual
echo -e "${CYAN}[Paso 2/5] Creando entorno virtual...${NC}"

if [ -d ".venv" ]; then
    echo -e "${YELLOW}El entorno virtual ya existe${NC}"
    read -p "¿Deseas recrearlo? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf .venv
        python3 -m venv .venv
        echo -e "${GREEN}✓ Entorno virtual recreado${NC}"
    fi
else
    python3 -m venv .venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
fi
echo ""

# Paso 3: Activar entorno virtual
echo -e "${CYAN}[Paso 3/5] Activando entorno virtual...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# Paso 4: Instalar dependencias Python
echo -e "${CYAN}[Paso 4/5] Instalando dependencias de Python...${NC}"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencias de Python instaladas${NC}"
else
    echo -e "${RED}ERROR: No se encontro requirements.txt${NC}"
    echo "Asegurate de estar en la carpeta correcta de Kalin"
    deactivate
    exit 1
fi
echo ""

# Paso 5: Configurar archivo .env
echo -e "${CYAN}[Paso 5/5] Configurando variables de entorno...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creando archivo .env...${NC}"
    cat > .env << EOF
# ============================================
# CONFIGURACION DE KALIN AI
# ============================================

# Elige UNO de estos proveedores de IA (descomenta el que uses):

# OpenAI (GPT-3.5, GPT-4)
# Obtén tu clave en: https://platform.openai.com/api-keys
#OPENAI_API_KEY=tu_clave_aqui

# Anthropic (Claude)
# Obtén tu clave en: https://console.anthropic.com/
#ANTHROPIC_API_KEY=tu_clave_aqui

# Alibaba Cloud (Qwen)
# Obtén tu clave en: https://help.aliyun.com/
#QWEN_API_KEY=tu_clave_aqui

# Configuración del servidor
PORT=5000
HOST=0.0.0.0

# Modo debug (True para desarrollo, False para producción)
DEBUG=False

# Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
EOF
    
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Debes agregar tu clave API${NC}"
    echo ""
    echo "Edita el archivo .env y agrega tu clave:"
    echo "  nano .env"
    echo ""
    echo "Opciones de claves API gratuitas:"
    echo "  - OpenAI: https://platform.openai.com/api-keys"
    echo "  - Anthropic: https://console.anthropic.com/"
    echo "  - Qwen: https://help.aliyun.com/"
    echo ""
    
    read -p "¿Deseas editar el archivo .env ahora? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        nano .env
    fi
else
    echo -e "${GREEN}✓ El archivo .env ya existe${NC}"
fi
echo ""

# Hacer scripts ejecutables
echo -e "${CYAN}Configurando permisos de scripts...${NC}"
chmod +x iniciar_kalin.sh 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
echo -e "${GREEN}✓ Scripts configurados${NC}"
echo ""

# Resumen final
echo -e "${CYAN}================================================${NC}"
echo -e "${GREEN}  ¡INSTALACION COMPLETADA EXITOSAMENTE!${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""
echo -e "${GREEN}Próximos pasos:${NC}"
echo ""
echo "1. ${YELLOW}Configura tu clave API${NC} (si no lo hiciste):"
echo "   nano .env"
echo ""
echo "2. ${YELLOW}Inicia Kalin${NC}:"
echo "   ./iniciar_kalin.sh"
echo "   O"
echo "   python3 iniciar_kalin.py"
echo ""
echo "3. ${YELLOW}Abre tu navegador${NC}:"
echo "   http://localhost:5000"
echo ""
echo -e "${CYAN}================================================${NC}"
echo ""
echo -e "${GREEN}Documentación útil:${NC}"
echo "  - GUIA_LINUX_PRINCIPIANTES.md (Guía completa)"
echo "  - README.md (Información general)"
echo "  - GUIA_DE_USO.md (Uso de scripts)"
echo ""

# Desactivar entorno virtual (el usuario lo activará al usar Kalin)
deactivate

echo -e "${YELLOW}Para usar Kalin en el futuro:${NC}"
echo "  cd $(pwd)"
echo "  source .venv/bin/activate"
echo "  ./iniciar_kalin.sh"
echo ""

read -p "¿Deseas iniciar Kalin ahora? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    source .venv/bin/activate
    python3 iniciar_kalin.py
fi
