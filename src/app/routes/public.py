from flask import Blueprint, render_template
from app.models import db, Imovel
from flask import request, redirect, url_for
from flask_login import login_required, current_user

public_bp = Blueprint('public', __name__)

@public_bp.route('/')

@public_bp.route('/')
def home():
    imoveis = Imovel.query.filter_by(status='disponivel').all()
    return render_template('home.html', imoveis=imoveis)

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

@public_bp.route('/imovel/<int:id>')
def detalhe_imovel(id):
    imovel = Imovel.query.get_or_404(id)
    return render_template('detalhe_imovel.html', imovel=imovel)

@public_bp.route('/imovel/novo', methods=['GET', 'POST'])
@login_required
def novo_imovel():
    if request.method == 'POST':
        imovel = Imovel(
            nome=request.form.get('nome'),
            descricao=request.form.get('descricao'),
            preco=request.form.get('preco'),
            localizacao=request.form.get('localizacao'),
            tipo=request.form.get('tipo'),
            quartos=request.form.get('quartos'),
            banheiros=request.form.get('banheiros'),
            area=request.form.get('area'),
            status='disponivel'
        )
        db.session.add(imovel)
        db.session.commit()
        return redirect(url_for('public.detalhe_imovel', id=imovel.id))

    return render_template('novo_imovel.html')