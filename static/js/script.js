const formulario = document.getElementById("formulario");
const chat = document.getElementById("chat");
const nomeInput = document.getElementById("nome");
const mensagemInput = document.getElementById("mensagem");

let nome = "";

formulario.addEventListener("submit", async function(e) {
    e.preventDefault();

    if (!nome) {
        nome = nomeInput.value.trim();
        if (nome) {
            nomeInput.style.display = "none";
            mensagemInput.focus();
            return;
        }
    }

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
            body: JSON.stringify({ nome: nome, mensagem: mensagem }),
        });

        const data = await response.json();
        clearInterval(interval);
        digitando.remove();

        adicionarMensagem("nicole", data.resposta);
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
