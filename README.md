# 🏠 [Nome do Site] — Site de Imóveis

> Site desenvolvido para [nome do cliente/vizinho], com o objetivo de divulgar imóveis disponíveis de forma simples e acessível.

![status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![python](https://img.shields.io/badge/python-3.x-blue)
![flask](https://img.shields.io/badge/flask-3.x-black)

## 📋 Sobre o projeto

Descreva aqui em 2-3 parágrafos:
- Qual problema o site resolve (ex: cliente não tinha presença online, divulgava imóveis só por WhatsApp/boca a boca)
- Para quem é (público-alvo)
- O que o site permite fazer (visitantes buscam imóveis, cliente cadastra/gerencia)

**Contexto**: este foi meu primeiro projeto profissional, desenvolvido logo após concluir o curso técnico em [nome do curso]. Documentei aqui todo o processo de decisão técnica, não só o resultado final.

## ✨ Funcionalidades

- [ ] Listagem de imóveis com filtros (preço, bairro, quartos, tipo)
- [ ] Página de detalhes com galeria de fotos
- [ ] Formulário de contato / interesse no imóvel
- [ ] Área administrativa para cadastro e edição de imóveis (login protegido)
- [ ] Layout responsivo (mobile-first)
- [ ] Busca por localização / mapa

*(marque com `[x]` conforme for implementando)*

## 🛠️ Tecnologias

| Camada | Tecnologia | Por quê |
|---|---|---|
| Backend | Flask | Leve, direto, ideal para o porte do projeto |
| Banco de dados | SQLite | Sem necessidade de servidor separado, suficiente para o volume de dados esperado |
| Frontend | HTML5 + CSS3 | Controle total do layout, sem dependência de frameworks pesados |
| Autenticação | Flask-Login | Proteção da área administrativa |
| Formulários | Flask-WTF | Proteção CSRF nativa |

*(edite a coluna "Por quê" com sua própria justificativa — isso é o que mostra maturidade técnica pra quem for avaliar seu portfólio)*

## 🗂️ Estrutura do projeto

```
projeto-imoveis/
├── app/
│   ├── __init__.py
│   ├── models.py          # Modelos do banco (Imovel, Foto, Usuario)
│   ├── routes.py          # Rotas principais
│   ├── admin/              # Blueprint da área administrativa
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/        # Fotos dos imóveis
├── docs/
│   ├── ARQUITETURA.md
│   ├── BANCO_DE_DADOS.md
│   └── DECISOES.md
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## 🗃️ Modelo de dados (resumo)

Descreva aqui as tabelas principais. Exemplo:

**Imovel**
- id, título, descrição, preço, tipo (casa/apto/terreno), bairro, quartos, banheiros, área, status (disponível/vendido/alugado)

**Foto**
- id, imovel_id (FK), caminho_arquivo, ordem

**Usuario**
- id, email, senha_hash (apenas o administrador do site)

*(link para `docs/BANCO_DE_DADOS.md` com o diagrama completo, se fizer um)*

## 🚀 Como rodar localmente

```bash
# Clonar o repositório
git clone [url-do-repo]
cd projeto-imoveis

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# edite o .env com suas configurações

# Rodar migrações / criar banco
flask db upgrade   # ou o comando que você usar para criar as tabelas

# Rodar o servidor
flask run
```

## 🔒 Segurança

Liste o que foi implementado — isso é ótimo para o portfólio:
- Senhas com hash (werkzeug.security)
- Proteção CSRF nos formulários (Flask-WTF)
- Validação de upload de arquivos (extensão, tamanho, renomeação)
- Variáveis sensíveis fora do código (.env)
- Queries parametrizadas / uso de ORM

## 🌐 Deploy

- **Ambiente**: [Render / PythonAnywhere / VPS]
- **URL**: [link do site no ar]
- Descreva brevemente o processo de deploy escolhido e por quê.

## 📌 Decisões técnicas e aprendizados

Um resumo curto aqui, com link para `docs/DECISOES.md` para o detalhe completo. Exemplos de coisas para registrar:
- Por que SQLite em vez de Postgres nesse estágio
- Algum desafio que você resolveu (ex: upload de imagens, busca com filtros)
- O que você faria diferente numa próxima versão

## 📷 Screenshots

*(adicione prints do site aqui quando estiver pronto — página inicial, listagem, detalhes do imóvel, admin)*

## 👤 Autor

[Seu nome] — desenvolvido como projeto de portfólio após conclusão do curso técnico em [curso].
[LinkedIn] | [GitHub] | [Portfólio]

## 📄 Licença

Este projeto está sob a licença MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.
