#!/usr/bin/env python3
"""Script para criar um usuário administrador no banco de dados."""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.models import db, ADM

def criar_admin(email, senha, nome="Administrador"):
    """Cria um novo administrador no banco de dados."""
    app = create_app()

    with app.app_context():
        # Verifica se o admin já existe
        admin_existente = ADM.query.filter_by(email=email).first()

        if admin_existente:
            print(f"❌ Administrador com o email '{email}' já existe no banco de dados.")
            print(f"   ID: {admin_existente.id}")
            print(f"   Nome: {admin_existente.nome}")
            return False

        # Cria o novo administrador
        novo_admin = ADM(nome=nome, email=email)
        novo_admin.set_senha(senha)

        try:
            db.session.add(novo_admin)
            db.session.commit()
            print(f"✅ Administrador criado com sucesso!")
            print(f"   ID: {novo_admin.id}")
            print(f"   Nome: {novo_admin.nome}")
            print(f"   Email: {novo_admin.email}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar administrador: {e}")
            return False

if __name__ == '__main__':
    # Dados do administrador
    EMAIL = "gunderiiiterceiro@gmail.com"
    SENHA = "wapp1928"
    NOME = "Administrador"

    print("🔧 Criando administrador...")
    print(f"   Email: {EMAIL}")
    print(f"   Nome: {NOME}")
    print()

    criar_admin(EMAIL, SENHA, NOME)
