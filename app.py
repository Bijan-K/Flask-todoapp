from flask import Flask, request, g, redirect, url_for, render_template, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = "todo.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route("/")
def index():
    db = get_db()
    cur = db.execute("SELECT id, task, completed FROM tasks ORDER BY completed, id")
    tasks = cur.fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    task = request.form["task"]
    db = get_db()
    db.execute("INSERT INTO tasks (task, completed) VALUES (?, 0)", [task])
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", [task_id])
    db.commit()
    return redirect(url_for("index"))


@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    task = request.form["task"]
    db = get_db()
    db.execute("UPDATE tasks SET task = ? WHERE id = ?", [task, task_id])
    db.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET completed = NOT completed WHERE id = ?", [task_id])
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete_completed")
def delete_completed():
    db = get_db()
    db.execute("DELETE FROM tasks WHERE completed = 1")
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
