from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
# Secure key for sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'e0edae4f06c1be9a705b03e1faa2ac57998f30fc4337be34')

# ✅ Database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "users.db")

# ✅ Create tables automatically
def create_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        hours TEXT
    )""")
    conn.commit()
    conn.close()

create_table()

def get_db():
    return sqlite3.connect(db_path)

# 🏠 LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('loginerror.html')
    return render_template('login.html')

# 📝 SIGN UP / CREATE ACCOUNT
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            return "Username already exists!"
        
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('create.html')

# 📊 DASHBOARD 1
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html', name=session['username'])

# 📊 DASHBOARD 2
@app.route('/dashboard2', methods=['GET', 'POST'])
def dashboard2():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        subject = request.form['subject']
        hours = request.form['hours']
        cursor.execute("INSERT INTO study_logs (username, subject, hours) VALUES (?, ?, ?)", (username, subject, hours))
        conn.commit()
        conn.close()
        return redirect('/dashboard2')
    cursor.execute("SELECT id, subject, hours FROM study_logs WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()
    data = [{"id": row[0], "subject": row[1], "hours": row[2]} for row in rows]
    return render_template('dashboard2.html', data=data)

# ⚙️ SETTINGS PAGE
@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect('/')
    return render_template('settings.html', name=session['username'])

# 📜 TERMS & MISC
@app.route('/terms')
def terms():
    return render_template('t&c1.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/t&c')
def t_c():
    return render_template('t&c.html')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear() # Clears the session so they are actually logged out
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
