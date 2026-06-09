from datetime import datetime

from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random, string

app = Flask(__name__)
app.secret_key = "2fe2f5cbef19637547cc3ac5937d2c70e81018cdd9a8369ae07c0101ffd21b88"

WORLD_CUP_TEAMS = [
    "Algerije", "Argentinië", "Australië", "België",
    "Bosnië en Herzegovina", "Brazilië", "Canada", "Colombia",
    "Curaçao", "Democratische Republiek Congo", "Duitsland",
    "Ecuador", "Egypte", "Engeland", "Frankrijk", "Ghana",
    "Haïti", "Iran", "Irak", "Ivoorkust", "Japan", "Jordanië",
    "Kaapverdië", "Kroatië", "Marokko", "Mexico", "Nederland",
    "Nieuw-Zeeland", "Noorwegen", "Oezbekistan", "Oostenrijk",
    "Panama", "Paraguay", "Portugal", "Qatar", "Saoedi-Arabië",
    "Schotland", "Senegal", "Spanje", "Tunesië", "Turkije",
    "Uruguay", "Verenigde Staten", "Zuid-Afrika", "Zuid-Korea",
    "Zweden", "Zwitserland"
]


#Registreer
@app.route("/register", methods=["GET", "POST"])
def register():
#data van user ophalen
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "onvolledige gegevens"
#paswoord beveiligen dmv hashing
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()
#data in database steken, user_id koppelen aan sessie
#check op dubbele username
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            """, (username, hashed_password))
            conn.commit()
            session["user_id"] = cursor.lastrowid 

        except sqlite3.IntegrityError:
            conn.close()
            return "Username bestaat al"

        conn.close()
        return redirect("/")

    return render_template("register.html")


#Login
@app.route("/login", methods=["GET", "POST"])
def login():
#data van user ophalen
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()
#data van in database vergelijken met getypte data
        cursor.execute("""
            SELECT id, password_hash
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):

            session["user_id"] = user[0]
            return redirect("/")

        return "Invalid credentials"

    return render_template("login.html")


#Logout
@app.route("/logout")
def logout():
#verwijder alles in session
    session.clear()
    return redirect("/")


#Dashboard
@app.route("/")
def dashboard():
    conn = sqlite3.connect("wk_prono.db")
    cursor = conn.cursor()
#haal data op voor leaderboard
    cursor.execute("""
        SELECT users.username, COALESCE(SUM(countries.score * picks.factor), 0) AS points
        FROM users
        LEFT JOIN picks
        ON users.id = picks.user_id
        LEFT JOIN countries
        ON picks.country_id = countries.id
        GROUP BY users.id, users.username
        ORDER BY points DESC, users.username ASC
    """)

    leaderboard = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", leaderboard=leaderboard)


#Regels
@app.route("/regels")
def regels():
    return render_template("regels.html")
#Punten
@app.route("/punten")
def punten():
#check voor user id
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("wk_prono.db")
    cursor = conn.cursor()
#haal alles uit database om punten te berekenen
    cursor.execute("""
    SELECT countries.score, picks.factor
    FROM picks
    JOIN countries
    ON picks.country_id = countries.id
    WHERE picks.user_id = ?
    """, (session["user_id"],))
    sum = 0
    for row in cursor.fetchall():
        score = row[0]
        factor = row[1]
        sum += score * factor
    conn.close()
    return render_template("punten.html", sum=sum)
#Competitie

@app.route("/competitie")
def competitie():
#check voor user id
    if "user_id" not in session:
        return redirect("/login")
#maak unieke code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    conn = sqlite3.connect("wk_prono.db")
    cursor = conn.cursor()

    #competitie aanmaken in db
    cursor.execute("""
        INSERT INTO leagues (name, join_code)
        VALUES (?, ?)
    """, ("Mijn competitie", code))

    league_id = cursor.lastrowid

    #user aan competitie zetten
    cursor.execute("""
        UPDATE users
        SET league_id = ?
        WHERE id = ?
    """, (league_id, session["user_id"]))

    conn.commit()
    conn.close()

    return f"Deel deze code: {code}"

@app.route("/join", methods=["GET", "POST"])
def join():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        code = request.form.get("code")

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()

        #zoek competitie
        cursor.execute("""
            SELECT id
            FROM leagues
            WHERE join_code = ?
        """, (code,))

        league = cursor.fetchone()

        if not league:
            return "Code bestaat niet"

        league_id = league[0]

        #user koppelen
        cursor.execute("""
            UPDATE users
            SET league_id = ?
            WHERE id = ?
        """, (league_id, session["user_id"]))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("join.html")

#Keuze
@app.route("/keuze", methods=["GET", "POST"])
def keuze():
#check voor user id
    if "user_id" not in session:
        return redirect("/login")

    DEADLINE = datetime(2026, 6, 11, 19, 0, 0)

    if datetime.now() > DEADLINE:
        return "De pronostiek is gesloten"
#data van user ophalen
    if request.method == "POST":

        conn = sqlite3.connect("wk_prono.db")
        cursor = conn.cursor()

        selected_countries = []
        selected_factors = []

        for i in range(20):

            country_id = request.form.get(f"country_{i}")
            factor = request.form.get(f"factor_{i}")

            if not country_id or not factor:
                return "Vul alle velden in"

            selected_countries.append(int(country_id))
            selected_factors.append(int(factor))

        # check dubell land of factor
        if len(set(selected_countries)) != 20:
            return "Duplicate countries not allowed"

        if len(set(selected_factors)) != 20:
            return "Duplicate factors not allowed"

        user_id = session["user_id"]

        #indien al picks verwijder en vul in
        cursor.execute("""
            DELETE FROM picks
            WHERE user_id = ?
        """, (user_id,))

        for i in range(20):
            cursor.execute("""
                INSERT INTO picks (user_id, country_id, factor)
                VALUES (?, ?, ?)
            """, (
                user_id,
                selected_countries[i],
                selected_factors[i]
            ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("keuze.html")

    # vul lenderlandse naam toe
    cursor.execute("SELECT id, dutch_name FROM countries ORDER BY dutch_name ASC")
    countries = cursor.fetchall()

    conn.close()

    return render_template("keuze.html", countries=countries)

if __name__ == "__main__":
    app.run(debug=True)
