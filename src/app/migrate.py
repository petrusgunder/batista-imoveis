"""Migração idempotente do esquema — banco SQLite.

O SQLite não tem o conceito de migrations migratórias do Alembic nem permite
ALTER ADD COLUMN ... UNIQUE (3.45 rejeita). Este módulo estende um banco JÁ
criado com as colunas novas, via ALTER, sem tocar nos dados existentes:

  - banco recém-criado:  `db.create_all()` já traz tudo → nada a fazer;
  - banco já existente:  PRAGMA table_info mostra quais colunas faltam e o
                         ALTER as acrescenta; o índice único parcial entra
                         depois com CREATE INDEX IF NOT EXISTS.

Idempotente: rodar de novo é um no-op.
"""
from sqlalchemy import text
from app.models import db

# (nome_da_coluna, tipo_SQL) que o código atual usa e que banco antigo pode não ter.
_COLUNAS_NOVAS = (
    ('google_id', 'VARCHAR(200)'),
    ('picture', 'VARCHAR(500)'),
)

# Índices novos criados fora do create_all (banco existente).
_INDICES_NOVOS = (
    # Unicidade do google_id SÓ quando não é NULL — múltiplos NULLs convivem
    # (as contas tradicionais) e um mesmo Google não pode ter usuário duplicado.
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_google_id "
    "ON usuarios (google_id) WHERE google_id IS NOT NULL",
)


def _colunas_existentes():
    """Nomes das colunas atuais da tabela usuarios, via PRAGMA table_info."""
    linha_de_coluna = db.session.execute(text("PRAGMA table_info('usuarios')")).fetchall()
    return {linha[1] for linha in linha_de_coluna}


def migrar_banco():
    """Acrescenta o que faltar ao esquema. Deve rodar com app context aberto."""
    colunas = _colunas_existentes()

    for nome, tipo in _COLUNAS_NOVAS:
        if nome not in colunas:
            db.session.execute(text(f"ALTER TABLE usuarios ADD COLUMN {nome} {tipo}"))

    for ddl in _INDICES_NOVOS:
        db.session.execute(text(ddl))

    db.session.commit()