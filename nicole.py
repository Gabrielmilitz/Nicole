import os
import json
import random
import fitz
import gc
from googlesearch import search
from sentence_transformers import SentenceTransformer, util
import torch

PASTA_PROCESSADOR = "dados"
DIRETORIO_PDFS = "pdfs"

# Carrega modelo global leve
modelo_global = SentenceTransformer('paraphrase-MiniLM-L3-v2')

def get_modelo():
    return modelo_global

def resposta_positiva(nome):
    return random.choice([
        f"Claro, {nome}! Aqui está o que encontrei:",
        f"Olha só, {nome}, achei isso para você:",
        f"Certo, {nome}. Veja essa informação:",
    ])

def resposta_negativa(nome):
    return random.choice([
        f"Hmm... ainda não sei responder isso, {nome} 😕.",
        f"Essa me pegou, {nome}! Mas estou sempre aprendendo! 🚀",
        f"Não achei ainda, {nome}. Me ensina? 🙏",
    ])

def carregar_processador():
    processador = {}
    if not os.path.exists(PASTA_PROCESSADOR):
        return processador

    for arq in os.listdir(PASTA_PROCESSADOR):
        if arq.endswith(".json"):
            try:
                with open(os.path.join(PASTA_PROCESSADOR, arq), "r", encoding="utf-8") as f:
                    processador.update(json.load(f))
            except Exception as e:
                print(f"[ERRO] Falha ao carregar {arq}: {e}")
    return processador

def preparar_base(processador):
    frases = list(processador.keys())
    with torch.no_grad():
        embeddings = get_modelo().encode(frases, convert_to_tensor=True)
    gc.collect()
    return frases, embeddings

def carregar_trechos_pdfs(diretorio):
    trechos = []
    if not os.path.exists(diretorio):
        return trechos

    for arq in os.listdir(diretorio):
        if arq.endswith(".pdf"):
            try:
                with fitz.open(os.path.join(diretorio, arq)) as pdf:
                    for pag in pdf:
                        texto = pag.get_text()
                        for par in texto.split("\n\n"):
                            p = par.strip().replace("\n", " ")
                            if len(p.split()) > 30:
                                trechos.append(p)
            except Exception as e:
                print(f"[ERRO PDF] {arq}: {e}")
    return trechos

def buscar_no_google(consulta):
    try:
        for url in search(consulta, num_results=3, lang="pt"):
            if "http" in url and not any(x in url for x in [".jpg", ".png", "imgres"]):
                return url
    except Exception as e:
        print(f"[GOOGLE ERROR] {e}")
    return None

def responder_usuario(usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador):
    modelo = get_modelo()

    with torch.no_grad():
        entrada = modelo.encode(usuario, convert_to_tensor=True)

        if embeddings_base is not None:
            sim = util.cos_sim(entrada, embeddings_base)[0]
            idx = sim.argmax().item()
            score = sim[idx].item() * 100

            if score >= 75:
                chave = frases_base[idx]
                return f"{resposta_positiva(nome)} {processador[chave]['significado'].capitalize()}", None

        if embeddings_pdf:
            sim_pdf = util.cos_sim(entrada, embeddings_pdf)[0]
            idx_pdf = sim_pdf.argmax().item()
            score_pdf = sim_pdf[idx_pdf].item() * 100

            if score_pdf >= 50:
                trecho = trechos_pdf[idx_pdf]
                return f"{resposta_positiva(nome)} {trecho[:700]}...", None

    url = buscar_no_google(usuario)
    if url:
        return f"Não encontrei uma resposta exata, {nome}, mas talvez isso ajude: {url}", None
    return resposta_negativa(nome), None
