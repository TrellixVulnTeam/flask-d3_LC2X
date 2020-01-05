from flask import Flask, render_template, redirect, url_for, request, make_response, session
import sqlite3
from sqlite3 import Error
import pwd_hasher
import logging
import base64

app = Flask(__name__)


@app.route('/')
def dashboard():
    if 'name' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('dashboard.html', name=session['name'])


@app.route('/pdc')
def pdc():
    if 'name' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('pdc.html', name=session['name'])


@app.route('/hello')
def hello():
    return 'Hello World'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        # session['name'] = ''
        email = request.form['email']
        pwd = request.form['pwd']
        logging.info(email)

        if email == '' or pwd == '':
            return render_template('login.html', email=email, pwd=pwd)

        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM user WHERE email = ?", (email,))
                users = cur.fetchall()
                # for user in users:
                #     print(user)
                if len(users) < 1:
                    print('doesn\'t exist')
                    return redirect(url_for('login'))

                stored_pwd = users[0][3]
                name = users[0][1]
                # stored_pwd = base64.b64decode(stored_pwd.decode("utf-8"))
                if not pwd_hasher.verify_password(stored_pwd, pwd):
                    print('wrong password')
                    return redirect(url_for('login'))
                session['name'] = name
                print('login ok')
        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form['email']
        name = request.form['name']
        pwd = pwd_hasher.hash_password(request.form['pwd'])
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO user (name, email, pwd) VALUES (?, ?, ?)",
                            (name, email, pwd))
                conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'ffce805ea02504f5a59820c1ea8985e0432f39566059d7f8'
    app.run("127.0.0.1", 8001, True)
