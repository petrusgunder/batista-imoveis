import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug controlado por ambiente: ligado só quando FLASK_DEBUG=1 (dev).
    # (create_app já garante o esquema do banco: create_all + migração.)
    app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1')