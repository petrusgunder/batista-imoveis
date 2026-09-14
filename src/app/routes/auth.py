import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app import limiter
from app.models import db, Usuario, ADM
from app.services.firebase_auth import verificar_token_google

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

@auth_bp.route('/entrar-google', methods=['POST'])
@limiter.limit("10 per minute")
def entrar_google():
    """Login/cadastro via Google (Firebase Authentication).

    O front já resolveu o popup do Google; o back confere o ID token de novo com
    a chave privada da service account (verify_id_token valida assinatura,
    expiração e audiência) e então cria OU linka o Usuario no SQLite:
      (a) google_id já existe  → login direto (mesma conta, não duplica);
      (b) e-mail já existe     → LIGA o Google na conta tradicional existente
          (vira híbrida: senha preservada), mesmo usuário para as duas formas;
      (c) ninguém             → cria conta nova (senha = hash sentinela).
    """
    id_token = request.form.get('id_token', '')
    destino = request.form.get('next', '').strip()

    def recusar(mensagem):
        flash(mensagem)
        # Preserva o ?next da página que originou o login.
        if destino and destino.startswith('/') and not destino.startswith('//'):
            return redirect(url_for('auth.loguin', next=destino))
        return redirect(url_for('auth.loguin'))

    claims = verificar_token_google(id_token)
    if not claims or not claims.get('uid'):
        return recusar('Não foi possível validar sua conta do Google. Tente novamente.')

    # Sem e-mail verificado o dono do endereço pode não ser dono da conta —
    # recusa para evitar account takeover.
    if not claims.get('email') or not claims.get('email_verified'):
        return recusar('O e-mail da sua conta do Google precisa estar verificado.')

    # (a) Já vinculado a um Usuario pelo google_id.
    usuario = Usuario.query.filter_by(google_id=claims['uid']).first()

    if usuario is None:
        # (b) E-mail já usado por uma conta tradicional → linka na MESMA linha.
        usuario = Usuario.query.filter_by(email=claims['email']).first()
        if usuario is not None:
            usuario.google_id = claims['uid']
            if claims.get('picture'):
                usuario.picture = claims['picture']
        else:
            # (c) Conta nova.
            nome = (claims.get('nome') or claims['email'].split('@')[0]).strip() or 'Usuário Google'
            usuario = Usuario(
                nome=nome,
                email=claims['email'],
                google_id=claims['uid'],
                picture=claims.get('picture'),
                # Conta só-Google não tem senha; o hash aleatório é um sentinela
                # irreversível pra coluna NOT NULL — check_senha sempre falha.
                senha=generate_password_hash(secrets.token_urlsafe(32)),
            )

    try:
        db.session.add(usuario)
        db.session.commit()
    except IntegrityError:
        # Corrida (duas abas abrindo o login Google no mesmo instante): outro
        # processo já criou/linkou a linha. Reembolsa e reprocura.
        db.session.rollback()
        usuario = (Usuario.query.filter_by(google_id=claims['uid']).first()
                   or Usuario.query.filter_by(email=claims['email']).first())
        if usuario is None:
            return recusar('Não foi possível acessar sua conta. Tente novamente.')

    login_user(usuario)

    # Redirecionamento é o mesmo guard anti open-redirect do login tradicional.
    if destino and destino.startswith('/') and not destino.startswith('//'):
        return redirect(destino)
    return redirect(url_for('public.home'))

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