import time 

# f(x) = a.x + b    

armazenado = 3  
resultado = 1   
taxa_aprendizado = 0.001  
soma = 0  

while True: 
    erro = armazenado - resultado  

    if armazenado > resultado:
        novo_peso = armazenado - (taxa_aprendizado * erro)
        armazenado = novo_peso  
        time.sleep(2)
        taxa_aprendizado += 0.010  
        soma += taxa_aprendizado 
        print(f"Novo peso: {novo_peso:.4f}, Taxa de aprendizado: {taxa_aprendizado:.4f}, Soma total do aprendizado: {soma:.4f}")
    
   
    elif abs(armazenado - resultado) <= 0.01:
        print("A inteligência aprendeu com o tempo")
        break






   
