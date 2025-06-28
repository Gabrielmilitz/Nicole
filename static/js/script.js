const formulario = document.getElementById("formulario");
const chat = document.getElementById("chat");
const mensagemInput = document.getElementById("mensagem");

formulario.addEventListener("submit", async function (e) {
    e.preventDefault();

    const mensagem = mensagemInput.value.trim();
    if (!mensagem) return;

    adicionarMensagem("usuario", mensagem);
    mensagemInput.value = "";

    const digitando = adicionarMensagem("nicole", "<em>Nicole está digitando...</em>");

    let pontos = 0;
    const interval = setInterval(() => {
        pontos = (pontos + 1) % 4;
        digitando.innerHTML = `<em>Nicole está digitando${".".repeat(pontos)}</em>`;
    }, 400);

    try {
        const response = await fetch("/perguntar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem }),
        });

        const data = await response.json();
        clearInterval(interval);
        digitando.remove();

        const respostaDiv = adicionarMensagem("nicole", "");
        simularDigitacao(data.resposta, respostaDiv);
    } catch (error) {
        clearInterval(interval);
        digitando.remove();
        adicionarMensagem("nicole", "Erro ao tentar conversar com o servidor. 😕");
    }
});

function adicionarMensagem(tipo, conteudo) {
    const div = document.createElement("div");
    div.className = `mensagem ${tipo}`;
    div.innerHTML = conteudo;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

function simularDigitacao(texto, container, callback) {
    let i = 0;
    const intervalo = setInterval(() => {
        container.innerHTML += texto.charAt(i);
        chat.scrollTop = chat.scrollHeight;
        i++;
        if (i >= texto.length) {
            clearInterval(intervalo);
            if (callback) callback();
        }
    }, 25);
}
