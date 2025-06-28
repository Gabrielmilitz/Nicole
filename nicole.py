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

def resposta_positiva():
    return random.choice([
        "Claro! Aqui está o que encontrei:",
        "Veja só o que achei para você:",
        "Certo. Veja essa informação:"
    ])

def resposta_negativa():
    return random.choice([
        "Hmm... ainda não sei responder isso.",
        "Essa me pegou! Mas estou sempre aprendendo!",
        "Não achei ainda. Quer me ensinar?"
    ])

def responder_usuario(mensagem, processador):
    mensagem = mensagem.strip().lower()

    if mensagem in processador:
        significado = processador[mensagem].get("significado", "")
        return f"{resposta_positiva()} {significado}", None

    for chave, dados in processador.items():
        correspondencia = dados.get("correspondencia", "").lower().split()
        if any(palavra in mensagem for palavra in correspondencia):
            significado = dados.get("significado", "")
            return f"{resposta_positiva()} {significado}", None

    return resposta_negativa(), None
