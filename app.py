import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.secret_key = "your_secret_key"


def get_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS comments
            (id INTEGER PRIMARY KEY, user_id INTEGER, comment TEXT, FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    conn.commit()
    return conn, c


class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    conn, c = get_db()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if row:
        return User(row[0], row[1], row[2], row[3])
    return None


# Home Route
@app.route("/")
def index():
    return render_template("index.html")


# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn, c = get_db()
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("signup"))

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            flash("Username already exists")
            return redirect(url_for("signup"))

        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password)),
        )
        conn.commit()
        flash("Account created successfully")
        return redirect(url_for("login"))

    return render_template("signup.html")


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn, c = get_db()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        row = c.fetchone()
        if row and check_password_hash(row[3], password):
            user = User(row[0], row[1], row[2], row[3])
            login_user(user)
            flash("Login successful")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Dashboard Route
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        return render_template("dashboard.html")
    else:
        flash("You need to be logged in to access this page")
        return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/community")
def community():
    if current_user.is_authenticated:
        return render_template("community.html")
    else:
        flash("You need to be logged in to access this page")
        return redirect(url_for("login"))


@app.route("/bmi_calculator", methods=["GET", "POST"])
def bmi_calculator():
    if request.method == "POST":
        weight = float(request.form["weight"])
        height = float(request.form["height"])

        bmi = weight / (height**2)
        bmi_category = get_bmi_category(bmi)

        return render_template(
            "bmi_calculator.html", bmi=bmi, bmi_category=bmi_category
        )
    return render_template("bmi_calculator.html")


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


@app.route("/calories_calculator")
def calories_calculator():
    return render_template("calories_calculator.html")


if __name__ == "__main__":
    app.run(debug=True)
