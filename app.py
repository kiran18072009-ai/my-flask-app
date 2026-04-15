from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "123"

# Setup Database Path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Table for Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    # Table for Study Logs (Dashboard2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        hours TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect(db_path)

# --- ROUTES ---

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
            session['user'] = username
            return redirect('/dashboard')
        else:
            # Matches your loginerror.html
            return render_template('loginerror.html')
            
    return render_template("login.html")

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()
            
    return render_template("create.html")

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        # Pass name=session['user'] to match your {{ name }} in dashboard.html
        return render_template("dashboard.html", name=session['user'])
    return redirect('/')

@app.route('/dashboard2', methods=['GET', 'POST'])
def dashboard2():
    if 'user' not in session:
        return redirect('/')
    
    username = session['user']
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        subject = request.form.get('subject')
        hours = request.form.get('hours')
        cursor.execute("INSERT INTO study_logs (username, subject, hours) VALUES (?, ?, ?)", (username, subject, hours))
        conn.commit()
        return redirect('/dashboard2')

    cursor.execute("SELECT id, subject, hours FROM study_logs WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()

    # Formats data for your dashboard2.html loop
    data = [{"id": r[0], "subject": r[1], "hours": r[2]} for r in rows]
    return render_template("dashboard2.html", name=username, data=data)

@app.route('/calculator')
def calculator():
    return render_template("calculator.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/terms')
def terms():
    return render_template("t&c1.html")

@app.route('/t&c')
def tandc():
    return render_template("t&c.html")

@app.route('/analyse')
def analyse():
    return render_template("analyse.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
