import secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import Flask, session, request, abort, render_template
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from app.models import db, ADM, Usuario

login_manager = LoginManager()

# Rate limiting contra brute force/spam em login e cadastro.
limiter = Limiter(key_func=get_remote_address)

SALT_CSRF = 'csrf-jb-imoveis'


@login_manager.user_loader
def load_user(user_id):
    tipo, id_real = user_id.split('-')
    if tipo == 'admin':
        return ADM.query.get(int(id_real))
    return Usuario.query.get(int(id_real))


def _serializer_csrf(app):
    return URLSafeTimedSerializer(app.config['SECRET_KEY'], salt=SALT_CSRF)


def gerar_token_csrf():
    """Gera (e reutiliza por sessão) um token CSRF assinado."""
    if '_csrf_seed' not in session:
        session['_csrf_seed'] = secrets.token_urlsafe(32)
    from flask import current_app
    return _serializer_csrf(current_app).dumps(session['_csrf_seed'])


def validar_token_csrf(token):
    from flask import current_app
    if '_csrf_seed' not in session or not token:
        return False
    try:
        carregado = _serializer_csrf(current_app).loads(token)
    except (BadSignature, SignatureExpired):
        return False
    return secrets.compare_digest(carregado, session['_csrf_seed'])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.loguin'
    limiter.init_app(app)

    # Proteção CSRF: injeta o token em todos os templates e valida em todo POST.
    @app.context_processor
    def injetar_csrf():
        return dict(csrf_token=gerar_token_csrf)

    @app.context_processor
    def injetar_firebase():
        """Config pública do Firebase (SDK JS) — None se ainda não configurado.

        Com None, o template não renderiza o botão "Entrar com Google". Sempre
        passada por referência: o código nunca injeta a chave da service account
        (segredo) no navegador.
        """
        chaves = ('FIREBASE_API_KEY', 'FIREBASE_AUTH_DOMAIN', 'FIREBASE_PROJECT_ID',
                  'FIREBASE_APP_ID', 'FIREBASE_STORAGE_BUCKET',
                  'FIREBASE_MESSAGING_SENDER_ID')
        valores = [app.config.get(k) for k in chaves]
        if not all(valores):
            return dict(firebase_config=None)
        return dict(firebase_config={
            'apiKey': valores[0],
            'authDomain': valores[1],
            'projectId': valores[2],
            'appId': valores[3],
            'storageBucket': valores[4],
            'messagingSenderId': valores[5],
        })

    @app.before_request
    def proteger_csrf():
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            if not validar_token_csrf(token):
                abort(400)

    from app.routes.public import public_bp
    app.register_blueprint(public_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Esquema: cria as tabelas e, em banco JÁ existente, acrescenta as colunas
    # novas (google_id, picture) via ALTER — idempotente e sem tocar nos dados.
    # Roda aqui para que qualquer entry point que construa o app encontre o
    # banco no esquema que o código espera.
    with app.app_context():
        db.create_all()
        from app.migrate import migrar_banco
        migrar_banco()

    # Páginas de erro amigáveis — em produção, um 500 cru com stack trace
    # vaza detalhes internos pro visitante.
    @app.errorhandler(404)
    def pagina_nao_encontrada(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def erro_interno(e):
        return render_template('500.html'), 500

    return app