"""Validação de ID tokens do Google (Firebase Authentication).

O navegador resolve o popup do Google e entrega um ID token; o back-end manda
ele pra cá, e o SDK `firebase-admin` confere assinatura, expiração e audiência
usando a chave privada da service account (que nunca sai do servidor).

Tudo é lazy e tolerante a falha de propósito: o app sobe mesmo sem o pacote
instalado ou sem credenciais configuradas — nesses casos devolve None e a rota
mostra um erro amigável em vez de derrubar a aplicação.
"""
from flask import current_app


def verificar_token_google(id_token):
    """Valida o ID token do Google e devolve os claims do usuário.

    Retorna dict {'uid', 'email', 'email_verified', 'nome', 'picture'} ou None
    (sem lançar exceção) quando: o token está ausente/vazio, o Firebase não está
    configurado, o pacote não está instalado ou o token é inválido/expirado.
    """
    if not id_token or not current_app.config.get('FIREBASE_SERVICE_ACCOUNT_JSON'):
        return None

    try:
        import firebase_admin
        from firebase_admin import auth, credentials

        # Inicialização única por processo (lazy singleton).
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(
                credentials.Certificate(
                    current_app.config['FIREBASE_SERVICE_ACCOUNT_JSON']
                ),
                {'projectId': current_app.config['FIREBASE_PROJECT_ID']},
            )

        # verify_id_token confere assinatura, expiração e emissor/audiência.
        claims = auth.verify_id_token(id_token)
    except Exception:
        return None

    return {
        'uid': claims.get('uid'),
        'email': claims.get('email'),
        'email_verified': bool(claims.get('email_verified')),
        'nome': claims.get('name'),
        'picture': claims.get('picture'),
    }