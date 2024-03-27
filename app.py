from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'fakenews123'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fakenews'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    url = None  # Initialize URL variable
    if request.method == 'POST':
        url = request.form.get('url')  # Retrieve URL from form data
        # return url
        print("------", url, request.args)
        return render_template('signup.html')

    return render_template('index.html')

# def index():
#     return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if 'name' in request.form and 'email' in request.form and 'password' in request.form:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            mysql.connection.commit()
            cur.close()
            #return 'Sign-up successful!'
            return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        if user:
            #return 'Login successful!'
            return redirect(url_for('index'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
