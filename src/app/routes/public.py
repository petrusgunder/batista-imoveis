from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
@public_bp.route('/home')
def home():
    return render_template('home.html')

@public_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')