import random, os, json, fitz, gc
from googlesearch import search
from sentence_transformers import SentenceTransformer, util
import torch

PASTA_PROCESSADOR = "dados"
DIRETORIO_PDFS = "pdfs"

# Modelo global (carregado só uma vez)
modelo_global = SentenceTransformer('paraphrase-MiniLM-L3-v2')

def get_modelo():
    return modelo_global

def resposta_positiva(nome):
    return random.choice([
        f"Claro, {nome}! Aqui está o que encontrei:",
        f"Olha só, {nome}, achei isso para você:",
        f"Certo, {nome}. Veja essa informação:"
    ])

def resposta_negativa(nome):
    return random.choice([
        f"Hmm... ainda não sei responder isso, {nome} 😕.",
        f"Essa me pegou, {nome}! Mas estou sempre aprendendo!",
        f"Não achei ainda, {nome}. Me ensina? 🙏"
    ])

def carregar_processador():
    processador = {}
    if not os.path.exists(PASTA_PROCESSADOR):
        return {}
    for arq in os.listdir(PASTA_PROCESSADOR):
        if arq.endswith(".json"):
            with open(os.path.join(PASTA_PROCESSADOR, arq), "r", encoding="utf-8") as f:
                processador.update(json.load(f))
    return processador

def preparar_base(processador):
    frases = list(processador.keys())
    with torch.no_grad():
        embeddings = modelo_global.encode(frases, convert_to_tensor=True)
    return frases, embeddings

def carregar_trechos_pdfs(pasta):
    trechos = []
    if not os.path.exists(pasta):
        return trechos
    for nome in os.listdir(pasta):
        if nome.endswith(".pdf"):
            doc = fitz.open(os.path.join(pasta, nome))
            for page in doc:
                texto = page.get_text()
                for p in texto.split("\n\n"):
                    if p.strip().count('\n') >= 10:
                        trechos.append(p.strip().replace('\n', ' '))
            doc.close()
    return trechos

def buscar_no_google(consulta):
    try:
        for url in search(consulta, num_results=3, lang="pt"):
            if url.startswith("http") and not any(x in url for x in [".png", ".jpg", "/images/"]):
                return url
    except Exception:
        return None
    return None

def responder_usuario(pergunta, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador):
    modelo = get_modelo()
    with torch.no_grad():
        emb_usuario = modelo.encode(pergunta, convert_to_tensor=True)
        sim = util.cos_sim(emb_usuario, embeddings_base)[0]
        idx = sim.argmax().item()
        score = sim[idx].item() * 100

        if score >= 75:
            chave = frases_base[idx]
            significado = processador[chave]["significado"]
            return f"{resposta_positiva(nome)} {significado}", None

        elif embeddings_pdf:
            sim_pdf = util.cos_sim(emb_usuario, embeddings_pdf)[0]
            idx_pdf = sim_pdf.argmax().item()
            score_pdf = sim_pdf[idx_pdf].item() * 100

            if score_pdf >= 50:
                trecho = trechos_pdf[idx_pdf]
                return f"{resposta_positiva(nome)} {trecho[:700]}...", None

        url = buscar_no_google(pergunta)
        if url:
            return f"Não encontrei uma resposta exata, {nome}, mas talvez isso ajude: {url}", None
        else:
            return resposta_negativa(nome), None
