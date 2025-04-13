import random
from sentence_transformers import SentenceTransformer, util #biblioteca transforma sentença em vetores 
import requests
import json
import os
import fitz  # PyMuPDF
from googlesearch import search

# processador json
#aqui um ponto pq estamos trabalahndo com diretorio pdfs e com arquivo json, pode ser um ponto de melhoria
ARQUIVO_PROCESSADOR = "processador.json"
DIRETORIO_PDFS = "pdfs"

# --- MODELO ---
modelo = SentenceTransformer('all-MiniLM-L6-v2')

#respostas padrão com random 

def resposta_positiva(nome):
    opcoes = [
        f"Claro, {nome}! Aqui está o que encontrei:",
        f"Olha só, {nome}, achei isso para você:",
        f"Certo, {nome}. Veja essa informação:",
        f"Encontrei algo interessante para você, {nome}!",
    ]
    return random.choice(opcoes)
#respostas padrão com random
def resposta_negativa(nome):
    opcoes = [
        f"Hmm... ainda não sei responder isso, {nome} 😕.",
        f"Essa me pegou, {nome}! Mas estou sempre aprendendo! 🚀",
        f"Não achei ainda, {nome}. Me ensina? 🙏",
    ]
    return random.choice(opcoes)

def carregar_processador(): #aqui o processador ta sendo carregado em modelo leitura
    if os.path.exists(ARQUIVO_PROCESSADOR):
        with open(ARQUIVO_PROCESSADOR, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_processador(processador): #aqui em modo escrita
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
 #se o arquivo tive no diretorio 
    # e tive o final .pdf para iso precisados da bibliotece fitz  
    # caminho = os. pra isso importamos import os (diretorio, arquivo) 
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".pdf"):
            caminho = os.path.join(diretorio, arquivo)
            pdf = fitz.open(caminho)
            for pagina in pdf: #se a pagina esta no pdf
                texto = pagina.get_text()  #pegamos o texto que ta nela
                paragrafo_list = texto.split('\n\n') #damos um split 
                for paragrafo in paragrafo_list:   #para o paragrafo no texto com split
                    paragrafo = paragrafo.strip()  
                    if paragrafo.count('\n') >= 10:  # faz uma contagem pra ver se o paragrafo é maior que 10 ou mais quebras de linha
                        #isso é importante pq se for menor pode retornar uma mensagem quebrada
                        texto_limpo = paragrafo.replace('\n', ' ')
                        trechos.append(texto_limpo) #trecho é nossa lista vazia la em cima 
            pdf.close()
    return trechos  #retorna a lista 

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

# --- ATENÇÃO AQUI POIS É A LOGICA DE RESPOSTA DA IA ----------------------------
def responder_usuario(usuario, nome, frases_base, embeddings_base, trechos_pdf, embeddings_pdf, processador):
    resposta = ""
    imagem = None

    embedding_usuario = modelo.encode(usuario, convert_to_tensor=True)

    # Primeiro tenta encontrar nas frases treinadas
      '''
      embedding_usuario = aqui é o que o usuario digita e é converitdo em vetor
      embedding_base = aqui é o que já ta salvo
      util.cos_sim  = calcula a simularidade do cos entre a e b #é um calculo que diz o quanto dois vetores são parecidos 
      O [0] no final pega o vetor de resultados, porque o retorno da função é uma matriz.

      '''
    similaridades = util.cos_sim(embedding_usuario, embeddings_base)[0]
    melhor_indice = similaridades.argmax().item()
                                   #argmax() acha o indice onde a similaridade foi maior 
                                    #item() transforam em numero em python normal, lembra que numero não é um vetor
    melhor_pontuacao = similaridades[melhor_indice].item() * 100
        #se houve similaridade no indice maior que 75%
    if melhor_pontuacao >= 75:
         #vai pega a frase do processador mais vai pega só o sifnicafo
        chave = frases_base[melhor_indice]
        resposta_crua = processador[chave]["significado"]
           #resposta positiva é a função do random
        resposta = f"{resposta_positiva(nome)} {resposta_crua.capitalize()}"  
    else:
        encontrou_no_pdf = False #se <  75

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
