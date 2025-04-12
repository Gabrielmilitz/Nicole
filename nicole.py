import random
from sentence_transformers import SentenceTransformer, util
import requests
import json
import os
import fitz  # PyMuPDF
from googlesearch import search

# --- CONFIGURAÇÕES ---
ARQUIVO_PROCESSADOR = "processador.json"
DIRETORIO_PDFS = "pdfs"

# --- MODELO ---
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# --- FUNÇÕES DE INTELIGÊNCIA ---

def resposta_positiva(nome):
    opcoes = [
        f"Claro, {nome}! Aqui está o que encontrei:",
        f"Olha só, {nome}, achei isso para você:",
        f"Certo, {nome}. Veja essa informação:",
        f"Encontrei algo interessante para você, {nome}!",
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
    if os.path.exists(ARQUIVO_PROCESSADOR):
        with open(ARQUIVO_PROCESSADOR, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_processador(processador):
    with open(ARQUIVO_PROCESSADOR, 'w', encoding='utf-8') as f:
        json.dump(processador, f, indent=4, ensure_ascii=False)

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

# --- BUSCAR NO GOOGLE (com filtro correto) ---
def buscar_no_google(consulta):
    try:
        for url in search(consulta, num_results=5, lang="pt"):
            # Só aceita links que realmente são sites (e não imagens ou buscas quebradas)
            if url.startswith("http") and not any(ext in url for ext in [".jpg", ".png", ".jpeg", "imgres", "/images/", "/search?"]):
                return url
    except Exception as e:
        print(f"Erro na busca Google: {e}")
    return None

# --- INTELIGÊNCIA DE RESPOSTA PRINCIPAL ---
def responder_usuario(usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador):
    resposta = ""
    imagem = None

    embedding_usuario = modelo.encode(usuario, convert_to_tensor=True)

    # Primeiro tenta encontrar nas frases treinadas
    similaridades = util.cos_sim(embedding_usuario, embeddings_base)[0]
    melhor_indice = similaridades.argmax().item()
    melhor_pontuacao = similaridades[melhor_indice].item() * 100

    if melhor_pontuacao >= 75:
        chave = frases_base[melhor_indice]
        resposta_crua = processador[chave]["significado"]
        resposta = f"{resposta_positiva(nome)} {resposta_crua.capitalize()}"
    else:
        encontrou_no_pdf = False

        # Tenta nos PDFs
        if embeddings_pdf is not None:
            similaridades_pdf = util.cos_sim(embedding_usuario, embeddings_pdf)[0]
            melhor_indice_pdf = similaridades_pdf.argmax().item()
            melhor_pontuacao_pdf = similaridades_pdf[melhor_indice_pdf].item() * 100

            if melhor_pontuacao_pdf >= 50:
                trecho_encontrado = trechos_pdf[melhor_indice_pdf]
                resposta = f"{resposta_positiva(nome)} {trecho_encontrado[:700]}..."
                encontrou_no_pdf = True

        if not encontrou_no_pdf:
            # Se ainda não encontrou, faz busca no Google
            print("🔎 Buscando no Google...")
            resultado_google = buscar_no_google(usuario)
            if resultado_google:
                resposta = f"Não encontrei uma resposta exata ainda, {nome}, mas encontrei isso que pode te ajudar: {resultado_google}"
            else:
                resposta = resposta_negativa(nome)

    return resposta, imagem
