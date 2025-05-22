from flask import Flask, render_template, request, jsonify
import nicole
from nicole import responder_usuario
import os

app = Flask(__name__)

# Carrega dados e embeddings uma única vez
processador = nicole.carregar_processador()
frases_base, embeddings_base = nicole.preparar_base(processador)
trechos_pdf = nicole.carregar_trechos_pdfs(nicole.DIRETORIO_PDFS)

if trechos_pdf:
    embeddings_pdf = nicole.get_modelo().encode(trechos_pdf, convert_to_tensor=True)
else:
    embeddings_pdf = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json(force=True)
        usuario = data.get("mensagem", "").strip().lower()
        nome = data.get("nome", "amigo")

        resposta, imagem = responder_usuario(
            usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador
        )

        return jsonify({"resposta": resposta, "imagem": imagem})

    except Exception as e:
        print(f"[ERRO INTERNO] {e}")
        return jsonify({
            "resposta": "Erro interno no servidor. 😕",
            "imagem": None
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
