#!/bin/bash
# Script para iniciar o site Batista Imóveis
# Uso: ./iniciar-site.sh

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Batista Imóveis - Inicializador${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Navegar para o diretório do projeto
cd "$(dirname "$0")/src"

# Verificar se o .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}[1/4] Criando arquivo .env...${NC}"
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cat > .env << EOF
# Configurações básicas do Flask
SECRET_KEY=$SECRET_KEY
FLASK_DEBUG=1

# Banco de dados (SQLite local)
# DATABASE_URL=sqlite:///banco.db

# Cookies de sessão
SESSION_COOKIE_SECURE=0

# Firebase Authentication (opcional - deixe em branco se não usar)
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
FIREBASE_STORAGE_BUCKET=
FIREBASE_MESSAGING_SENDER_ID=
FIREBASE_SERVICE_ACCOUNT_JSON=
EOF
    echo -e "${GREEN}   ✓ Arquivo .env criado${NC}\n"
else
    echo -e "${GREEN}[1/4] Arquivo .env já existe${NC}\n"
fi

# Verificar/criar ambiente virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[2/4] Criando ambiente virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}   ✓ Ambiente virtual criado${NC}\n"
else
    echo -e "${GREEN}[2/4] Ambiente virtual já existe${NC}\n"
fi

# Ativar ambiente virtual e instalar dependências
echo -e "${YELLOW}[3/4] Instalando dependências...${NC}"
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}   ✓ Dependências instaladas${NC}\n"

# Iniciar servidor
echo -e "${YELLOW}[4/4] Iniciando servidor Flask...${NC}\n"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Servidor rodando em:${NC}"
echo -e "${GREEN}   http://127.0.0.1:5000${NC}"
echo -e "${GREEN}   http://localhost:5000${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}   Pressione CTRL+C para parar${NC}\n"

python run.py
