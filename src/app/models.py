from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)

    favoritos = db.relationship('Favorito', backref='usuario', cascade='all, delete-orphan')
    historico = db.relationship('Historico', backref='usuario', cascade='all, delete-orphan')


class ADM(db.Model):
    __tablename__ = 'adm'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)


class Imovel(db.Model):
    __tablename__ = 'imoveis'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.DECIMAL(10, 2), nullable=False)
    localizacao = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
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