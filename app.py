from flask import Flask, render_template, request, redirect
import sqlite3
from pathlib import Path
import uuid
import os

app = Flask(__name__)


def get_db_connection():
    db = Path(__file__).parent / "db.sqlite"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pilsetas", methods=["GET", "POST"])
def pilsetas():
    conn = get_db_connection()
    if request.method == "POST":
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO statistika (iedzivotaji, platiba) VALUES (?, ?)",
            (
                request.form["iedzivotaji"],
                request.form["platiba"],
            ),
        )
        statistika_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO pilsetas (nosaukums, statistika_id) VALUES (?, ?)",
            (
                request.form["nosaukums"],
                statistika_id,
            ),
        )
        conn.commit()

    pilsetas = conn.execute("SELECT * FROM pilsetas").fetchall()
    conn.close()
    return render_template("pilsetas_index.html", pilsetas=pilsetas)


@app.route("/pilsetas/create")
def pievienot_pilsetu():
    return render_template("pilsetas_create.html")


@app.route("/pilsetas/<int:id>")
def pilseta(id):
    conn = get_db_connection()
    pilseta = conn.execute(
        "SELECT pilsetas.id, nosaukums, iedzivotaji, platiba FROM pilsetas JOIN statistika ON pilsetas.statistika_id = statistika.id WHERE pilsetas.id = ?",
        (id,),
    ).fetchone()
    conn.close()
    return render_template("pilsetas_show.html", pilseta=pilseta)


@app.route("/pilsetas/<int:id>/edit", methods=["GET", "POST"])
def edit_pilseta(id):
    conn = get_db_connection()
    if request.method == "POST":
        cursor = conn.cursor()
        pilseta = cursor.execute(
            "SELECT statistika_id FROM pilsetas WHERE id = ?",
            (id,),
        ).fetchone()
        cursor.execute(
            "UPDATE pilsetas SET nosaukums = ? WHERE id = ?",
            (request.form["nosaukums"], id),
        )
        cursor.execute(
            "UPDATE statistika SET iedzivotaji = ?, platiba = ? WHERE id = ?",
            (request.form["iedzivotaji"], request.form["platiba"], pilseta["statistika_id"]),
        )
        conn.commit()
        conn.close()
        return redirect(f"/pilsetas/{id}")
    
    pilseta = conn.execute(
        "SELECT pilsetas.id, nosaukums, iedzivotaji, platiba FROM pilsetas JOIN statistika ON pilsetas.statistika_id = statistika.id WHERE pilsetas.id = ?",
        (id,),
    ).fetchone()
    conn.close()
    return render_template("pilsetas_edit.html", pilseta=pilseta)


@app.route("/pilsetas/<int:id>/dzest")
def dzest_pilsetu(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    pilseta = cursor.execute(
        "SELECT * FROM pilsetas WHERE id = ?",
        (id,),
    ).fetchone()
    cursor.execute(
        "DELETE FROM pilsetas WHERE id = ?",
        (id,),
    )
    cursor.execute(
        "DELETE FROM statistika WHERE id = ?",
        (pilseta["statistika_id"],),
    )
    fotos = cursor.execute(
        "SELECT foto_url FROM apskates_objekti WHERE pilsetas_id = ?",
        (id,),
    ).fetchall()
    cursor.execute(
        "DELETE FROM apskates_objekti WHERE pilsetas_id = ?",
        (id,),
    )
    conn.commit()
    for foto in fotos:
        path = Path(__file__).parent / "static" / "images" / "objekti" / foto[0]
        os.remove(path)

    return redirect("/pilsetas")


@app.route("/pilsetas/<int:id>/objekti", methods=["GET", "POST"])
def apskates_objekti(id):
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file and file.filename:
            filename = str(uuid.uuid4()) + ".jpg"
            path = Path(__file__).parent / "static" / "images" / "objekti" / filename
            file.save(path)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO apskates_objekti (foto_url, pilsetas_id) VALUES (?, ?)",
                (
                    filename,
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

if __name__ == "__main__":
    app.run(debug=True)