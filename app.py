from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'torneos.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
    """)

    # Torneos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS torneos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        fecha_inicio TEXT,
        fecha_fin TEXT
    )
    """)

    # Equipos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        torneo_id INTEGER,
        FOREIGN KEY(torneo_id) REFERENCES torneos(id)
    )
    """)

    # Partidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS partidos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo1_id INTEGER,
        equipo2_id INTEGER,
        goles1 INTEGER,
        goles2 INTEGER,
        fecha TEXT,
        torneo_id INTEGER,
        FOREIGN KEY(equipo1_id) REFERENCES equipos(id),
        FOREIGN KEY(equipo2_id) REFERENCES equipos(id),
        FOREIGN KEY(torneo_id) REFERENCES torneos(id)
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- TORNEOS ----------------

@app.route("/torneos")
def torneos():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM torneos")
    torneos = cursor.fetchall()

    conn.close()

    return render_template("torneos.html", torneos=torneos)


@app.route("/torneos/create", methods=["GET", "POST"])
def crear_torneo():

    if request.method == "POST":
        nombre = request.form["nombre"]
        inicio = request.form["inicio"]
        fin = request.form["fin"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO torneos(nombre, fecha_inicio, fecha_fin)
        VALUES (?, ?, ?)
        """, (nombre, inicio, fin))

        conn.commit()
        conn.close()

        return redirect(url_for("torneos"))

    return render_template("crear_torneo.html")


@app.route("/torneos/delete/<int:id>")
def eliminar_torneo(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM torneos WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("torneos"))


# ---------------- EQUIPOS ----------------

@app.route("/equipos")
def equipos():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT equipos.*, torneos.nombre AS torneo
    FROM equipos
    JOIN torneos ON equipos.torneo_id = torneos.id
    """)

    equipos = cursor.fetchall()

    cursor.execute("SELECT * FROM torneos")
    torneos = cursor.fetchall()

    conn.close()

    return render_template("equipos.html", equipos=equipos, torneos=torneos)


@app.route("/equipos/create", methods=["POST"])
def crear_equipo():

    nombre = request.form["nombre"]
    torneo = request.form["torneo"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO equipos(nombre, torneo_id)
    VALUES (?, ?)
    """, (nombre, torneo))

    conn.commit()
    conn.close()

    return redirect(url_for("equipos"))


# ---------------- PARTIDOS ----------------

@app.route("/partidos")
def partidos():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT p.id,
           e1.nombre AS equipo1,
           e2.nombre AS equipo2,
           p.goles1,
           p.goles2,
           p.fecha,
           t.nombre AS torneo
    FROM partidos p
    JOIN equipos e1 ON p.equipo1_id = e1.id
    JOIN equipos e2 ON p.equipo2_id = e2.id
    JOIN torneos t ON p.torneo_id = t.id
    """)

    partidos = cursor.fetchall()

    cursor.execute("SELECT * FROM equipos")
    equipos = cursor.fetchall()

    cursor.execute("SELECT * FROM torneos")
    torneos = cursor.fetchall()

    conn.close()

    return render_template(
        "partidos.html",
        partidos=partidos,
        equipos=equipos,
        torneos=torneos
    )


@app.route("/partidos/create", methods=["POST"])
def crear_partido():

    e1 = request.form["equipo1"]
    e2 = request.form["equipo2"]
    g1 = request.form["goles1"]
    g2 = request.form["goles2"]
    fecha = request.form["fecha"]
    torneo = request.form["torneo"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO partidos
    (equipo1_id, equipo2_id, goles1, goles2, fecha, torneo_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (e1, e2, g1, g2, fecha, torneo))

    conn.commit()
    conn.close()

    return redirect(url_for("partidos"))


# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)
