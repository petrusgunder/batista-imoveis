from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import ADM
from app.models import db, Usuario
from flask_login import login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email_digitado = request.form.get('email')

        email_existe = Usuario.query.filter_by(email=email_digitado).first()
        if email_existe:
            flash('Esse e-mail já está cadastrado.')
            return render_template('cadastro.html')

        usuario = Usuario(
            nome=request.form.get('nome'),
            email=email_digitado
        )
        usuario.set_senha(request.form.get('senha'))

        db.session.add(usuario)
        db.session.commit()

        login_user(usuario)
        return redirect(url_for('public.home'))

    return render_template('cadastro.html')

@auth_bp.route('/entrar', methods=['GET', 'POST'])
def loguin():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(email=request.form.get('email')).first()

        if usuario and usuario.check_senha(request.form.get('senha')):
            login_user(usuario)
            return redirect(url_for('public.home'))

        flash('E-mail ou senha incorretos.')

    return render_template('login.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
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

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))