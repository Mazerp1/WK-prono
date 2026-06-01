#flask --app app --debug run#
from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
WORLD_CUP_TEAMS = [
    "Algerije",
    "Argentinië",
    "Australië",
    "België",
    "Bosnië en Herzegovina",
    "Brazilië",
    "Canada",
    "Colombia",
    "Curaçao",
    "Democratische Republiek Congo",
    "Duitsland",
    "Ecuador",
    "Egypte",
    "Engeland",
    "Frankrijk",
    "Ghana",
    "Haïti",
    "Iran",
    "Irak",
    "Ivoorkust",
    "Japan",
    "Jordanië",
    "Kaapverdië",
    "Kroatië",
    "Marokko",
    "Mexico",
    "Nederland",
    "Nieuw-Zeeland",
    "Noorwegen",
    "Oezbekistan",
    "Oostenrijk",
    "Panama",
    "Paraguay",
    "Portugal",
    "Qatar",
    "Saoedi-Arabië",
    "Schotland",
    "Senegal",
    "Spanje",
    "Tunesië",
    "Turkije",
    "Uruguay",
    "Verenigde Staten",
    "Zuid-Afrika",
    "Zuid-Korea",
    "Zweden",
    "Zwitserland"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/regels")
def regels():
    return render_template("regels.html")

@app.route("/keuze", methods=["GET", "POST"])
def keuze():

    if request.method == "POST":

        selected_countries = []
        selected_factors = []

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()

        for i in range(20):
            country = request.form.get(f"country_{i}")
            factor = request.form.get(f"factor_{i}")

            if not country or not factor:
                return "Vul alle velden in"

            selected_countries.append(country)
            selected_factors.append(int(factor))

        if len(set(selected_countries)) != 20:
            return "Duplicate countries not allowed"

        if len(set(selected_factors)) != 20:
            return "Duplicate factors not allowed"

        user_id = session.get("user_id")

        for i in range(20):
            cursor.execute("""
                INSERT INTO picks (user_id, country, factor)
                VALUES (?, ?, ?)
            """, (user_id, selected_countries[i], selected_factors[i]))

        conn.commit()
        conn.close()

        return "Picks opgeslagen!"

    return render_template("keuze.html", countries=WORLD_CUP_TEAMS)
if __name__ == "__main__":
    app.run(debug=True)