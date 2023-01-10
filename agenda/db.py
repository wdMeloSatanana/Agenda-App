from werkzeug.security import check_password_hash, generate_password_hash 
import sqlite3

data = [
    ["user1", "123"],
    ["user2", "453"],
    ["user3", "356"],
    ["user4", "358"],
    ["user5", "359"],
    ["user6", "388"],
]

def sanitizedList():
    for i in range(len(data)):
        data[i][1] = generate_password_hash(data[i][1])
    return data

listaDB = sanitizedList()
connection = sqlite3.connect("users.db")
cursor = connection.cursor()


cursor.execute("create table users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
cursor.execute("create table event (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER NOT NULL, CREATED TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, title TEXT NOT NULL, body TEXT NOT NULL, time TEXT NOT NULL, FOREIGN KEY (author_id) REFERENCES users (id))")

for i in range(len(listaDB)):
  cursor.execute("insert into users (username, password) values (?,?)", (listaDB[i][0], listaDB[i][1]),)
  print("added ", listaDB[i][0])

connection.commit()
connection.close()