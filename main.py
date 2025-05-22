from flask import Flask, render_template, request, jsonify
import nicole
import os

app = Flask(__name__)

# Carrega processador e base textual
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

        # Modelo carregado sob demanda para reduzir uso
        modelo = nicole.get_modelo()
        embeddings_pdf = modelo.encode(trechos_pdf, convert_to_tensor=True) if trechos_pdf else None

        resposta, imagem = nicole.responder_usuario(
            usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador, modelo
        )

        return jsonify({"resposta": resposta, "imagem": imagem}), 200

    except Exception as e:
        print(f"[ERRO /perguntar] {e}")
        return jsonify({"resposta": "Erro interno ao processar a resposta.", "imagem": None}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
