from detector import predict
from utils import (
	fetch_url_content,
	sha256_hash,
	url_validator
)

from flask import (
	Flask,
	render_template,
	request,
	redirect,
	session,
	url_for
)
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "fakenews123"

#MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "fakenews"
mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def index():
	explanation = ""
	value = ""

	if not session:
		return redirect(url_for("login"))

	if request.method == "POST":
		url = request.form.get("url")  # Retrieve URL from form data
		is_valid_url = url_validator(url)
		if is_valid_url:
			content = fetch_url_content(url)
			if content:
				user_id = session["id"]

				cur = mysql.connection.cursor()
				cur.execute(
					"INSERT INTO article_data (url, content, user_id) VALUES (%s, %s, %s)",
					(url, content, user_id)
				)
				mysql.connection.commit()
				article_id = cur.lastrowid

				value = predict(content)
				classification_result = 1 if value else 0

				cur.execute(
					"INSERT INTO classification_results (article_id, classification_result) VALUES (%s, %s)",
					(article_id, classification_result)
				)
				mysql.connection.commit()
				cur.close()
			else:
				value = "Error!!"
				explanation = ""
		else:
			value = "Invalid url!!"
			explanation = ""

	return render_template("index.html", value=value, explanation=explanation)


@app.route("/signup", methods=["GET", "POST"])
def signup():
	error = ""

	if request.method == "POST":
		if "name" in request.form and "email" in request.form and "password" in request.form:
			name = request.form["name"]
			email = request.form["email"]
			password = request.form["password"]
			hashed_password = sha256_hash(password)
		
			cur = mysql.connection.cursor()
			cur.execute("SELECT * FROM users WHERE email = %s", (email,))
			user = cur.fetchone()

			if not user:
				cur.execute(
					"INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
					(name, email, hashed_password)
				)
				mysql.connection.commit()
				cur.close()

				user_id = cur.lastrowid
				session["id"] = user_id
				session["name"] = name
				session["email"] = email

				return redirect(url_for("index"))

			error = "Email already taken"				
	return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
	error = ""

	if request.method == "POST":
		email = request.form["email"]
		password = request.form["password"]
		hashed_password = sha256_hash(password)

		cur = mysql.connection.cursor()
		cur.execute(
			"SELECT user_id, name, email FROM users WHERE email = %s AND password = %s",
			(email, hashed_password)
		)
		user = cur.fetchone()
		cur.close()
		
		if user:
			user_id, name, email = user
			session["id"] = user_id
			session["name"] = name
			session["email"] = email

			return redirect(url_for("index"))

		error = "Invalid email or password"

	return render_template("login.html", error=error)


@app.route("/logout")
def logout():
	session.pop("id", None)
	session.pop("name", None)
	session.pop("email", None)
	return redirect(url_for("login"))


if __name__ == "__main__":
	app.run(debug=True)
