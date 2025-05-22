try {
    const response = await fetch("/perguntar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nome, mensagem: mensagem }),
    });

    if (!response.ok) {
        throw new Error(`Servidor respondeu com status ${response.status}`);
    }

    let data;
    try {
        data = await response.json();
    } catch (jsonError) {
        digitando.remove();
        adicionarMensagem("nicole", "Erro ao processar resposta do servidor (formato inválido). 😕");
        console.error("Erro ao converter para JSON:", jsonError);
        return;
    }

    clearInterval(interval);
    digitando.remove();

    if (data.imagem) {
        adicionarMensagem("nicole", `${data.resposta}<br><img src="${data.imagem}" alt="Imagem gerada">`);
    } else {
        adicionarMensagem("nicole", data.resposta);
    }

} catch (error) {
    clearInterval(interval);
    digitando.remove();
    adicionarMensagem("nicole", "Erro ao tentar conversar com o servidor. 😕");
    console.error("Erro:", error);
}
