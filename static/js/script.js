const formulario = document.getElementById("formulario");
const chat = document.getElementById("chat");
const nomeInput = document.getElementById("nome");
const mensagemInput = document.getElementById("mensagem");

let nome = "";

formulario.addEventListener("submit", async function (e) {
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

        clearInterval(interval);
        digitando.remove();

        if (!response.ok) {
            adicionarMensagem("nicole", "Erro no servidor. Tente novamente mais tarde. 😕");
            console.error("Erro HTTP:", response.status);
            return;
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            adicionarMensagem("nicole", "Resposta inválida do servidor. 😕");
            console.error("Tipo de resposta inesperado:", contentType);
            return;
        }

        const data = await response.json();

        if (data.imagem) {
            adicionarMensagem("nicole", `${data.resposta}<br><img src="${data.imagem}" alt="Imagem gerada" style="max-width:100%; margin-top:10px;">`);
        } else {
            adicionarMensagem("nicole", data.resposta);
        }

    } catch (error) {
        clearInterval(interval);
        digitando.remove();
        adicionarMensagem("nicole", "Erro de conexão. Tente novamente. 😕");
        console.error("Erro:", error);
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
