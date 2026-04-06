from flask import Flask, render_template, request, redirect, url_for ,session

app = Flask(__name__)

VALID_PASSWORD = "1234"   # <-- change to your password

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if password == VALID_PASSWORD:
            with open("name.txt","w") as f:
                f.write(username)
            return render_template('dashboard.html', name=username)
        else:
            return render_template('loginerror.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard(name):

    name = session.get('name',name) 
    

    return render_template('dashboard.html', name=name)

@app.route('/dashboard2', methods=['GET','POST'])
def dashboard2():
    try:
        with open("name.txt","r") as f:
            username = f.read()
    except:
        username = "User"

    if request.method == 'POST':
        subject = request.form["subject"]
        hours = request.form["hours"]

        with open("data.txt", "a") as f:
            f.write(f"{subject}|{hours}\n")

        return redirect("/dashboard2")

    data = []
    try:
        with open("data.txt", "r") as f:
            lines = f.readlines()

            for i, line in enumerate(lines):
                if "|" in line:
                    subject, hours = line.strip().split("|")

                    data.append({
                        "id": i,
                        "subject": subject,
                        "hours": hours
                    })
    except:
        pass

    return render_template("dashboard2.html", data=data, name=username)

@app.route("/done/<int:id>")
def done(id):
    try:
        with open("data.txt", "r") as f:
            lines = f.readlines()

        if id < len(lines):
            lines.pop(id)

        with open("data.txt", "w") as f:
            f.writelines(lines)
    except:
        pass

    return redirect("/dashboard2")






@app.route('/logout')
def logout():
    # For now, we just redirect them back to the login page
    return redirect(url_for('login'))

@app.route('/back')
def back():
    return redirect(url_for('login'))
@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/calculator')
def calculator():
    return render_template("calculator.html",)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
