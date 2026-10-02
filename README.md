# 🏠 Batista Imóveis - Guia de Uso

Este guia mostrará como iniciar o site sem precisar de assistência técnica.

## 📋 Requisitos

Antes de começar, certifique-se de ter instalado:
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

Para verificar se você tem o Python instalado, abra o terminal e digite:
```bash
python3 --version
```

## 🚀 Como Iniciar o Site

### Método 1: Script Automático (Recomendado)

1. **Abra o terminal** na pasta do projeto `batista-imoveis`

2. **Execute o script de inicialização:**
   ```bash
   ./iniciar-site.sh
   ```

3. **Pronto!** O site estará disponível em:
   - http://127.0.0.1:5000
   - http://localhost:5000

4. **Para parar o servidor**, pressione `CTRL+C` no terminal

### Método 2: Manual

Se preferir fazer manualmente, siga estes passos:

1. **Navegue até a pasta src:**
   ```bash
   cd src
   ```

2. **Ative o ambiente virtual:**
   ```bash
   source venv/bin/activate
   ```

3. **Instale as dependências (primeira vez):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor:**
   ```bash
   python run.py
   ```

5. **Para parar o servidor**, pressione `CTRL+C`

## 📂 Estrutura do Projeto

```
batista-imoveis/
├── iniciar-site.sh          # Script de inicialização automática
├── src/
│   ├── .env                 # Configurações (SECRET_KEY, Firebase, etc)
│   ├── run.py              # Arquivo principal para iniciar o servidor
│   ├── config.py           # Configurações do Flask
│   ├── requirements.txt    # Dependências do projeto
│   ├── venv/               # Ambiente virtual Python
│   └── app/
│       ├── __init__.py     # Inicialização do Flask
│       ├── models.py       # Modelos do banco de dados
│       ├── routes/         # Rotas da aplicação
│       ├── templates/      # Templates HTML
│       └── static/         # Arquivos CSS, JS, imagens
```

## ⚙️ Configurações

### Arquivo .env

O arquivo `src/.env` contém todas as configurações do site:

```env
# Chave secreta (já configurada automaticamente)
SECRET_KEY=sua-chave-secreta-aqui

# Modo debug (1 = ativo, 0 = desativo)
FLASK_DEBUG=1

# Segurança de cookies
SESSION_COOKIE_SECURE=0

# Firebase (opcional - apenas se usar login com Google)
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
FIREBASE_STORAGE_BUCKET=
FIREBASE_MESSAGING_SENDER_ID=
FIREBASE_SERVICE_ACCOUNT_JSON=
```

### Configurar Login com Google (Opcional)

Se quiser ativar o login com Google:

1. Acesse o [Firebase Console](https://console.firebase.google.com/)
2. Crie um novo projeto ou use um existente
3. Ative o Authentication → Google
4. Copie as credenciais e cole no arquivo `.env`

## 🔧 Solução de Problemas

### Problema: "Permission denied" ao executar o script

**Solução:**
```bash
chmod +x iniciar-site.sh
```

### Problema: "python3: command not found"

**Solução:** Instale o Python 3:
- Ubuntu/Debian: `sudo apt install python3 python3-pip`
- Fedora: `sudo dnf install python3 python3-pip`
- Arch: `sudo pacman -S python python-pip`

### Problema: "Module not found"

**Solução:** Reinstale as dependências:
```bash
cd src
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: Porta 5000 já em uso

**Solução:** Pare outros processos na porta 5000:
```bash
# Descubra o processo
lsof -i :5000

# Mate o processo (substitua PID pelo número mostrado)
kill -9 PID
```

Ou edite `src/run.py` e mude a porta:
```python
app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1', port=8000)
```

### Problema: Erro "SECRET_KEY not found"

**Solução:** Execute o script automático que criará o `.env` automaticamente, ou crie manualmente:
```bash
cd src
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > .env
echo "FLASK_DEBUG=1" >> .env
echo "SESSION_COOKIE_SECURE=0" >> .env
```

## 📝 Banco de Dados

O site usa SQLite, que cria automaticamente um arquivo `src/banco.db` na primeira execução.

**Backup do banco:**
```bash
cp src/banco.db src/banco_backup_$(date +%Y%m%d).db
```

**Resetar banco (CUIDADO: apaga todos os dados):**
```bash
rm src/banco.db
# O banco será recriado na próxima inicialização
```

## 🔒 Segurança

### Para Desenvolvimento (ambiente local):
- `FLASK_DEBUG=1` - Modo debug ativo
- `SESSION_COOKIE_SECURE=0` - Cookies funcionam sem HTTPS

### Para Produção (servidor real):
1. Mude no arquivo `.env`:
   ```env
   FLASK_DEBUG=0
   SESSION_COOKIE_SECURE=1
   ```

2. Use um servidor WSGI como Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

## 📞 Comandos Úteis

```bash
# Ver logs do servidor em tempo real
tail -f src/app.log

# Listar processos Python rodando
ps aux | grep python

# Parar todos os servidores Flask
pkill -f "python run.py"

# Atualizar dependências
cd src && source venv/bin/activate && pip install --upgrade -r requirements.txt

# Criar novo usuário administrador (via Python)
cd src && source venv/bin/activate && python
>>> from app import create_app, db
>>> from app.models import ADM
>>> app = create_app()
>>> with app.app_context():
...     admin = ADM(username='admin', email='admin@exemplo.com', senha='senha123')
...     db.session.add(admin)
...     db.session.commit()
```

## 📖 Páginas Disponíveis

- `/` - Página inicial
- `/login` - Login de usuários
- `/cadastro` - Cadastro de novos usuários
- `/loguinadm` - Login de administradores
- `/gerenciar_imoveis` - Gerenciar imóveis (apenas admin)
- `/novo_imovel` - Adicionar novo imóvel (apenas admin)
- `/favoritos` - Imóveis favoritos do usuário
- `/contato` - Página de contato

## 💡 Dicas

1. **Primeira execução**: O script automático configura tudo para você
2. **Atualizações**: Sempre use `git pull` antes de iniciar para ter a versão mais recente
3. **Backup**: Faça backup regular do arquivo `src/banco.db`
4. **Logs**: Se algo der errado, verifique as mensagens no terminal

## 🎯 Início Rápido (TL;DR)

```bash
# Clone ou baixe o projeto
cd batista-imoveis

# Execute o script
./iniciar-site.sh

# Acesse no navegador
# http://localhost:5000
```

---

**Desenvolvido com Flask** 🐍

*Última atualização: Outubro 2026*
