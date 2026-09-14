import os
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env e carrega as variáveis

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Sem fallback hardcoded: se a SECRET_KEY não existir no ambiente,
    # o app falha ao iniciar em vez de rodar com uma chave fraca/commitada.
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'banco.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Cookies de sessão ---
    SESSION_COOKIE_HTTPONLY = True            # JS não lê o cookie de sessão
    SESSION_COOKIE_SAMESITE = 'Lax'           # não envia o cookie em POST cross-site
    # Em produção com HTTPS, rode com SESSION_COOKIE_SECURE=1 no .env.
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'

    # --- Segurança de upload -------------------------------------------------
    # Limite total de uma requisição (protege contra upload de arquivos enormes).
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB por requisição
    # Tamanho máximo de um único arquivo de imagem.
    MAX_TAMANHO_ARQUIVO = 5 * 1024 * 1024  # 5 MB por foto
    # Número máximo de fotos por imóvel (evita encher o servidor de arquivos).
    MAX_FOTOS_POR_IMOVEL = 10
