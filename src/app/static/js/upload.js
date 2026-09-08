/* Adicionar fotos uma a uma (acumulando) antes de enviar o formulário.
   Cada clique em "Adicionar foto" cria um novo campo <input type="file" name="fotos">,
   e o usuário pode selecionar várias (segurando Ctrl/Cmd) em cada um. Todos são
   enviados juntos no submit, e o servidor lê com request.files.getlist('fotos'). */
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('linhas-fotos');
    const botaoAdicionar = document.getElementById('btn-adicionar-foto');
    if (!container || !botaoAdicionar) return;

    function criarLinha() {
        const linha = document.createElement('div');
        linha.className = 'linha-foto';

        const input = document.createElement('input');
        input.type = 'file';
        input.name = 'fotos';
        input.accept = 'image/png, image/jpeg, image/webp';
        input.multiple = true;

        const preview = document.createElement('div');
        preview.className = 'preview-fotos';

        const remover = document.createElement('button');
        remover.type = 'button';
        remover.className = 'btn-remover-linha';
        remover.title = 'Remover este campo de foto';
        remover.textContent = '×';
        remover.addEventListener('click', () => linha.remove());

        input.addEventListener('change', () => {
            preview.innerHTML = '';
            [...input.files].forEach(arquivo => {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(arquivo);
                preview.appendChild(img);
            });
        });

        linha.append(input, preview, remover);
        container.appendChild(linha);
    }

    botaoAdicionar.addEventListener('click', criarLinha);
    criarLinha(); // começa com um campo visível
});
