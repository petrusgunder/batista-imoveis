from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)  # 200, não 100 — hash é mais longo que 100 caracteres

    def set_senha(self, senha_pura):
        self.senha = generate_password_hash(senha_pura)

    def check_senha(self, senha_pura):
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