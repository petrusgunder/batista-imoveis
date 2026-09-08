import os
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env e carrega as variáveis

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'troque-essa-chave-no-env')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'banco.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Segurança de upload -------------------------------------------------
    # Limite total de uma requisição (protege contra upload de arquivos enormes).
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB por requisição
    # Tamanho máximo de um único arquivo de imagem.
    MAX_TAMANHO_ARQUIVO = 5 * 1024 * 1024  # 5 MB por foto
    # Número máximo de fotos por imóvel (evita encher o servidor de arquivos).
    MAX_FOTOS_POR_IMOVEL = 10
