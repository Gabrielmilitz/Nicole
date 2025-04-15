from flask import Flask, render_template, request, jsonify
import nicole
from nicole import responder_usuario



app = Flask(__name__)


processador = nicole.carregar_processador()
frases_base, embeddings_base = nicole.preparar_base(processador)
trechos_pdf = nicole.carregar_trechos_pdfs(nicole.DIRETORIO_PDFS)
if trechos_pdf:
    embeddings_pdf = nicole.modelo.encode(trechos_pdf, convert_to_tensor=True)
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

    
    resposta, imagem = nicole.responder_usuario(
        usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador
    )

    return jsonify({"resposta": resposta, "imagem": imagem})

# --- MAIN ---
if __name__ == "__main__":
    app.run(debug=True)
