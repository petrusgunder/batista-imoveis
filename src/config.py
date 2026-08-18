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
