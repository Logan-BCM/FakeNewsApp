from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from detector import predict
from utils import fetch_from_url
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.secret_key = 'fakenews123'
bycrpt = Bcrypt(app)

#MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fakenews'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():

    value = ""
    if request.method == 'POST':
        url = request.form.get('url')  # Retrieve URL from form data
        content = fetch_from_url(url)
        value = predict(content)

    return render_template('index.html', value=value)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if 'name' in request.form and 'email' in request.form and 'password' in request.form:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            hashed_password= bycrpt.generate_password_hash(password).decode('utf-8')
        
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            mysql.connection.commit()
            cur.close()
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
        user = True
        cur.close()
        
        if user:
            return redirect(url_for('index'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')


if __name__ == '_main_':
    app.run(debug=True)