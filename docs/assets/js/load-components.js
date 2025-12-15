// VERSÃO SIMPLIFICADA E CONFIÁVEL
document.addEventListener('DOMContentLoaded', function() {
  // Lista de componentes para carregar
  const componentes = [
    { id: 'header-container', arquivo: 'includes/header.html' },
    { id: 'footer-placeholder', arquivo: 'includes/footer.html' }
  ];
  
  // Carrega cada componente
  componentes.forEach(function(componente) {
    if (document.getElementById(componente.id)) {
      fetch(componente.arquivo)
        .then(resposta => {
          if (!resposta.ok) {
            throw new Error(`Arquivo não encontrado: ${componente.arquivo}`);
          }
          return resposta.text();
        })
        .then(html => {
          document.getElementById(componente.id).innerHTML = html;
          console.log(`✅ ${componente.id} carregado`);
        })
        .catch(erro => {
          console.error(`❌ Erro no ${componente.id}:`, erro);
          // Fallback: mostra uma mensagem se não carregar
          document.getElementById(componente.id).innerHTML = 
            `<div style="padding: 20px; background: #ffebee; color: #c62828;">
               Erro ao carregar ${componente.id}. Verifique se o arquivo ${componente.arquivo} existe.
             </div>`;
        });
    }
  });
});