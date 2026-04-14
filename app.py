from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e0edae4f06c1be9a705b03e1faa2ac57998f30fc4337be34'


# 🔌 DB connection
def get_db():
    return sqlite3.connect('users.db')


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


# 📊 DASHBOARD 1
@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect('/')

    return render_template('dashboard.html', name=session['username'])


# 📊 DASHBOARD 2 (NEW)

@app.route('/dashboard2', methods=['GET', 'POST'])
def dashboard2():

    if 'username' not in session:
        return redirect('/')

    username = session['username']

    conn = get_db()
    cursor = conn.cursor()

    # ➕ ADD DATA (same POST logic)
    if request.method == 'POST':
        subject = request.form['subject']
        hours = request.form['hours']

        cursor.execute(
            "INSERT INTO study_logs (username, subject, hours) VALUES (?, ?, ?)",
            (username, subject, hours)
        )

        conn.commit()
        return redirect('/dashboard2')

    # 📊 FETCH DATA (replaces file read + split)
    cursor.execute(
        "SELECT id, subject, hours FROM study_logs WHERE username=?",
        (username,)
    )

    rows = cursor.fetchall()
    conn.close()

    # 🔄 convert to your SAME format (so HTML works same)
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "subject": row[1],
            "hours": row[2]
        })

    return render_template('dashboard2.html', data=data, name=username)


@app.route("/done/<int:id>")
def done(id):

    if 'username' not in session:
        return redirect('/')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM study_logs WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard2")

# 🆕 CREATE ACCOUNT PAGE
@app.route('/create_account')
def create_page():
    return render_template('create.html')


# ➕ CREATE ACCOUNT
@app.route('/create', methods=['POST'])
def create_account():

    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "Username already exists!"

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()

    return redirect('/')


# ⚙️ SETTINGS PAGE (NEW)
@app.route('/settings')
def settings():

    if 'username' not in session:
        return redirect('/')

    return render_template('settings.html', name=session['username'])


# 📜 TERMS & CONDITIONS (NEW)
@app.route('/terms')
def terms():
    return render_template('t&c1.html')
@app.route("/calculator")
def calculator():
    return render_template('calculator.html')
@app.route("/t&c")
def t_c():
    return render_template("t&c.html")



# 🔓 LOGOUT
@app.route('/logout')
def logout():
   
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
