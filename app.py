from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "database.db"

# ========================
# CONEXIÓN A BD
# ========================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ========================
# CREAR TABLAS
# ========================
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    # Tabla torneos con FK a usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS torneos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            lugar TEXT NOT NULL,
            creador_id INTEGER,
            FOREIGN KEY(creador_id) REFERENCES usuarios(id)
        )
    """)

    # Tabla equipos con FK a torneos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            torneo_id INTEGER NOT NULL,
            FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ========================
# FUNCIONES CRUD USUARIOS
# ========================
def obtener_usuarios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def crear_usuario_db(nombre, email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, email) VALUES (?, ?)", (nombre, email))
    conn.commit()
    conn.close()

# ========================
# FUNCIONES CRUD TORNEOS
# ========================
def obtener_torneos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT torneos.*, usuarios.nombre AS creador_nombre
        FROM torneos LEFT JOIN usuarios ON torneos.creador_id = usuarios.id
    """)
    torneos = cursor.fetchall()
    conn.close()
    return torneos

def obtener_torneo(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM torneos WHERE id = ?", (id,))
    torneo = cursor.fetchone()
    conn.close()
    return torneo

def crear_torneo_db(nombre, fecha, lugar, creador_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO torneos (nombre, fecha, lugar, creador_id) VALUES (?, ?, ?, ?)",
                   (nombre, fecha, lugar, creador_id))
    conn.commit()
    conn.close()

def editar_torneo_db(id, nombre, fecha, lugar):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE torneos SET nombre = ?, fecha = ?, lugar = ? WHERE id = ?",
                   (nombre, fecha, lugar, id))
    conn.commit()
    conn.close()

def eliminar_torneo_db(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM torneos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# ========================
# FUNCIONES CRUD EQUIPOS
# ========================
def obtener_equipos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT equipos.id, equipos.nombre, torneos.nombre AS torneo_nombre, torneos.id AS torneo_id
        FROM equipos
        JOIN torneos ON equipos.torneo_id = torneos.id
    """)
    equipos = cursor.fetchall()
    conn.close()
    return equipos

def obtener_equipo(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipos WHERE id = ?", (id,))
    equipo = cursor.fetchone()
    conn.close()
    return equipo

def crear_equipo_db(nombre, torneo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO equipos (nombre, torneo_id) VALUES (?, ?)", (nombre, torneo_id))
    conn.commit()
    conn.close()

def editar_equipo_db(id, nombre, torneo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE equipos SET nombre = ?, torneo_id = ? WHERE id = ?", (nombre, torneo_id, id))
    conn.commit()
    conn.close()

def eliminar_equipo_db(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# ========================
# RUTAS USUARIOS
# ========================
@app.route("/usuarios/crear", methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        try:
            crear_usuario_db(nombre, email)
            flash("Usuario creado correctamente", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error al crear usuario: {e}", "error")
            return render_template("crear_usuario.html")

    return render_template("crear_usuario.html")

# ========================
# RUTAS TORNEOS
# ========================
@app.route("/")
def index():
    torneos = obtener_torneos()
    equipos = obtener_equipos()
    return render_template("index.html", torneos=torneos, equipos=equipos)

@app.route("/crear", methods=["GET", "POST"])
def crear_torneo():
    usuarios = obtener_usuarios()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha = request.form.get("fecha", "").strip()
        lugar = request.form.get("lugar", "").strip()
        creador_id = request.form.get("creador_id")

        if not nombre or not fecha or not lugar or not creador_id:
            flash("Todos los campos son obligatorios", "error")
            return render_template("crear.html", usuarios=usuarios)

        try:
            crear_torneo_db(nombre, fecha, lugar, creador_id)
            flash("Torneo creado exitosamente", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error al crear torneo: {e}", "error")
            return render_template("crear.html", usuarios=usuarios)

    return render_template("crear.html", usuarios=usuarios)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_torneo(id):
    torneo = obtener_torneo(id)
    if not torneo:
        flash("Torneo no encontrado", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha = request.form.get("fecha", "").strip()
        lugar = request.form.get("lugar", "").strip()

        if not nombre or not fecha or not lugar:
            flash("Todos los campos son obligatorios", "error")
            return render_template("editar.html", torneo=torneo)

        try:
            editar_torneo_db(id, nombre, fecha, lugar)
            flash("Torneo actualizado exitosamente", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error al actualizar torneo: {e}", "error")
            return render_template("editar.html", torneo=torneo)

    return render_template("editar.html", torneo=torneo)

@app.route("/eliminar/<int:id>")
def eliminar_torneo(id):
    torneo = obtener_torneo(id)
    if not torneo:
        flash("Torneo no encontrado", "error")
    else:
        try:
            eliminar_torneo_db(id)
            flash("Torneo eliminado exitosamente", "success")
        except Exception as e:
            flash(f"Error al eliminar torneo: {e}", "error")
    return redirect(url_for("index"))

# ========================
# RUTAS EQUIPOS
# ========================
@app.route("/equipos")
def equipos_interface():
    equipos = obtener_equipos()
    torneos = obtener_torneos()
    return render_template("equipos.html", equipos=equipos, torneos=torneos)

@app.route("/equipos/crear", methods=["GET", "POST"])
def crear_equipo():
    torneos = obtener_torneos()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        torneo_id = request.form.get("torneo_id")

        if not nombre or not torneo_id:
            flash("Todos los campos son obligatorios", "error")
            return render_template("crear_equipo.html", torneos=torneos)

        try:
            crear_equipo_db(nombre, torneo_id)
            flash("Equipo creado exitosamente", "success")
            return redirect(url_for("equipos_interface"))
        except Exception as e:
            flash(f"Error al crear equipo: {e}", "error")
            return render_template("crear_equipo.html", torneos=torneos)

    return render_template("crear_equipo.html", torneos=torneos)

@app.route("/equipos/editar/<int:id>", methods=["GET", "POST"])
def editar_equipo(id):
    equipo = obtener_equipo(id)
    torneos = obtener_torneos()
    if not equipo:
        flash("Equipo no encontrado", "error")
        return redirect(url_for("equipos_interface"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        torneo_id = request.form.get("torneo_id")

        if not nombre or not torneo_id:
            flash("Todos los campos son obligatorios", "error")
            return render_template("crear_equipo.html", equipo=equipo, torneos=torneos)

        try:
            editar_equipo_db(id, nombre, torneo_id)
            flash("Equipo actualizado exitosamente", "success")
            return redirect(url_for("equipos_interface"))
        except Exception as e:
            flash(f"Error al actualizar equipo: {e}", "error")
            return render_template("crear_equipo.html", equipo=equipo, torneos=torneos)

    return render_template("crear_equipo.html", equipo=equipo, torneos=torneos)

@app.route("/equipos/eliminar/<int:id>")
def eliminar_equipo(id):
    equipo = obtener_equipo(id)
    if not equipo:
        flash("Equipo no encontrado", "error")
    else:
        try:
            eliminar_equipo_db(id)
            flash("Equipo eliminado exitosamente", "success")
        except Exception as e:
            flash(f"Error al eliminar equipo: {e}", "error")
    return redirect(url_for("equipos_interface"))

# ========================
# RUTA PARA VER TORNEO DETALLADO
# ========================
@app.route("/torneo/<int:id>")
def ver_torneo(id):
    torneo = obtener_torneo(id)
    if not torneo:
        flash("Torneo no encontrado", "error")
        return redirect(url_for("index"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipos WHERE torneo_id = ?", (id,))
    equipos = cursor.fetchall()
    conn.close()

    return render_template("ver_torneo.html", torneo=torneo, equipos=equipos)

# ========================
# EJECUTAR
# ========================
if __name__ == "__main__":
    app.run(debug=True)
