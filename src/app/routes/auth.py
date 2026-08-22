from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import ADM

auth_bp = Blueprint('auth', __name__)

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