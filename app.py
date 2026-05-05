from flask import Flask, render_template
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
