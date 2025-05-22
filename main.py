from flask import Flask, render_template, request, jsonify
from nicole import inicializar_nicole, responder
import os

app = Flask(__name__)

# Inicialização única ao subir o app
config = inicializar_nicole()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json(force=True)
        nome = data.get("nome", "Usuário").strip()
        mensagem = data.get("mensagem", "").strip()

        if not mensagem:
            return jsonify({"resposta": "Mensagem vazia recebida.", "imagem": None}), 400

        resposta, imagem = responder(mensagem, nome, config)
        return jsonify({"resposta": resposta, "imagem": imagem})

    except Exception as e:
        print(f"[ERRO INTERNO] {e}")
        return jsonify({
            "resposta": "Ocorreu um erro interno ao processar sua pergunta.",
            "imagem": None
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
