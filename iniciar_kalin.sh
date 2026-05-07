#!/bin/bash
# Kalin AI - Script de inicio para Linux/macOS
# Este script facilita el inicio de Kalin en sistemas Unix

set -e  # Salir si hay errores

# Colores para la terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  KALIN AI - ASISTENTE DE PROGRAMACION${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar Python
echo -e "${YELLOW}Verificando instalacion...${NC}"
echo ""

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 no esta instalado${NC}"
    echo ""
    echo "Por favor instala Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}[OK] Python encontrado: $PYTHON_VERSION${NC}"
echo ""

# Verificar pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}[ADVERTENCIA] pip no encontrado${NC}"
    echo "Instalando dependencias puede fallar sin pip"
    echo ""
fi

# Verificar entorno virtual
VENV_PATH="./.venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo -e "${GREEN}[OK] Entorno virtual encontrado${NC}"
    echo "Activando entorno virtual..."
    source "$VENV_PATH"
else
    echo -e "${YELLOW}[INFO] No se encontro entorno virtual${NC}"
    echo "Usando Python del sistema..."
    echo ""
    echo "Para crear un entorno virtual (recomendado):"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    
    read -p "¿Deseas continuar sin entorno virtual? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operacion cancelada."
        exit 0
    fi
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  INICIANDO KALIN...${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}Abre tu navegador en: http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener Kalin${NC}"
echo ""
echo -e "${CYAN}========================================${NC}"
echo ""

# Iniciar Kalin
python3 iniciar_kalin.py
