from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
@public_bp.route('/home')
def home():
    return render_template('home.html')

@public_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@public_bp.route('/entrar')
def loguin():
    return render_template('login.html')

@public_bp.route('/carrinho')
def carrinho():
    return render_template('favoritos.html')

@public_bp.route('/menu_dos_menus')
def menu_dos_menus():
    return render_template('configuracoes.html')

@public_bp.route('/colaborador')
def colaborador():
    return render_template('colaborador.html')

@public_bp.route('/historico')
def historico():
    return render_template('historico.html')

@public_bp.route('/contato')
def contato():
    return render_template('contato.html')

@public_bp.route('/loguinadm')
def loguinadm():
    return render_template('loguinadm.html')