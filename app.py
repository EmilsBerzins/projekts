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
def pilsetas():
    conn = get_db_connection()
    pilsetas = conn.execute("SELECT * FROM pilsetas").fetchall()
    conn.close()
    return render_template("index.html", pilsetas=pilsetas)
