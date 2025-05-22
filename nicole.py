import os
import json
import fitz
import gc
import random
import torch
from googlesearch import search
from sentence_transformers import SentenceTransformer, util

PASTA_PROCESSADOR = "dados"
DIRETORIO_PDFS = "pdfs"

modelo_global = SentenceTransformer('paraphrase-MiniLM-L3-v2')

def get_modelo():
    return modelo_global

def resposta_positiva(nome):
    return random.choice([
        f"Claro, {nome}! Veja só:",
        f"Achei isso, {nome}:",
        f"Está aqui, {nome}:"
    ])

def resposta_negativa(nome):
    return random.choice([
        f"Poxa, {nome}, ainda não sei responder isso. 😞",
        f"Não encontrei nada, {nome}. Me ensina? 🙏",
    ])

def carregar_processador():
    base = {}
    if not os.path.exists(PASTA_PROCESSADOR):
        return base
    for arq in os.listdir(PASTA_PROCESSADOR):
        if arq.endswith(".json"):
            with open(os.path.join(PASTA_PROCESSADOR, arq), encoding="utf-8") as f:
                base.update(json.load(f))
    return base

def preparar_base(processador):
    frases = list(processador.keys())
    with torch.no_grad():
        embeddings = modelo_global.encode(frases, convert_to_tensor=True)
    gc.collect()
    return frases, embeddings

def carregar_e_processar_pdfs():
    trechos = []
    if not os.path.exists(DIRETORIO_PDFS):
        return trechos, None

    for arq in os.listdir(DIRETORIO_PDFS):
        if arq.endswith(".pdf"):
            try:
                with fitz.open(os.path.join(DIRETORIO_PDFS, arq)) as pdf:
                    for page in pdf:
                        texto = page.get_text("text")
                        paragrafos = [p.strip().replace('\n', ' ') for p in texto.split('\n\n') if p.strip()]
                        trechos.extend(paragrafos)
            except Exception as e:
                print(f"[ERRO PDF] {arq}: {e}")

    if trechos:
        with torch.no_grad():
            embeddings = modelo_global.encode(trechos, convert_to_tensor=True)
        gc.collect()
        return trechos, embeddings
    return trechos, None

def buscar_no_google(consulta):
    try:
        for url in search(consulta, num_results=3, lang="pt"):
            if url.startswith("http") and not any(x in url for x in [".jpg", ".png", "imgres", "/images/", "/search?"]):
                return url
    except Exception as e:
        print(f"[GOOGLE] Erro: {e}")
    return None

def responder_usuario(usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador):
    with torch.no_grad():
        emb_usuario = modelo_global.encode(usuario, convert_to_tensor=True)

        sim_base = util.cos_sim(emb_usuario, embeddings_base)[0]
        idx_base = sim_base.argmax().item()
        score_base = sim_base[idx_base].item() * 100

        if score_base >= 75:
            chave = frases_base[idx_base]
            resposta = processador[chave]["significado"]
            return f"{resposta_positiva(nome)} {resposta}", None

        if embeddings_pdf:
            sim_pdf = util.cos_sim(emb_usuario, embeddings_pdf)[0]
            idx_pdf = sim_pdf.argmax().item()
            score_pdf = sim_pdf[idx_pdf].item() * 100
            if score_pdf >= 50:
                return f"{resposta_positiva(nome)} {trechos_pdf[idx_pdf][:700]}...", None

        url = buscar_no_google(usuario)
        if url:
            return f"Ainda não sei isso, {nome}, mas esse link pode ajudar: {url}", None
        return resposta_negativa(nome), None
