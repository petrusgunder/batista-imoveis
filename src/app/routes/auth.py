from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from app import limiter
from app.models import ADM
from app.models import db, Usuario
from flask_login import login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar_senha', '')

        # --- Validação server-side (não confiar nos `required` do HTML) ---
        erros = []
        if len(nome) < 2:
            erros.append('Nome deve ter pelo menos 2 caracteres.')
        if email.count('@') != 1 or email.startswith('@') or email.endswith('@'):
            erros.append('E-mail inválido.')
        if len(senha) < 8:
            erros.append('A senha deve ter pelo menos 8 caracteres.')
        if senha != confirmar:
            erros.append('As senhas não coincidem.')

        if not erros and Usuario.query.filter_by(email=email).first():
            erros.append('Esse e-mail já está cadastrado.')

        if erros:
            for e in erros:
                flash(e)
            return render_template('cadastro.html')

        usuario = Usuario(nome=nome, email=email)
        usuario.set_senha(senha)

        try:
            db.session.add(usuario)
            db.session.commit()
        except IntegrityError:
            # Corrida de dois cadastros com o mesmo e-mail: o unique do banco
            # impede o segundo, e não estouramos um 500 cru.
            db.session.rollback()
            flash('Esse e-mail já está cadastrado.')
            return render_template('cadastro.html')

        login_user(usuario)
        return redirect(url_for('public.home'))

    return render_template('cadastro.html')

@auth_bp.route('/entrar', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def loguin():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(email=request.form.get('email')).first()

        if usuario and usuario.check_senha(request.form.get('senha')):
            login_user(usuario)
            # Volta para a página que o usuário tentava acessar antes de logar
            # (ex.: favoritar um imóvel sem estar logado). Só aceita caminho
            # interno — evita open redirect para sites externos.
            destino = request.form.get('next')
            if destino and destino.startswith('/') and not destino.startswith('//'):
                return redirect(destino)
            return redirect(url_for('public.home'))

        flash('E-mail ou senha incorretos.')

    return render_template('login.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        admin = ADM.query.filter_by(email=email).first()

        if admin and admin.check_senha(senha):
            login_user(admin)
            return redirect(url_for('public.home'))

        flash('E-mail ou senha incorretos.')  # veja explicação do flash abaixo

    return render_template('admin_login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))