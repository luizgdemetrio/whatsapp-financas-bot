from flask import Flask, request, jsonify
import sqlite3
from config import DB_NAME

app = Flask(__name__)


def conectar_bd():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


@app.route("/add_transacao", methods=["POST"])
def add_transacao():
    data = request.json
    descricao = data.get("descricao")
    tipo = data.get("tipo")
    valor = data.get("valor")
    parcelas = data.get("parcelas", 1)

    if not descricao or not tipo or not valor:
        return jsonify({"error": "Dados insuficientes"}), 400

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transacoes (descricao, tipo, valor, parcelas) VALUES (?, ?, ?, ?)",
        (descricao, tipo, valor, parcelas),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Transação adicionada com sucesso!"})


@app.route("/resumo", methods=["GET"])
def resumo():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT descricao, tipo, valor, parcelas FROM transacoes")
    transacoes = cursor.fetchall()
    conn.close()

    if not transacoes:
        return jsonify({"message": "Nenhuma transação registrada."})

    resultado = {"transacoes": []}
    for t in transacoes:
        resultado["transacoes"].append(
            {"descricao": t[0], "tipo": t[1], "valor": t[2], "parcelas": t[3]}
        )

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)
