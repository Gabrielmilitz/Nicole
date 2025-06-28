from flask import Flask, render_template, request, jsonify
import nicole
import os

app = Flask(__name__)

# Carrega os dados da IA apenas uma vez
processador = nicole.carregar_processador()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json()
        usuario = data.get("mensagem", "").strip().lower()

        resposta, imagem = nicole.responder_usuario(usuario, processador)
        return jsonify({"resposta": resposta, "imagem": imagem}), 200

    except Exception as e:
        print(f"[ERRO INTERNO] {e}")
        return jsonify({
            "resposta": "Houve um erro interno no servidor. 😞",
            "imagem": None
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
