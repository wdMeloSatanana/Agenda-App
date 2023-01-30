import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')



@bp.route('/registrar', methods=('GET', 'POST'))
def registrar():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = "Nome de usuário deve ser preenchido"
        elif not password:
            error = "Senha deve ser preenchida"

        
        if error is None:
            try:
                db.cursor(dictionary=True).execute(
                    "INSERT INTO users (username, password) VALUES(%s,%s)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except:
                error = f"Usuário {username} já registrado."
            else:
                return redirect(url_for("auth.login"))
    
    return render_template('auth/registrar.html')


@bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db().cursor(dictionary=True)
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = %s ', (username,)
        )
        user = db.fetchone()
        
    
        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreto.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            print("Usuario na sessao")
            print(g.user)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cursor =  get_db().cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM users WHERE id = %s', (user_id,))
        g.user = cursor.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
