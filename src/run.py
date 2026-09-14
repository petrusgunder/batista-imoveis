import os
from app import create_app
from app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # cria as tabelas se ainda não existirem
    # Debug controlado por ambiente: ligado só quando FLASK_DEBUG=1 (dev).
    app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1')
