import json
import os
import random

PASTA_PROCESSADOR = "dados"

def carregar_processador():
    processador = {}
    if not os.path.exists(PASTA_PROCESSADOR):
        return {}

    for arquivo in os.listdir(PASTA_PROCESSADOR):
        if arquivo.endswith(".json"):
            caminho = os.path.join(PASTA_PROCESSADOR, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                processador.update(json.load(f))
    return processador

def resposta_positiva(nome):
    return random.choice([
        f"Claro, {nome}! Aqui está o que encontrei:",
        f"Olha só, {nome}, achei isso para você:",
        f"Certo, {nome}. Veja essa informação:"
    ])

def resposta_negativa(nome):
    return random.choice([
        f"Hmm... ainda não sei responder isso, {nome}.",
        f"Essa me pegou, {nome}! Mas estou sempre aprendendo!",
        f"Não achei ainda, {nome}. Me ensina?"
    ])

def responder_usuario(mensagem, nome, processador):
    mensagem = mensagem.strip().lower()

    # Etapa 1: Verificação direta por tópico (chave exata)
    if mensagem in processador:
        significado = processador[mensagem].get("significado", "")
        return f"{resposta_positiva(nome)} {significado}", None

    # Etapa 2: Verificação por palavras no campo 'correspondencia'
    for chave, dados in processador.items():
        correspondencia = dados.get("correspondencia", "").lower().split()
        if any(palavra in mensagem for palavra in correspondencia):
            significado = dados.get("significado", "")
            return f"{resposta_positiva(nome)} {significado}", None

    return resposta_negativa(nome), None
