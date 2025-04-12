from encoding import *  # importa encoding e define
import json
import os

ARQUIVO_PROCESSADOR = "processador.json"

# Função para carregar o processador existente
def carregar_processador():
    if os.path.exists(ARQUIVO_PROCESSADOR):
        with open(ARQUIVO_PROCESSADOR, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

# Função para salvar o processador atualizado
def salvar_processador(processador):
    with open(ARQUIVO_PROCESSADOR, "w", encoding="utf-8") as f:
        json.dump(processador, f, indent=4, ensure_ascii=False)

# Função para codificar uma frase ou palavra
def codificar_frase(frase):
    codificado = []
    total = 0
    for letra in frase.lower():
        if letra in define:
            valor = round(define[letra], 4)
            codificado.append(valor)
            total += valor
        else:
            codificado.append(0)
    return codificado, total

# Programa principal
def treinar():
    print("\n🌟 Bem-vindo ao Treinador da Nicole 🌟")
    processador = carregar_processador()

    while True:
        nova_frase = input("\nDigite a palavra ou frase que deseja treinar (ou 'sair' para encerrar): ").strip()
        if nova_frase.lower() == "sair":
            print("\n👋 Encerrando treinamento. Até logo!")
            break

        significado = input("Digite o significado ou descrição dessa frase: ").strip()

        codificacao, total = codificar_frase(nova_frase)

        # Formato compatível para a Nicole
        processador[nova_frase.lower()] = {
            "codificacao": " ".join(map(str, codificacao)),
            "total": round(total, 4),
            "significado": significado
        }

        salvar_processador(processador)
        print(f"\n✅ Frase '{nova_frase}' treinada e salva com sucesso!")

if __name__ == "__main__":
    treinar()
