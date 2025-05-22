import os
import json
import random

PASTA_DADOS = "dados"

def carregar_base():
    base = {}
    if os.path.exists(PASTA_DADOS):
        for arquivo in os.listdir(PASTA_DADOS):
            if arquivo.endswith(".json"):
                caminho = os.path.join(PASTA_DADOS, arquivo)
                with open(caminho, "r", encoding="utf-8") as f:
                    base.update(json.load(f))
    return base

def resposta_positiva(nome):
    return random.choice([
        f"Certo, {nome}! Veja o que encontrei:",
        f"Olha só, {nome}, isso pode te ajudar:",
        f"Aqui está, {nome}:",
    ])

def resposta_negativa(nome):
    return random.choice([
        f"Poxa, {nome}, não encontrei nada sobre isso. 😕",
        f"Essa eu não sei ainda, {nome}. Me ensina? 🤔",
    ])

def responder_usuario(mensagem, nome, base):
    mensagem = mensagem.lower()

    for frase, dados in base.items():
        tema = dados.get("tema", "").lower()
        if tema in mensagem:
            return f"{resposta_positiva(nome)} {dados['significado']}", None

    return resposta_negativa(nome), None
