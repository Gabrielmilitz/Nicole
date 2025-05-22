from flask import Flask, render_template, request, jsonify
import nicole
import os
import traceback

app = Flask(__name__)

# Carregamento inicial otimizado
try:
    processador = nicole.carregar_processador()
    frases_base, embeddings_base = nicole.preparar_base(processador)
    trechos_pdf = nicole.carregar_trechos_pdfs(nicole.DIRETORIO_PDFS)
    embeddings_pdf = nicole.get_modelo().encode(trechos_pdf, convert_to_tensor=True) if trechos_pdf else None
except Exception as e:
    print("[ERRO INICIAL] Falha ao carregar dados ou modelo:", e)
    processador = {}
    frases_base = []
    embeddings_base = None
    trechos_pdf = []
    embeddings_pdf = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"resposta": "Requisição inválida.", "imagem": None}), 400

        usuario = data.get("mensagem", "").strip().lower()
        nome = data.get("nome", "Usuário")

        if not usuario:
            return jsonify({"resposta": "Digite uma pergunta válida.", "imagem": None}), 400

        resposta, imagem = nicole.responder_usuario(
            usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador
        )
        return jsonify({"resposta": resposta, "imagem": imagem}), 200

    except Exception as e:
        print("[ERRO INTERNO]", traceback.format_exc())
        return jsonify({
            "resposta": "Ocorreu um erro interno no servidor. Tente novamente mais tarde.",
            "imagem": None
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
