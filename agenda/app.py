from flask import Flask, session, render_template, request, g, redirect,url_for, flash
import datetime, calendario, auth
from werkzeug.exceptions import abort
from database import get_db, dbPosts
from auth import login_required

app = Flask(__name__)
app.secret_key = "dev"


@app.route("/")
def index():
    auth.load_logged_in_user()
    posts = dbPosts()
    session['data-visualizada'], session['mes-visualizado'], session['mes-objeto'] = calendario.data_util()
    return render_template('calendario/index.html', posts=posts, mes=session['mes-objeto'], btnMeio = session['mes-visualizado'])

@app.route('/dia/<diaDoMes>', methods=['POST', 'GET'])
def dia(diaDoMes):
    if diaDoMes is None:
        abort(404)
    posts = dbPosts()
    session['dia-visualizado'] = diaDoMes
    return render_template('calendario/dia.html', diaVisualizado = session['dia-visualizado'], posts=posts, mesVisualizado=session['mes-visualizado'])




@app.route("/prox", methods=["POST", "GET"])
def prox():
    nova = session['data-visualizada']
    nova = datetime.datetime.strptime(nova, '%Y-%m-%d').date()
    posts = dbPosts()
    if nova.month == 12:
        nova = datetime.datetime(nova.year + 1, 1, 1)
    else:
        nova = datetime.date(nova.year, nova.month + 1, 1)

    session['data-visualizada'], session['mes-visualizado'], session['mes-objeto'] = calendario.data_util(nova)
    session.modified = True
    return render_template("calendario/index.html", posts=posts, mes=session['mes-objeto'], btnMeio = session['mes-visualizado'], dataVis=session['data-visualizada'])

@app.route("/ant", methods=["POST", "GET"])
def ant():
    nova = session['data-visualizada']
    nova = datetime.datetime.strptime(nova, '%Y-%m-%d').date()
    posts = dbPosts()
    if nova.month == 1:
        nova = datetime.datetime(nova.year - 1, 12, 1)
    else:
        nova = datetime.date(nova.year, nova.month -1, 1)

    session['data-visualizada'], session['mes-visualizado'], session['mes-objeto'] = calendario.data_util(nova)
    session.modified = True
    return render_template("calendario/index.html", posts=posts, mes=session['mes-objeto'], btnMeio = session['mes-visualizado'], dataVis=session['data-visualizada'])


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
            db.cursor(dictionary=True).execute(
                'INSERT INTO event (title, body, author_id, time)'
                ' VALUES (%s, %s, %s, %s)',
                (title, body, g.user['id'], timestamp),
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('calendario/criar.html')

def get_post(id, check_author=True):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM event p JOIN users u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = cursor.fetchone()

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
            db.cursor().execute(
                'UPDATE event SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )

            db.commit()
            return redirect(url_for('index'))

    return render_template('calendario/atualizar.html', post=post)

    
@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.cursor().execute('DELETE FROM event WHERE id = %s', (id,))
    db.commit()
    return redirect(url_for('index'))

app.register_blueprint(auth.bp, url_prefix='/auth')

 
if __name__ == '__main__':
    app.run(debug=True)