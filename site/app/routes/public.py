from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    return render_template('base.html')

@public_bp.route('/home')
def home_page():
    return render_template('home.html')