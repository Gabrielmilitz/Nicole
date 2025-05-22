const formulario = document.getElementById("formulario");
const chat = document.getElementById("chat");
const nomeInput = document.getElementById("nome");
const mensagemInput = document.getElementById("mensagem");

let nome = "";

formulario.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Primeiro envio: captura nome
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

    const digitando = adicionarMensagem("nicole", "<em>Nicole está digitando</em>");
    let pontos = 0;
    const interval = setInterval(() => {
        pontos = (pontos + 1) % 4;
        digitando.innerHTML = `<em>Nicole está digitando${".".repeat(pontos)}</em>`;
    }, 400);

    try {
        const response = await fetch("/perguntar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, mensagem }),
        });

        clearInterval(interval);
        digitando.remove();

        if (!response.ok) {
            adicionarMensagem("nicole", "O servidor não respondeu corretamente. Código: " + response.status);
            return;
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            adicionarMensagem("nicole", "Resposta inesperada do servidor.");
            return;
        }

        const data = await response.json();

        if (data.imagem) {
            adicionarMensagem("nicole", `${data.resposta}<br><img src="${data.imagem}" alt="Imagem" style="max-width:100%; margin-top:10px;">`);
        } else {
            adicionarMensagem("nicole", data.resposta);
        }
    } catch (erro) {
        clearInterval(interval);
        digitando.remove();
        adicionarMensagem("nicole", "Erro ao conectar com o servidor.");
        console.error("[ERRO FRONTEND]", erro);
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
