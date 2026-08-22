from flask import Blueprint, render_template
from app.models import db, Imovel
from flask import request, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from flask import abort
from flask_login import current_user
from app.models import ADM
from flask_login import logout_user
from flask import flash
from app.models import db, Imovel, Favorito, Historico

public_bp = Blueprint('public', __name__)

@public_bp.route('/')

@public_bp.route('/')
def home():
    imoveis = Imovel.query.filter_by(status='disponivel').all()
    return render_template('home.html', imoveis=imoveis)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, ADM):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@public_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@public_bp.route('/entrar')
def loguin():
    return render_template('login.html')

@public_bp.route('/carrinho')
@login_required
def carrinho():
    favoritos = Favorito.query.filter_by(usuario_id=current_user.id).all()
    imoveis_favoritados = [Imovel.query.get(f.imovel_id) for f in favoritos]
    return render_template('favoritos.html', imoveis=imoveis_favoritados)

@public_bp.route('/menu_dos_menus')
def menu_dos_menus():
    return render_template('configuracoes.html')

@public_bp.route('/colaborador')
def colaborador():
    return render_template('colaborador.html')

@public_bp.route('/historico')
@login_required
def historico():
    registros = Historico.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Historico.data_acesso.desc()).all()

    return render_template('historico.html', registros=registros)

@public_bp.route('/contato')
def contato():
    return render_template('contato.html')

@public_bp.route('/loguinadm')
def loguinadm():
    return render_template('loguinadm.html')

@public_bp.route('/imovel/<int:id>')
def detalhe_imovel(id):
    imovel = Imovel.query.get_or_404(id)

    if current_user.is_authenticated:
        visualizacao = Historico(usuario_id=current_user.id, imovel_id=id)
        db.session.add(visualizacao)
        db.session.commit()

    ja_favoritado = False
    if current_user.is_authenticated:
        ja_favoritado = Favorito.query.filter_by(
            usuario_id=current_user.id, imovel_id=id
        ).first() is not None

    return render_template('detalhe_imovel.html', imovel=imovel, ja_favoritado=ja_favoritado)

@public_bp.route('/imovel/<int:id>/favoritar', methods=['POST'])
@login_required
def favoritar(id):
    ja_favoritado = Favorito.query.filter_by(
        usuario_id=current_user.id, imovel_id=id
    ).first()

    if ja_favoritado:
        db.session.delete(ja_favoritado)
    else:
        novo = Favorito(usuario_id=current_user.id, imovel_id=id)
        db.session.add(novo)

    db.session.commit()
    return redirect(url_for('public.detalhe_imovel', id=id))

@public_bp.route('/imovel/novo', methods=['GET', 'POST'])
@admin_required
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

@public_bp.route('/conta/editar', methods=['POST'])
@login_required
def editar_conta():
    current_user.nome = request.form.get('nome')
    current_user.email = request.form.get('email')
    db.session.commit()
    flash('Dados atualizados.')
    return redirect(url_for('public.menu_dos_menus'))


@public_bp.route('/conta/trocar-senha', methods=['POST'])
@login_required
def trocar_senha():
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')

    if not current_user.check_senha(senha_atual):
        flash('Senha atual incorreta.')
        return redirect(url_for('public.menu_dos_menus'))

    current_user.set_senha(senha_nova)
    db.session.commit()
    flash('Senha atualizada.')
    return redirect(url_for('public.menu_dos_menus'))


@public_bp.route('/conta/deletar', methods=['POST'])
@login_required
def deletar_conta():
    usuario_a_apagar = current_user._get_current_object()
    logout_user()
    db.session.delete(usuario_a_apagar)
    db.session.commit()
    return redirect(url_for('public.home'))