from flask import (
    Blueprint, render_template, request, redirect, url_for,
    current_app, abort, flash
)
from flask_login import login_required, current_user, logout_user
from functools import wraps
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, InvalidOperation
from werkzeug.utils import secure_filename
import os

from app.models import db, Imovel, Favorito, Historico, Foto, ADM, Usuario


def validar_dados_imovel(dados):
    """Valida o formulário de imóvel no servidor — evita que um campo vazio ou
    numérico inválido (ex.: preco='abc') estoure um 500 na hora do INSERT.

    Retorna lista de mensagens de erro (vazia = formulário válido).
    """
    erros = []

    for campo in ('nome', 'descricao', 'localizacao', 'tipo', 'finalidade'):
        if not (dados.get(campo) or '').strip():
            erros.append(f'O campo "{campo}" é obrigatório.')

    # preco e area: DECIMAL(10,2) no banco
    for campo, rotulo in (('preco', 'preço'), ('area', 'área')):
        valor = (dados.get(campo) or '').strip()
        if not valor:
            erros.append(f'O campo "{rotulo}" é obrigatório.')
        else:
            try:
                if Decimal(valor) < 0:
                    erros.append(f'O {rotulo} não pode ser negativo.')
            except InvalidOperation:
                erros.append(f'O {rotulo} deve ser um número válido (ex.: 250000.00).')

    # quartos e banheiros: INTEGER no banco
    for campo in ('quartos', 'banheiros'):
        valor = (dados.get(campo) or '').strip()
        if not valor:
            erros.append(f'O campo "{campo}" é obrigatório.')
        else:
            try:
                if int(valor) < 0:
                    erros.append(f'O campo "{campo}" não pode ser negativo.')
            except ValueError:
                erros.append(f'O campo "{campo}" deve ser um número inteiro.')

    return erros

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}

def extensao_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


def eh_imagem_valida(arquivo):
    """Valida o conteúdo real do arquivo (magic bytes), não só a extensão.
    Impede enviar um .exe ou script renomeado para .jpg/.png/.webp."""
    arquivo.stream.seek(0)
    cabecalho = arquivo.read(16)
    arquivo.stream.seek(0)

    if cabecalho[:3] == b'\xff\xd8\xff':                      # JPEG
        return True
    if cabecalho[:8] == b'\x89PNG\r\n\x1a\n':                  # PNG
        return True
    if cabecalho[:4] == b'RIFF' and cabecalho[8:12] == b'WEBP':  # WEBP
        return True
    return False


def salvar_fotos(imovel, arquivos):
    """Salva os arquivos de imagem de um imóvel no disco e cria os registros Foto.

    Rejeita arquivos que não sejam imagem válida (magic bytes), que passem do
    limite de tamanho ou que estoure o limite de fotos por imóvel.
    """
    limite_fotos = current_app.config['MAX_FOTOS_POR_IMOVEL']
    limite_tamanho = current_app.config['MAX_TAMANHO_ARQUIVO']
    qtd_atual = len(imovel.fotos)
    descartadas = 0

    for arquivo in arquivos:
        if qtd_atual >= limite_fotos:
            descartadas += 1
            continue
        if not (arquivo and arquivo.filename):
            continue
        if not extensao_permitida(arquivo.filename):
            descartadas += 1
            continue
        if arquivo.content_length and arquivo.content_length > limite_tamanho:
            descartadas += 1
            continue
        if not eh_imagem_valida(arquivo):
            descartadas += 1
            continue

        nome_seguro = secure_filename(arquivo.filename)
        nome_unico = f"{imovel.id}_{qtd_atual}_{nome_seguro}"
        caminho_completo = os.path.join('app', 'static', 'uploads', nome_unico)
        arquivo.save(caminho_completo)

        foto = Foto(imovel_id=imovel.id, url=nome_unico)
        db.session.add(foto)
        qtd_atual += 1

    if descartadas > 0:
        flash(f'{descartadas} foto(s) não foram salvas (limite de {limite_fotos} fotos, '
              'tamanho máximo 5 MB ou arquivo não é uma imagem válida).')

public_bp = Blueprint('public', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, ADM):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@public_bp.route('/')

@public_bp.route('/')
def home():
    query = Imovel.query.filter_by(status='disponivel')

    busca = request.args.get('busca')
    negociacao = request.args.get('negociacao')
    tipo = request.args.get('tipo')
    preco_min = request.args.get('preco_min')
    preco_max = request.args.get('preco_max')

    if busca:
        query = query.filter(
            Imovel.localizacao.ilike(f'%{busca}%') | Imovel.nome.ilike(f'%{busca}%')
        )
    if negociacao:
        query = query.filter_by(finalidade=negociacao)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if preco_min:
        query = query.filter(Imovel.preco >= preco_min)
    if preco_max:
        query = query.filter(Imovel.preco <= preco_max)

    imoveis = query.limit(10).all()

    mais_visitados = (
        db.session.query(Imovel, func.count(Historico.id).label('visitas'))
        .join(Historico, Historico.imovel_id == Imovel.id)
        .group_by(Imovel.id)
        .order_by(func.count(Historico.id).desc())
        .limit(8)
        .all()
    )

    return render_template('home.html', imoveis=imoveis, mais_visitados=mais_visitados)
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
    imovel = Imovel.query.get(id)
    if imovel is None:
        # Sem essa verificação, um id inexistente criaria um Favorito órfão
        # (SQLite não força a FK em tempo de execução por padrão).
        flash('Imóvel não encontrado.')
        return redirect(url_for('public.menu_dos_menus'))

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

@public_bp.route('/conta/editar', methods=['POST'])
@login_required
def editar_conta():
    nome = (request.form.get('nome') or '').strip()
    email = (request.form.get('email') or '').strip()

    if len(nome) < 2:
        flash('O nome deve ter pelo menos 2 caracteres.')
        return redirect(url_for('public.menu_dos_menus'))
    if email.count('@') != 1 or email.startswith('@') or email.endswith('@'):
        flash('E-mail inválido.')
        return redirect(url_for('public.menu_dos_menus'))

    # E-mail pertence a outra conta? (unique no banco estouraria IntegrityError)
    ja_existe = Usuario.query.filter(
        Usuario.email == email,
        Usuario.id != current_user.id
    ).first()
    if ja_existe:
        flash('Esse e-mail já está em uso por outra conta.')
        return redirect(url_for('public.menu_dos_menus'))

    current_user.nome = nome
    current_user.email = email
    try:
        db.session.commit()
    except IntegrityError:
        # Corrida: outro cadastro pegou esse e-mail entre a checagem e o commit.
        db.session.rollback()
        flash('Esse e-mail já está em uso por outra conta.')
        return redirect(url_for('public.menu_dos_menus'))

    flash('Dados atualizados.')
    return redirect(url_for('public.menu_dos_menus'))


@public_bp.route('/conta/trocar-senha', methods=['POST'])
@login_required
def trocar_senha():
    senha_atual = request.form.get('senha_atual', '')
    senha_nova = request.form.get('senha_nova', '')

    if not current_user.check_senha(senha_atual):
        flash('Senha atual incorreta.')
        return redirect(url_for('public.menu_dos_menus'))

    if len(senha_nova) < 8:
        flash('A nova senha deve ter pelo menos 8 caracteres.')
        return redirect(url_for('public.menu_dos_menus'))

    if senha_nova == senha_atual:
        flash('A nova senha deve ser diferente da atual.')
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

@public_bp.route('/imovel/novo', methods=['GET', 'POST'])
@admin_required
def novo_imovel():
    if request.method == 'POST':
        erros = validar_dados_imovel(request.form)
        if erros:
            for e in erros:
                flash(e)
            return render_template('novo_imovel.html')

        imovel = Imovel(
            nome=request.form.get('nome'),
            descricao=request.form.get('descricao'),
            preco=request.form.get('preco'),
            localizacao=request.form.get('localizacao'),
            tipo=request.form.get('tipo'),
            finalidade=request.form.get('finalidade'),
            quartos=request.form.get('quartos'),
            banheiros=request.form.get('banheiros'),
            area=request.form.get('area'),
            status='disponivel'
        )
        db.session.add(imovel)
        db.session.commit()  # precisa salvar antes, pra existir um imovel.id pras fotos referenciarem

        salvar_fotos(imovel, request.files.getlist('fotos'))

        db.session.commit()
        return redirect(url_for('public.detalhe_imovel', id=imovel.id))

    return render_template('novo_imovel.html')

@public_bp.route('/admin/imoveis')
@admin_required
def gerenciar_imoveis():
    imoveis = Imovel.query.all()
    return render_template('gerenciar_imoveis.html', imoveis=imoveis)


@public_bp.route('/imovel/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_imovel(id):
    imovel = Imovel.query.get_or_404(id)

    if request.method == 'POST':
        erros = validar_dados_imovel(request.form)
        if erros:
            for e in erros:
                flash(e)
            return render_template('editar_imovel.html', imovel=imovel)

        imovel.nome = request.form.get('nome')
        imovel.descricao = request.form.get('descricao')
        imovel.preco = request.form.get('preco')
        imovel.localizacao = request.form.get('localizacao')
        imovel.tipo = request.form.get('tipo')
        imovel.finalidade = request.form.get('finalidade')
        imovel.quartos = request.form.get('quartos')
        imovel.banheiros = request.form.get('banheiros')
        imovel.area = request.form.get('area')
        imovel.status = request.form.get('status')

        salvar_fotos(imovel, request.files.getlist('fotos'))

        db.session.commit()
        return redirect(url_for('public.detalhe_imovel', id=imovel.id))

    return render_template('editar_imovel.html', imovel=imovel)


@public_bp.route('/imovel/<int:id>/foto/<int:foto_id>/remover', methods=['POST'])
@admin_required
def remover_foto(id, foto_id):
    foto = Foto.query.get_or_404(foto_id)
    if foto.imovel_id != id:
        abort(400)

    caminho = os.path.join('app', 'static', 'uploads', foto.url)
    try:
        os.remove(caminho)
    except OSError:
        pass

    db.session.delete(foto)
    db.session.commit()
    return redirect(url_for('public.editar_imovel', id=id))


@public_bp.route('/imovel/<int:id>/excluir', methods=['POST'])
@admin_required
def excluir_imovel(id):
    imovel = Imovel.query.get_or_404(id)
    db.session.delete(imovel)
    db.session.commit()
    return redirect(url_for('public.gerenciar_imoveis'))