from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

VALID_PASSWORD = "1234"   # <-- change to your password

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if password == VALID_PASSWORD:
            return redirect(url_for('dashboard', name=username))
        else:
            return "Wrong password ❌"

    return render_template('login.html')


@app.route('/dashboard/<name>')
def dashboard(name):
    return render_template('dashboard.html', name=name)


@app.route('/logout')
def logout():
    # For now, we just redirect them back to the login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
