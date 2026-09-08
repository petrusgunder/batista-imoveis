# 🏠 JB Imóveis — Site de Imóveis

> Site de divulgação de imóveis para venda e aluguel, com área administrativa para cadastro, edição e exclusão de imóveis, galeria de fotos, favoritos e histórico de visitas.

![status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![python](https://img.shields.io/badge/python-3.x-blue)
![flask](https://img.shields.io/badge/flask-3.x-black)

## 📋 Sobre o projeto

O **JB Imóveis** é uma aplicação web (Flask) que permite a visitantes **buscar e ver imóveis disponíveis** (venda ou aluguel) com filtros de busca, negociação, tipo e preço. Cada anúncio tem uma **página de detalhe com galeria de fotos** (foto principal em destaque + miniaturas).

Visitantes podem **criar conta**, salvar **imóveis favoritos** e consultar o **histórico** dos imóveis que visualizaram. A área administrativa (login protegido) permite gerenciar o catálogo: **cadastrar, editar e excluir imóveis**, além de **adicionar e remover fotos** individualmente.

## ✨ Funcionalidades

- [x] Listagem de imóveis com filtros (busca por local, negociação venda/aluguel, tipo e faixa de preço)
- [x] Carrossel de "Mais visitados" na página inicial
- [x] Página de detalhe com galeria de fotos (foto principal + miniaturas clicáveis)
- [x] Cadastro e login de usuários (Flask-Login)
- [x] Favoritos e histórico de visitas
- [x] Área administrativa (login próprio) para cadastro, edição e exclusão de imóveis
- [x] Upload múltiplo de fotos (com pré-visualização e botão para adicionar uma a uma)
- [x] Remoção individual de fotos na edição
- [x] Página de configurações de conta (editar dados, trocar senha, excluir conta)
- [x] Layout responsivo

## 🛠️ Tecnologias

| Camada | Tecnologia | Por quê |
|---|---|---|
| Backend | Flask 3.x | Leve e direto, ideal para o porte do projeto |
| Banco de dados | SQLite | Sem servidor separado; suficiente para o volume esperado |
| Frontend | HTML5 + CSS3 + JS vanilla | Controle total do layout, sem frameworks pesados |
| Autenticação | Flask-Login | Sessões e proteção de rotas (usuário e admin) |
| Proteção CSRF | itsdangerous (nativa do Flask) | Token assinado por sessão em todos os formulários POST |

## 🗂️ Estrutura do projeto

```
batista-imoveis/
├── README.md
├── documentação/
│   ├── BD.pdf                 # Diagrama do banco de dados
│   └── modelo logico.txt      # Modelo lógico das tabelas
└── src/
    ├── run.py                 # Inicialização (cria tabelas e sobe o servidor)
    ├── requirements.txt       # Dependências
    ├── config.py              # Configuração + limites de segurança de upload
    ├── banco.db               # Banco SQLite (gerado automaticamente)
    ├── .env                   # Variáveis sensíveis (SECRET_KEY) — não versionar
    ├── app/
    │   ├── __init__.py        # create_app + proteção CSRF global
    │   ├── models.py          # Modelos: Usuario, ADM, Imovel, Foto, Favorito, Historico
    │   ├── routes/
    │   │   ├── auth.py        # Cadastro, login (usuário e admin), logout
    │   │   └── public.py      # Home, detalhe, favoritos, histórico, admin de imóveis
    │   ├── templates/         # Páginas HTML (Jinja2)
    │   └── static/
    │       ├── css/style.css  # Estilos (paleta terracota/madeira/papel)
    │       ├── js/upload.js   # Adicionar múltiplas fotos com pré-visualização
    │       └── uploads/       # Fotos dos imóveis
```

## 🗃️ Modelo de dados (resumo)

**Usuario** — id, nome, email, senha (hash)

**ADM** — id, nome, email, senha (hash) — administrador do site

**Imovel** — id, nome, descricao, preco, localizacao, tipo, finalidade (`venda`/`aluguel`), quartos, banheiros, area, status (`disponivel`/`vendido`/`alugado`)

**Foto** — id, imovel_id (FK), url (um imóvel pode ter várias fotos, limitadas a 10)

**Favorito** — id, usuario_id (FK), imovel_id (FK), com unicidade por par usuário/imóvel

**Historico** — id, usuario_id (FK), imovel_id (FK), data_acesso

O modelo lógico completo está em `documentação/modelo logico.txt` e o diagrama em `documentação/BD.pdf`.

## 🚀 Como rodar localmente

```bash
cd src

# Opção A — usar o Python do sistema (é o que tem Flask instalado)
python3 run.py

# Opção B — com ambiente virtual
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python run.py
```

> Acesse `http://localhost:5000`. As tabelas são criadas automaticamente na primeira execução (`db.create_all()`).

> **Login de administrador**: o acesso admin é feito pela rota `/admin/login`. O primeiro administrador precisa ser criado direto na tabela `adm` do banco (o cadastro público cria apenas usuários comuns). Exemplo:
> ```bash
> python3 -c "
> from app import create_app
> from app.models import db, ADM
> app = create_app()
> with app.app_context():
>     adm = ADM(nome='Admin', email='admin@email.com')
>     adm.set_senha('sua-senha')
>     db.session.add(adm); db.session.commit()
> "
> ```

## 🔒 Segurança implementada

- **Senhas com hash** — `werkzeug.security` (nenhuma senha em texto puro no banco)
- **Proteção CSRF** — token assinado por sessão (itsdangerous) validado em **todo** formulário POST no `before_request`; requisições sem token válido recebem HTTP 400
- **Validação de upload** — extensão permitida + verificação de **conteúdo real** (magic bytes de JPEG/PNG/WEBP), impedindo arquivos renomeados
- **Limites de upload** — no máximo **10 fotos por imóvel**, **5 MB por foto** e **16 MB por requisição** (`config.py` → `MAX_CONTENT_LENGTH`)
- **Nome de arquivos saneado** — `secure_filename` + prefixo do id do imóvel (evita colisão e path traversal)
- **Variáveis sensíveis fora do código** — `SECRET_KEY` no `.env`
- **Queries parametrizadas / uso de ORM** — SQLAlchemy, sem concatenação de SQL

## 📌 Decisões técnicas

- **SQLite em vez de Postgres**: sem infraestrutura extra, suficiente para o volume do projeto; fácil de trocar depois via `DATABASE_URL`.
- **Múltiplas fotos por imóvel**: tabela `Foto` separada com FK para `Imovel`, permitindo galeria de N fotos com limite para proteger o servidor.
- **CSRF sem Flask-WTF**: token assinado com `itsdangerous` (já é dependência do Flask), evitando adicionar uma biblioteca e um ciclo de formulários externos.
- **Thumbnails na galeria**: foto principal + miniaturas trocáveis via JavaScript puro, sem biblioteca de carrossel.

## 📷 Screenshots

*(adicione prints do site quando estiver pronto — página inicial, detalhe do imóvel e área admin)*

## 👤 Autor

Projeto de portfólio desenvolvido após a conclusão do curso técnico.
[LinkedIn] | [GitHub] | [Portfólio]