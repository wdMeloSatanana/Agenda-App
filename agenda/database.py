import mysql.connector
from flask import g
from dotenv import dotenv_values

config = dotenv_values(".env")


mydb = mysql.connector.connect(
    host='localhost',
    user=config['DB_USER'],
    password=config['DB_PASS']
)

print('Conectado a base de dados')


if mydb.is_connected():
    db_info = mydb.get_server_info()
    print('Conectado ao servidor MySQL', db_info)
    cursor = mydb.cursor()
    cursor.execute("SHOW DATABASES")
    listaDBs = [str(val[0]) for val in cursor]

    if "users" not in listaDBs:
        cursor.execute("CREATE DATABASE users")
        mydb.database='users'
        cursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL)")
        cursor.execute("CREATE TABLE event (id INTEGER PRIMARY KEY AUTO_INCREMENT, author_id INTEGER NOT NULL, CREATED TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(), title TEXT NOT NULL, body TEXT NOT NULL, time TEXT NOT NULL, FOREIGN KEY (author_id) REFERENCES users (id))")
        print("base")
        mydb.commit()
    mydb.database='users'

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
                host='localhost',
                user=config['DB_USER'],
                password=config['DB_PASS'],
                database='users'
                )

    return g.db

def dbPosts():
    db = get_db().cursor(dictionary=True)
    db.execute(
        'SELECT p.id, title, body, created, author_id, username, time'
        ' FROM event p JOIN users u ON p.author_id = u.id'
        ' ORDER BY created DESC')
    posts = db.fetchall()
    return posts


if mydb.is_connected():
    cursor.close()
    mydb.close()
    print("Conexão MySQL encerrada.")


