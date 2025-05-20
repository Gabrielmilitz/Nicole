import random
from sentence_transformers import SentenceTransformer, util
import requests
import json
import os
import fitz
from googlesearch import search


PASTA_PROCESSADOR = "dados"
DIRETORIO_PDFS = "pdfs"


modelo = SentenceTransformer('all-MiniLM-L6-v2')



def resposta_positiva(nome):
    opcoes = [
        f"Claro, {nome}! Aqui está o que encontrei:",
        f"Olha só, {nome}, achei isso para você:",
        f"Certo, {nome}. Veja essa informação:",
        
    ]
    return random.choice(opcoes)

def resposta_negativa(nome):
    opcoes = [
        f"Hmm... ainda não sei responder isso, {nome} 😕.",
        f"Essa me pegou, {nome}! Mas estou sempre aprendendo! 🚀",
        f"Não achei ainda, {nome}. Me ensina? 🙏",
    ]
    return random.choice(opcoes)



def carregar_processador():
    processador = {}

    if not os.path.exists(PASTA_PROCESSADOR):
        return {}

    for arquivo in os.listdir(PASTA_PROCESSADOR):
        if arquivo.endswith(".json"):
            caminho = os.path.join(PASTA_PROCESSADOR, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
                processador.update(conteudo)
    
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
    embeddings = modelo.encode(frases, convert_to_tensor=True)
    return frases, embeddings


def carregar_trechos_pdfs(diretorio):
    trechos = []
    if not os.path.exists(diretorio):
        return trechos

    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".pdf"):
            caminho = os.path.join(diretorio, arquivo)
            pdf = fitz.open(caminho)
            for pagina in pdf:
                texto = pagina.get_text()
                paragrafo_list = texto.split('\n\n')
                for paragrafo in paragrafo_list:
                    paragrafo = paragrafo.strip()
                    if paragrafo.count('\n') >= 10:
                        texto_limpo = paragrafo.replace('\n', ' ')
                        trechos.append(texto_limpo)
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
    resposta = ""
    imagem = None

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

        if embeddings_pdf is not None:
            similaridades_pdf = util.cos_sim(embedding_usuario, embeddings_pdf)[0]
            melhor_indice_pdf = similaridades_pdf.argmax().item()
            melhor_pontuacao_pdf = similaridades_pdf[melhor_indice_pdf].item() * 100

            if melhor_pontuacao_pdf >= 50:
                trecho_encontrado = trechos_pdf[melhor_indice_pdf]
                resposta = f"{resposta_positiva(nome)} {trecho_encontrado[:700]}..."
                encontrou_no_pdf = True

        if not encontrou_no_pdf:
            print("🔎 Buscando no Google...")
            resultado_google = buscar_no_google(usuario)
            if resultado_google:
                resposta = f"Não encontrei uma resposta exata ainda, {nome}, mas encontrei isso que pode te ajudar: {resultado_google}"
            else:
                resposta = resposta_negativa(nome)

    return resposta, imagem
