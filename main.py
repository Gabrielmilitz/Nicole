from flask import Flask, render_template, request, jsonify
import nicole
import os

app = Flask(__name__)

base = nicole.carregar_base()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json(force=True)
        nome = data.get("nome", "Usuário")
        mensagem = data.get("mensagem", "")

        resposta, imagem = nicole.responder_usuario(mensagem, nome, base)
        return jsonify({"resposta": resposta, "imagem": imagem})

    except Exception as e:
        print(f"[ERRO] {e}")
        return jsonify({
            "resposta": "Erro interno no servidor. 😕",
            "imagem": None
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
