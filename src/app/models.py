from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    __table_args__ = (
        # google_id é único SÓ onde não é NULL. Indice único parcial, e não
        # unique=True na coluna: o SQLite 3.45 rejeita ALTER ADD COLUMN ...
        # UNIQUE, então a migração em banco existente precisa desse formato.
        db.Index('uq_usuarios_google_id', 'google_id',
                 unique=True, sqlite_where=db.text('google_id IS NOT NULL')),
    )
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)  # 200, não 100 — hash é mais longo que 100 caracteres
    # Contas do Google (ou híbridas) preenchem estes dois campos; as tradicionais ficam NULL.
    google_id = db.Column(db.String(200), nullable=True)
    picture = db.Column(db.String(500), nullable=True)  # avatar do Google

    def set_senha(self, senha_pura):
        self.senha = generate_password_hash(senha_pura)

    def check_senha(self, senha_pura):
        # Contas só-Google têm um hash sentinela irreversível na senha. Sem o
        # guard, check_password_hash(None, ...) subiria AttributeError em vez
        # de retornar False (senha sempre "errada" para elas).
        if not self.senha:
            return False
        return check_password_hash(self.senha, senha_pura)

    def get_id(self):
        return f"usuario-{self.id}"

    favoritos = db.relationship('Favorito', backref='usuario', cascade='all, delete-orphan')
    historico = db.relationship('Historico', backref='usuario', cascade='all, delete-orphan')

class ADM(db.Model, UserMixin):
    __tablename__ = 'adm'
    is_admin = True
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)  # aumentei pra 200, hash é maior que 100 chars

    def set_senha(self, senha_pura):
        from werkzeug.security import generate_password_hash
        self.senha = generate_password_hash(senha_pura)

    def check_senha(self, senha_pura):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.senha, senha_pura)

    def get_id(self):
        return f"admin-{self.id}"

class Imovel(db.Model):
    __tablename__ = 'imoveis'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.DECIMAL(10, 2), nullable=False)
    localizacao = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    finalidade = db.Column(db.String(20), nullable=False, default='venda')  # nova coluna: 'venda' ou 'aluguel'
    quartos = db.Column(db.Integer, nullable=False)
    banheiros = db.Column(db.Integer, nullable=False)
    area = db.Column(db.DECIMAL(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    

    fotos = db.relationship('Foto', backref='imovel', cascade='all, delete-orphan')
    favoritado_por = db.relationship('Favorito', backref='imovel', cascade='all, delete-orphan')
    historico = db.relationship('Historico', backref='imovel', cascade='all, delete-orphan')


class Foto(db.Model):
    __tablename__ = 'fotos'
    id = db.Column(db.Integer, primary_key=True)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imoveis.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)


class Historico(db.Model):
    __tablename__ = 'historico'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imoveis.id'), nullable=False)
    data_acesso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Favorito(db.Model):
    __tablename__ = 'favoritos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imoveis.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'imovel_id', name='uq_usuario_imovel_favorito'),
    )