from flask import Flask, session, render_template, request, g,redirect,url_for, flash
import sqlite3 , datetime,calendar, functools, calendario
from werkzeug.security import check_password_hash, generate_password_hash 
from werkzeug.exceptions import abort

app = Flask(__name__)
app.secret_key = "dev"

@app.route("/", methods=["POST", "GET"])
def index():
    session['conteudo']  = get_db_as_tuple()
    return render_template("index.html", conteudo=session['conteudo'])

@app.route("/main")
def main():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, time'
        ' FROM event p JOIN users u ON p.author_id = u.id'
        ' ORDER BY created DESC').fetchall()
    #if not (session.get('data-visualizada') and session.get('mes-objeto') and session.get('mes-visualizado')):
    session['data-visualizada'], session['mes-visualizado'], session['mes-objeto'] = calendario.data_util()
    return render_template('calendario/main.html', posts=posts, mes=session['mes-objeto'], btnMeio = session['mes-visualizado'])

@app.route('/dia/<diaDoMes>', methods=['POST', 'GET'])
def dia(diaDoMes):
    if diaDoMes is None:
        abort(404)
    db = get_db()
    posts = db.execute(
    'SELECT p.id, title, body, created, author_id, username, time'
    ' FROM event p JOIN users u ON p.author_id = u.id'
    ' ORDER BY created DESC').fetchall()
    session['dia-visualizado'] = diaDoMes
    return render_template('calendario/dia.html', diaVisualizado = session['dia-visualizado'], posts=posts, mesVisualizado=session['mes-visualizado'])




@app.route("/prox", methods=["POST", "GET"])
def prox():
    nova = session['data-visualizada']
    nova = datetime.datetime.strptime(nova, '%Y-%m-%d').date()

    if nova.month == 12:
        nova = datetime.datetime(nova.year + 1, 1, 1)
    else:
        nova = datetime.date(nova.year, nova.month + 1, 1)

    session['data-visualizada'], session['mes-visualizado'], session['mes-objeto'] = calendario.data_util(nova)
    session.modified = True
    return render_template("calendario/main.html", mes=session['mes-objeto'], btnMeio = session['mes-visualizado'], dataVis=session['data-visualizada'])

@app.route("/ant", methods=["POST", "GET"])
def ant():
    nova = session['data-visualizada']
    nova = datetime.datetime.strptime(nova, '%Y-%m-%d').date()
     
    if nova.month == 1:
        nova = datetime.datetime(nova.year - 1, 12, 1)
    else:
        nova = datetime.date(nova.year, nova.month -1, 1)

    session['data-visualizada'], session['mes-visualizado'], session['mes-objeto'] = calendario.data_util(nova)
    session.modified = True
    return render_template("calendario/main.html", mes=session['mes-objeto'], btnMeio = session['mes-visualizado'], dataVis=session['data-visualizada'])



@app.route('/registrar', methods=('GET', 'POST'))
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
                db.execute(
                    "INSERT INTO users (username, password) VALUES(?,?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Usuário {username} já registrado."
            else:
                return redirect(url_for("login"))
    
    return render_template('auth/registrar.html')


@app.route('/login', methods=("GET", "POST"))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()


        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreto.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('main'))

        flash(error)

    return render_template('auth/login.html')


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

def get_db_as_tuple():
    db = getattr(g, '_database', None)
    if db is None:
        db = g.database = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute("select username, password from users")
        dados = cursor.fetchall()
        for i in dados:
            print(i)
        dados = [(str(val[0]), str(val[1])) for val in dados]

    return dados

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('users.db')
        g.db.row_factory = sqlite3.Row
    return g.db

 

@app.route('/criar', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        timestamp  = request.form['time']
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M')
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:00")
        error = None
 
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO event (title, body, author_id, time)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], timestamp),
            )
            db.commit()
            return redirect(url_for('main'))

    return render_template('calendario/criar.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM event p JOIN users u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@app.route('/<int:id>/atualizar', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE event SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )

            db.commit()
            return redirect(url_for('main'))

    return render_template('calendario/atualizar.html', post=post)

    
@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM event WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True)