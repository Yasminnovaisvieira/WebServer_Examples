// Função para que não dê erro a conversão para mostrar no Front
// "Escapa" de caracteres perigosos
function escapeHtml(s) {
  // Converte o valor para string
  return String(s).replace(
    /[&<>"']/g, // Procura por &, <, >, " e '
    c => ({// Substitui por "coisas" do HTML
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
    // Faz uma requisição GET para o arquivo filmes.json
    const resposta = await fetch('/api/filmes', { cache: 'no-store' });

    // Mostra erro se estiver algo incorreto
    if (!resposta.ok) throw new Error('Status ' + resposta.status);

    // Converte o conteúdo da resposta para JSON
    const filmes = await resposta.json();

    // Pega a div onde vamos renderizar os filmes
    const div = document.getElementById('lista');

    // Se não tiver nenhum filme cadastrado
    if (!filmes.length) {
      div.innerHTML = '<p>Nenhum filme cadastrado.</p>';
      return;
    }

    // Formato que os dados serão colocados
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
          </tr>
        </thead>
        <tbody>
    `;

    // Percorre cada filme e cria uma linha na tabela
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
        </tr>
      `;
    });

    // Fecha o corpo e a tabela
    html += `
        </tbody>
      </table>
    `;

    // Insere a tabela pronta na página
    div.innerHTML = html;

  } catch (erro) {
    // Se der erro em qualquer parte, mostra a mensagem de erro
    document.getElementById('lista').textContent = 'Erro ao carregar filmes: ' + erro.message;
  }
}

load();