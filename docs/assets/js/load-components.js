// Sistema de carregamento de componentes
class ComponentLoader {
  constructor() {
    this.components = {};
  }
  
  // Carrega um componente
  async load(componentId, filePath) {
    try {
      const response = await fetch(filePath);
      if (!response.ok) throw new Error(`Arquivo não encontrado: ${filePath}`);
      
      const html = await response.text();
      const element = document.getElementById(componentId);
      
      if (element) {
        element.innerHTML = html;
        this.components[componentId] = true;
        console.log(`✅ Componente carregado: ${componentId}`);
        
        // Executa scripts dentro do componente
        this.executeScripts(element);
      } else {
        console.warn(`⚠️ Elemento #${componentId} não encontrado`);
      }
    } catch (error) {
      console.error(`❌ Erro ao carregar ${componentId}:`, error);
    }
  }
  
  // Executa scripts dentro do componente carregado
  executeScripts(container) {
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
  
  // Carrega múltiplos componentes
  async loadMultiple(components) {
    const promises = Object.entries(components).map(([id, path]) => 
      this.load(id, path)
    );
    await Promise.all(promises);
  }
}

// Uso fácil na página:
document.addEventListener('DOMContentLoaded', async () => {
  const loader = new ComponentLoader();
  
  // Define quais componentes carregar
  const pageComponents = {
    'header-container': '/includes/header.html',
    'sidebar-container': '/includes/sidebar.html',
    'footer-container': '/includes/footer.html'
  };
  
  // Carrega todos os componentes
  await loader.loadMultiple(pageComponents);
  
  // Ativa menu mobile (exemplo)
  const menuBtn = document.querySelector('.mobile-menu-btn');
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      document.querySelector('.main-nav').classList.toggle('active');
    });
  }
});