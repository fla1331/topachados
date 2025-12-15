// SISTEMA DE CARREGAMENTO DE COMPONENTES - VERSÃO CORRIGIDA
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 Iniciando carregamento de componentes...');
  
  // Configurações (pode ser sobrescrito por config.js)
  const config = window.SITE_CONFIG || {
    components: {
      header: '/includes/header.html',
      footer: '/includes/footer.html',
      sidebar: '/includes/sidebar.html'
    }
  };
  
  // Lista de componentes para carregar
  const componentsToLoad = [
    { 
      id: 'header-container', 
      url: config.components.header,
      fallback: `<header style="background:#f8f9fa;padding:15px;text-align:center;">
                  <a href="/" style="color:#333;font-weight:bold;">TopOfertas.ReviewNexus</a>
                </header>`
    },
    { 
      id: 'footer-placeholder', 
      url: config.components.footer,
      fallback: `<footer style="background:#333;color:white;padding:20px;text-align:center;">
                  &copy; 2025 TopOfertas.ReviewNexus
                </footer>`
    }
  ];
  
  // Função para carregar um componente
  function loadComponent(component) {
    const element = document.getElementById(component.id);
    
    if (!element) {
      console.warn(`⚠️ Elemento #${component.id} não encontrado na página`);
      return;
    }
    
    // Tenta carregar via fetch
    fetch(component.url)
      .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.text();
      })
      .then(html => {
        element.innerHTML = html;
        console.log(`✅ ${component.id} carregado de: ${component.url}`);
        
        // Executa scripts dentro do componente (se houver)
        executeScripts(element);
      })
      .catch(error => {
        console.error(`❌ Falha ao carregar ${component.id}:`, error.message);
        console.log(`🔍 Tentando caminho alternativo...`);
        
        // Tenta caminho relativo alternativo
        const altUrl = component.url.startsWith('/') 
          ? '.' + component.url 
          : component.url;
        
        fetch(altUrl)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status} no alt`);
            return response.text();
          })
          .then(html => {
            element.innerHTML = html;
            console.log(`✅ ${component.id} carregado de caminho alternativo`);
            executeScripts(element);
          })
          .catch(altError => {
            console.error(`❌ Falha total em ${component.id}`);
            // Usa fallback
            element.innerHTML = component.fallback;
          });
      });
  }
  
  // Executa scripts dentro do componente carregado
  function executeScripts(container) {
    const scripts = container.querySelectorAll('script');
    scripts.forEach(oldScript => {
      const newScript = document.createElement('script');
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });
      newScript.textContent = oldScript.textContent;
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }
  
  // Carrega todos os componentes
  componentsToLoad.forEach(loadComponent);
  
  console.log('🎯 Todos os componentes foram processados');
});