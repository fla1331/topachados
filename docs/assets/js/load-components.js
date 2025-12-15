// VERSÃO PARA GITHUB PAGES (docs/)
document.addEventListener('DOMContentLoaded', function() {
  console.log('📁 GitHub Pages Mode (docs/)');
  
  // Configuração padrão para docs/
  const config = window.SITE_CONFIG || {
    components: {
      header: 'includes/header.html',
      footer: 'includes/footer.html',
      sidebar: 'includes/sidebar.html'
    }
  };
  
  // Mapeamento ID -> URL
  const componentsMap = {
    'header-container': config.components.header,
    'footer-placeholder': config.components.footer
  };
  
  // Carrega todos os componentes
  Object.entries(componentsMap).forEach(([id, url]) => {
    const element = document.getElementById(id);
    if (!element) {
      console.warn(`Elemento #${id} não encontrado`);
      return;
    }
    
    fetch(url)
      .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
        return response.text();
      })
      .then(html => {
        element.innerHTML = html;
        console.log(`✅ ${id} carregado`);
        
        // Executa scripts dentro do componente
        const scripts = element.querySelectorAll('script');
        scripts.forEach(oldScript => {
          const newScript = document.createElement('script');
          Array.from(oldScript.attributes).forEach(attr => {
            newScript.setAttribute(attr.name, attr.value);
          });
          newScript.textContent = oldScript.textContent;
          oldScript.parentNode.replaceChild(newScript, oldScript);
        });
      })
      .catch(error => {
        console.error(`❌ Erro em ${id}:`, error.message);
        
        // Fallback baseado no ID
        if (id === 'header-container') {
          element.innerHTML = `
            <header style="background:#2c3e50;padding:15px;color:white;">
              <a href="/" style="color:white;text-decoration:none;font-weight:bold;">
                TopOfertas.ReviewNexus (Fallback)
              </a>
              <nav style="display:inline-block;margin-left:20px;">
                <a href="/" style="color:#ecf0f1;margin:0 10px;">Início</a>
                <a href="/eletrodomesticos/" style="color:#ecf0f1;margin:0 10px;">Eletro</a>
                <a href="/sobre/" style="color:#ecf0f1;margin:0 10px;">Sobre</a>
              </nav>
            </header>
          `;
        } else if (id === 'footer-placeholder') {
          element.innerHTML = `
            <footer style="background:#34495e;color:#bdc3c7;padding:20px;text-align:center;margin-top:30px;">
              <p>© 2025 TopOfertas.ReviewNexus</p>
              <p><small>Erro ao carregar footer. Arquivo: ${url}</small></p>
            </footer>
          `;
        }
      });
  });
});