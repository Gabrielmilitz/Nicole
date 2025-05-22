from flask import Flask, render_template, request, jsonify
import nicole
import os

# Evita deadlock do HuggingFace em servidores com fork
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)

# Dados base
processador = nicole.carregar_processador()
frases_base, embeddings_base = nicole.preparar_base(processador)
trechos_pdf = nicole.carregar_trechos_pdfs(nicole.DIRETORIO_PDFS)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    try:
        data = request.get_json()
        usuario = data.get("mensagem", "").strip().lower()
        nome = data.get("nome", "Usuário")

        resposta, imagem = nicole.responder_usuario(
            usuario, nome, frases_base, embeddings_base, trechos_pdf, processador
        )

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
