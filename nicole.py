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
        f"Claro, {nome}:",
        f"Olha só, {nome}:",
        f"Certo, {nome}:"
    ])

def resposta_negativa(nome):
    return random.choice([
        f"Hmm... ainda não sei responder isso, {nome}.",
        f"Essa me pegou, {nome}! Mas estou sempre aprendendo!",
        f"Não achei ainda, {nome}. Me ensina?"
    ])

def responder_usuario(mensagem, nome, processador):
    mensagem = mensagem.lower()

    for chave, dados in processador.items():
        if not isinstance(dados, dict):
            continue

        correspondencias = dados.get("correspondencia", "").lower().split()
        if any(palavra in mensagem for palavra in correspondencias):
            return f"{resposta_positiva(nome)} {dados['significado']}", None

    return resposta_negativa(nome), None
