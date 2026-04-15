from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "e0edae4f06c1be9a705b03e1faa2ac57998f30fc4337be34"

# Setup robust database path for server environments
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    # Study logs table for Dashboard 2
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        hours TEXT
    )""")
    conn.commit()
    conn.close()

# Initialize tables on startup
init_db()

def get_db():
    return sqlite3.connect(db_path)

# --- LOGIN & AUTHENTICATION ---

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
            return redirect(url_for('dashboard'))
        else:
            return render_template('loginerror.html')

    return render_template('login.html')

@app.route('/create_account')
def create_page():
    # Just opens the page
    return render_template('create.html')

@app.route('/create', methods=['POST'])
def create_account():
    # Handles the form submission from create.html
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "Username already exists!"

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return redirect(url_for('login'))

@app.route('/forgotpassword')
def forgot_password():
    # Added this because it was visible in your file explorer screenshot
    return render_template('forgotpassword.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# --- MAIN APPLICATION DASHBOARDS ---

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', name=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/dashboard2', methods=['GET', 'POST'])
def dashboard2():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        subject = request.form.get('subject')
        hours = request.form.get('hours')
        cursor.execute("INSERT INTO study_logs (username, subject, hours) VALUES (?, ?, ?)", (username, subject, hours))
        conn.commit()
        conn.close()
        return redirect('/dashboard2')

    cursor.execute("SELECT id, subject, hours FROM study_logs WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()

    data = [{"id": r[0], "subject": r[1], "hours": r[2]} for r in rows]
    return render_template("dashboard2.html", name=username, data=data)


# --- UTILITY & INFO PAGES ---

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


if __name__ == "__main__":
    app.run(debug=True)
