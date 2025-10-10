// Função para que não dê erro a conversão para mostrar no Front
// "Escapa" de caracteres perigosos
function escapeHtml(s) {
  return String(s).replace(
    /[&<>"']/g,
    c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[c]
  );
}

// Função que carrega e mostra os filmes
async function load() {
  try {
    const resposta = await fetch('/api/filmes', { cache: 'no-store' });
    if (!resposta.ok) throw new Error('Status ' + resposta.status);
    const filmes = await resposta.json();
    const div = document.getElementById('lista');

    if (!filmes.length) {
      div.innerHTML = '<p>Nenhum filme cadastrado.</p>';
      return;
    }

    let html = `
      <table>
        <thead>
          <tr>
            <th>Título</th>
            <th>Atores</th>
            <th>Diretor</th>
            <th>Ano</th>
            <th>Gênero</th>
            <th>Produtora</th>
            <th>Sinopse</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
    `;

    filmes.forEach(dado => {
      html += `
        <tr>
          <td>${escapeHtml(dado.titulo)}</td>
          <td>${escapeHtml(dado.atores || '')}</td>
          <td>${escapeHtml(dado.diretor || '')}</td>
          <td>${escapeHtml(dado.ano || '')}</td>
          <td>${escapeHtml(dado.genero || '')}</td>
          <td>${escapeHtml(dado.produtora || '')}</td>
          <td>${escapeHtml(dado.sinopse || '')}</td>
          <td>
            <button onclick="window.location.href='/editar_filme?titulo=${encodeURIComponent(dado.titulo)}'">Editar</button>
            <button onclick="deletarFilme('${escapeHtml(dado.titulo)}')">Deletar</button>
          </td>
        </tr>
      `;
    });

    html += `</tbody></table>`;
    div.innerHTML = html;

  } catch (erro) {
    document.getElementById('lista').textContent = 'Erro ao carregar filmes: ' + erro.message;
  }
}

// Função para deletar filme
async function deletarFilme(titulo) {
  await fetch('/delete_filme', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `titulo=${encodeURIComponent(titulo)}`
  });
  load();
}

// A função editarFilme agora apenas redireciona para a página de edição
function editarFilme(titulo) {
  window.location.href = '/editar_filme?titulo=' + encodeURIComponent(titulo);
}

load();
