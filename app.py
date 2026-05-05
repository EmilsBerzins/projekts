from flask import Flask, render_template, request, redirect
import sqlite3
from pathlib import Path

app = Flask(__name__)


def get_db_connection():
    db = Path(__file__).parent / "db.sqlite"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pilsetas")
def pilsetas():
    conn = get_db_connection()
    pilsetas = conn.execute("SELECT * FROM pilsetas").fetchall()
    conn.close()
    return render_template("pilsetas_index.html", pilsetas=pilsetas)


@app.route("/pilsetas/<int:id>")
def pilseta(id):
    conn = get_db_connection()
    pilseta = conn.execute(
        "SELECT pilsetas.id, nosaukums, iedzivotaji, platiba FROM pilsetas JOIN statistika ON pilsetas.statistika_id = statistika.id WHERE pilsetas.id = ?",
        (id,),
    ).fetchone()
    conn.close()
    return render_template("pilsetas_show.html", pilseta=pilseta)


@app.route("/pilsetas/<int:id>/objekti", methods=["GET", "POST"])
def apskates_objekti(id):
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file and file.filename:
            path = (
                Path(__file__).parent / "static" / "images" / "objekti" / file.filename
            )
            file.save(path)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO apskates_objekti (foto_url, pilsetas_id) VALUES (?, ?)",
                (
                    file.filename,
                    id,
                ),
            )
            conn.commit()

    conn = get_db_connection()
    objekti = conn.execute(
        "SELECT * FROM apskates_objekti WHERE pilsetas_id = ?",
        (id,),
    ).fetchall()
    conn.close()
    return render_template("objekti_show.html", objekti=objekti, id=id)


@app.route("/pilsetas/<int:id>/objekti/add")
def pievienot_objektu(id):
    return render_template("objekti_add.html", id=id)
