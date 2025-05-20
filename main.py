from flask import Flask, render_template, request, jsonify
import nicole
from nicole import responder_usuario
import os

app = Flask(__name__)

# --- Carregar JSON e embeddings uma vez ---
processador = nicole.carregar_processador()
frases_base, embeddings_base = nicole.preparar_base(processador)
trechos_pdf = nicole.carregar_trechos_pdfs(nicole.DIRETORIO_PDFS)

# Embeddings dos PDFs — apenas se houver PDFs
if trechos_pdf:
    frases_tmp = trechos_pdf
    modelo_tmp = nicole.get_modelo()
    embeddings_pdf = modelo_tmp.encode(frases_tmp, convert_to_tensor=True)
    del modelo_tmp
else:
    embeddings_pdf = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    data = request.get_json()
    usuario = data["mensagem"].lower().strip()
    nome = data["nome"]

    resposta, imagem = responder_usuario(
        usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador
    )
    return jsonify({"resposta": resposta, "imagem": imagem})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
