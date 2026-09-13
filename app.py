import os

from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor


app = Flask(__name__)


def conectar_banco():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", "5432"),
        sslmode="require"
    )


# READ - listar produtos
@app.route("/")
def index():
    conexao = conectar_banco()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id, nome, preco FROM produtos ORDER BY id;")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("index.html", produtos=produtos)


# CREATE - cadastrar produto
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO produtos (nome, preco) VALUES (%s, %s);",
            (nome, preco)
        )

        conexao.commit()

        cursor.close()
        conexao.close()

        return redirect(url_for("index"))

    return render_template("cadastrar.html")


# UPDATE - editar produto
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexao = conectar_banco()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])

        cursor.execute(
            """
            UPDATE produtos
            SET nome = %s, preco = %s
            WHERE id = %s;
            """,
            (nome, preco, id)
        )

        conexao.commit()

        cursor.close()
        conexao.close()

        return redirect(url_for("index"))

    cursor.execute(
        "SELECT id, nome, preco FROM produtos WHERE id = %s;",
        (id,)
    )

    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    if produto is None:
        return "Produto não encontrado", 404

    return render_template("editar.html", produto=produto)


# DELETE - excluir produto
@app.route("/excluir/<int:id>")
def excluir(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id = %s;",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)