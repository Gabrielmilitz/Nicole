import os
import json
import fitz
import gc
import torch
from sentence_transformers import SentenceTransformer, util
from googlesearch import search

PASTA_DADOS = "dados"
PASTA_PDFS = "pdfs"
MODELO_NOME = "paraphrase-MiniLM-L3-v2"

def carregar_json_diretorio(pasta):
    dados = {}
    if os.path.exists(pasta):
        for arquivo in os.listdir(pasta):
            if arquivo.endswith(".json"):
                with open(os.path.join(pasta, arquivo), "r", encoding="utf-8") as f:
                    dados.update(json.load(f))
    return dados

def carregar_trechos_pdf():
    trechos = []
    if not os.path.exists(PASTA_PDFS):
        return trechos

    for arquivo in os.listdir(PASTA_PDFS):
        if not arquivo.endswith(".pdf"):
            continue
        caminho = os.path.join(PASTA_PDFS, arquivo)
        with fitz.open(caminho) as pdf:
            for pagina in pdf:
                texto = pagina.get_text().strip()
                for trecho in texto.split('\n\n'):
                    if trecho.count('\n') >= 10:
                        trechos.append(trecho.replace('\n', ' '))
    return trechos

def buscar_no_google(pergunta):
    try:
        for url in search(pergunta, num_results=5, lang="pt"):
            if url.startswith("http") and all(x not in url for x in [".jpg", ".png", ".jpeg", "/images/", "/search?"]):
                return url
    except Exception as e:
        print(f"[Erro Google] {e}")
    return None

def inicializar_nicole():
    print("Carregando modelo e dados...")
    modelo = SentenceTransformer(MODELO_NOME)
    base = carregar_json_diretorio(PASTA_DADOS)
    frases = list(base.keys())
    embeddings = modelo.encode(frases, convert_to_tensor=True)

    trechos_pdf = carregar_trechos_pdf()
    embeddings_pdf = modelo.encode(trechos_pdf, convert_to_tensor=True) if trechos_pdf else None

    return {
        "modelo": modelo,
        "base": base,
        "frases": frases,
        "embeddings": embeddings,
        "trechos_pdf": trechos_pdf,
        "embeddings_pdf": embeddings_pdf,
    }

def responder(mensagem, nome, config):
    modelo = config["modelo"]
    base = config["base"]
    frases = config["frases"]
    embeddings = config["embeddings"]
    trechos_pdf = config["trechos_pdf"]
    embeddings_pdf = config["embeddings_pdf"]

    with torch.no_grad():
        input_embed = modelo.encode(mensagem, convert_to_tensor=True)
        scores = util.cos_sim(input_embed, embeddings)[0]
        top_idx = scores.argmax().item()
        top_score = scores[top_idx].item() * 100

        if top_score >= 75:
            resposta = base[frases[top_idx]]["significado"]
            return f"{nome}, aqui está o que encontrei:\n{resposta}", None

        if embeddings_pdf:
            scores_pdf = util.cos_sim(input_embed, embeddings_pdf)[0]
            idx_pdf = scores_pdf.argmax().item()
            score_pdf = scores_pdf[idx_pdf].item() * 100
            if score_pdf >= 50:
                return f"{nome}, encontrei este trecho útil:\n{trechos_pdf[idx_pdf][:700]}...", None

        link = buscar_no_google(mensagem)
        if link:
            return f"{nome}, não achei resposta exata, mas talvez isso ajude:\n{link}", None

        return f"Desculpe, {nome}, não consegui entender. Pode reformular?", None
