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
try:
    if trechos_pdf:
        modelo_tmp = nicole.get_modelo()  # Você deve definir essa função no nicole.py
        embeddings_pdf = modelo_tmp.encode(trechos_pdf, convert_to_tensor=True)
        del modelo_tmp  # Libera memória
    else:
        embeddings_pdf = None
except Exception as e:
    print(f"❌ Erro ao carregar embeddings dos PDFs: {e}")
    embeddings_pdf = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json()
        usuario = data["mensagem"].lower().strip()
        nome = data["nome"]

        resposta, imagem = responder_usuario(
            usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador
        )
        return jsonify({"resposta": resposta, "imagem": imagem})
    
    except Exception as e:
        print(f"❌ Erro na rota /perguntar: {e}")
        return jsonify({"resposta": "Erro interno ao processar a pergunta.", "imagem": None}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
