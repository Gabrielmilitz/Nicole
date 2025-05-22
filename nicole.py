import random
import os
import json
import fitz
import gc
from sentence_transformers import SentenceTransformer, util
import torch

PASTA_PROCESSADOR = "dados"
DIRETORIO_PDFS = "pdfs"

def get_modelo():
    return SentenceTransformer("paraphrase-MiniLM-L3-v2")

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
        return {}
    for arq in os.listdir(PASTA_PROCESSADOR):
        if arq.endswith(".json"):
            with open(os.path.join(PASTA_PROCESSADOR, arq), encoding="utf-8") as f:
                processador.update(json.load(f))
    return processador

def preparar_base(processador):
    frases = list(processador.keys())
    modelo = get_modelo()
    with torch.no_grad():
        embeddings = modelo.encode(frases, convert_to_tensor=True)
    return frases, embeddings

def carregar_trechos_pdfs(pasta):
    trechos = []
    if not os.path.exists(pasta):
        return trechos
    for nome in os.listdir(pasta):
        if nome.endswith(".pdf"):
            try:
                with fitz.open(os.path.join(pasta, nome)) as pdf:
                    for pagina in pdf:
                        texto = pagina.get_text()
                        for paragrafo in texto.split("\n\n"):
                            p = paragrafo.strip().replace("\n", " ")
                            if len(p.split()) > 50:
                                trechos.append(p)
            except Exception as e:
                print(f"[ERRO PDF] {nome}: {e}")
    return trechos

def responder_usuario(pergunta, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador, modelo):
    with torch.no_grad():
        emb_pergunta = modelo.encode(pergunta, convert_to_tensor=True)

        # Base textual
        sim_texto = util.cos_sim(emb_pergunta, embeddings_base)[0]
        indice_texto = sim_texto.argmax().item()
        score_texto = sim_texto[indice_texto].item() * 100

        if score_texto >= 75:
            chave = frases_base[indice_texto]
            significado = processador[chave]["significado"]
            return f"{resposta_positiva(nome)} {significado}", None

        # PDF
        if embeddings_pdf:
            sim_pdf = util.cos_sim(emb_pergunta, embeddings_pdf)[0]
            indice_pdf = sim_pdf.argmax().item()
            score_pdf = sim_pdf[indice_pdf].item() * 100

            if score_pdf >= 50:
                trecho = trechos_pdf[indice_pdf][:700]
                return f"{resposta_positiva(nome)} {trecho}...", None

    return resposta_negativa(nome), None
