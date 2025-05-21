import random
import os
import json
import fitz
import gc
from googlesearch import search
from sentence_transformers import SentenceTransformer, util
import torch

PASTA_PROCESSADOR = "dados"
DIRETORIO_PDFS = "pdfs"

# Função leve para carregar o modelo somente quando necessário
def get_modelo():
    return SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Mais leve e compatível com Render

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

    for arquivo in os.listdir(PASTA_PROCESSADOR):
        if arquivo.endswith(".json"):
            with open(os.path.join(PASTA_PROCESSADOR, arquivo), "r", encoding="utf-8") as f:
                processador.update(json.load(f))
    return processador

def salvar_processador_por_tema(processador):
    os.makedirs(PASTA_PROCESSADOR, exist_ok=True)
    temas = {}
    for frase, dados in processador.items():
        tema = dados.get("tema", "geral")
        if tema not in temas:
            temas[tema] = {}
        temas[tema][frase] = dados

    for tema, conteudo in temas.items():
        caminho = os.path.join(PASTA_PROCESSADOR, f"{tema}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(conteudo, f, indent=4, ensure_ascii=False)

def preparar_base(processador):
    frases = list(processador.keys())
    modelo = get_modelo()
    with torch.no_grad():
        embeddings = modelo.encode(frases, convert_to_tensor=True)
    del modelo
    gc.collect()
    return frases, embeddings

def carregar_trechos_pdfs(diretorio):
    trechos = []
    if not os.path.exists(diretorio):
        return trechos

    arquivos = [f for f in os.listdir(diretorio) if f.endswith(".pdf")]
    if not arquivos:
        return trechos

    for arquivo in arquivos:
        caminho = os.path.join(diretorio, arquivo)
        pdf = fitz.open(caminho)
        for pagina in pdf:
            texto = pagina.get_text()
            paragrafos = texto.split('\n\n')
            for p in paragrafos:
                p = p.strip()
                if p.count('\n') >= 10:
                    trechos.append(p.replace('\n', ' '))
        pdf.close()
    return trechos

def buscar_no_google(consulta):
    try:
        for url in search(consulta, num_results=5, lang="pt"):
            if url.startswith("http") and not any(ext in url for ext in [".jpg", ".png", ".jpeg", "imgres", "/images/", "/search?"]):
                return url
    except Exception as e:
        print(f"Erro na busca Google: {e}")
    return None

def responder_usuario(usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador):
    modelo = get_modelo()
    resposta = ""

    try:
        with torch.no_grad():
            embedding_usuario = modelo.encode(usuario, convert_to_tensor=True)
            similaridades = util.cos_sim(embedding_usuario, embeddings_base)[0]
            melhor_indice = similaridades.argmax().item()
            melhor_pontuacao = similaridades[melhor_indice].item() * 100

            if melhor_pontuacao >= 75:
                chave = frases_base[melhor_indice]
                resposta_crua = processador[chave]["significado"]
                resposta = f"{resposta_positiva(nome)} {resposta_crua.capitalize()}"
            else:
                encontrou_no_pdf = False
                if embeddings_pdf:
                    similaridades_pdf = util.cos_sim(embedding_usuario, embeddings_pdf)[0]
                    melhor_indice_pdf = similaridades_pdf.argmax().item()
                    melhor_pontuacao_pdf = similaridades_pdf[melhor_indice_pdf].item() * 100

                    if melhor_pontuacao_pdf >= 50:
                        trecho = trechos_pdf[melhor_indice_pdf]
                        resposta = f"{resposta_positiva(nome)} {trecho[:700]}..."
                        encontrou_no_pdf = True

                if not resposta:
                    print("🔎 Buscando no Google...")
                    resultado_google = buscar_no_google(usuario)
                    if resultado_google:
                        resposta = f"Não encontrei uma resposta exata ainda, {nome}, mas talvez isso te ajude: {resultado_google}"
                    else:
                        resposta = resposta_negativa(nome)

    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        resposta = "Houve um erro ao tentar responder. Tente novamente."

    del modelo
    gc.collect()
    return resposta, None
