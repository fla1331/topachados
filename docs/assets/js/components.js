// (docs/)
document.addEventListener('DOMContentLoaded', function() {
    console.log('(docs/) - Carregando componentes...');
    
    // Configuração padrão para docs/
    const config = window.SITE_CONFIG || {
        baseUrl: '',
        components: {
            header: 'includes/header.html',
            footer: 'includes/footer.html',
            sidebar: 'includes/sidebar.html'
        }
    };
    
    // Mapeamento ID -> URL (caminhos relativos)
    const componentsMap = {
        'header-placeholder': config.components.header,
        'footer-placeholder': config.components.footer,
        'sidebar-container': config.components.sidebar
    };
    
    // Carrega todos os componentes
    Object.entries(componentsMap).forEach(([id, url]) => {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`⚠️ Elemento #${id} não encontrado (pode ser opcional)`);
            return;
        }
        
        // URL relativa considerando baseUrl
        const fullUrl = config.baseUrl ? `${config.baseUrl}/${url}` : url;
        
        fetch(fullUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${fullUrl}`);
                }
                return response.text();
            })
            .then(html => {
                element.innerHTML = html;
                console.log(`✅ ${id} carregado de ${fullUrl}`);
                
                // Executa scripts dentro do componente
                executeScripts(element);
                
                // Inicializar componentes específicos
                if (id === 'header-placeholder') {
                    initHeader();
                }
                if (id === 'sidebar-container') {
                    initSidebar();
                }
            })
            .catch(error => {
                console.error(`❌ Erro ao carregar ${id}:`, error.message);
                
                // Fallback baseado no ID
                element.innerHTML = getFallbackHTML(id, url);
            });
    });
    
    // Função para executar scripts dentro do HTML carregado
    function executeScripts(container) {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            
            // Copiar atributos
            Array.from(oldScript.attributes).forEach(attr => {
                newScript.setAttribute(attr.name, attr.value);
            });
            
            // Copiar conteúdo
            newScript.textContent = oldScript.textContent;
            
            // Substituir script
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }
    
    // Função para inicializar o header
    function initHeader() {
        console.log('Inicializando header...');
        
        // Menu mobile toggle
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.getElementById('nav-menu');
        
        if (mobileMenuBtn && navMenu) {
            mobileMenuBtn.addEventListener('click', function() {
                navMenu.classList.toggle('active');
                mobileMenuBtn.innerHTML = navMenu.classList.contains('active') 
                    ? '<i class="fas fa-times"></i>' 
                    : '<i class="fas fa-bars"></i>';
            });
        }
        
        // Marcar link ativo baseado na URL atual
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || 
                (currentPage === '' && href === 'index.html') ||
                (currentPage === 'index.html' && href === '')) {
                link.classList.add('active');
            }
        });
    }
    
    // Função para inicializar o sidebar
    function initSidebar() {
        console.log('Inicializando sidebar...');
        
        // Toggle sidebar no mobile
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
        }
    }
    
    // HTML de fallback para cada componente
    function getFallbackHTML(id, url) {
        const fallbacks = {
            'header-placeholder': `
                <header class="site-header">
                    <div class="header-content">
                        <a href="/" class="logo">
                            <i class="fas fa-star"></i>
                            <span>TopOfertas.ReviewNexus</span>
                        </a>
                        <button id="mobile-menu-btn" class="mobile-menu-btn">
                            <i class="fas fa-bars"></i>
                        </button>
                        <nav id="nav-menu" class="nav-menu">
                            <a href="index.html" class="nav-link active">Início</a>
                            <a href="eletrodomesticos.html" class="nav-link">Eletrodomésticos</a>
                            <a href="sobre.html" class="nav-link">Sobre</a>
                            <a href="#" class="nav-link">Contato</a>
                        </nav>
                    </div>
                </header>
            `,
            'footer-placeholder': `
                <footer class="site-footer">
                    <div class="footer-content">
                        <div class="footer-section">
                            <h3>TopOfertas.ReviewNexus</h3>
                            <p>Encontre as melhores ofertas com análises detalhadas.</p>
                        </div>
                        <div class="footer-section">
                            <h4>Links Rápidos</h4>
                            <a href="index.html">Início</a>
                            <a href="eletrodomesticos.html">Eletrodomésticos</a>
                            <a href="sobre.html">Sobre</a>
                        </div>
                        <div class="footer-section">
                            <h4>Contato</h4>
                            <p>contato@topofertas.reviewnexus.com</p>
                        </div>
                    </div>
                    <div class="footer-bottom">
                        <p>&copy; ${new Date().getFullYear()} TopOfertas.ReviewNexus. Todos os direitos reservados.</p>
                        <p><small>Fallback - Arquivo original: ${url}</small></p>
                    </div>
                </footer>
            `,
            'sidebar-container': `
                <aside id="sidebar" class="sidebar">
                    <button id="sidebar-toggle" class="sidebar-toggle">
                        <i class="fas fa-times"></i>
                    </button>
                    <div class="sidebar-content">
                        <h3>Categorias</h3>
                        <ul class="sidebar-menu">
                            <li><a href="eletrodomesticos.html"><i class="fas fa-blender"></i> Eletrodomésticos</a></li>
                            <li><a href="#"><i class="fas fa-laptop"></i> Tecnologia</a></li>
                            <li><a href="#"><i class="fas fa-couch"></i> Móveis</a></li>
                            <li><a href="#"><i class="fas fa-tshirt"></i> Moda</a></li>
                        </ul>
                        <div class="sidebar-footer">
                            <p>Encontre as melhores ofertas!</p>
                        </div>
                    </div>
                </aside>
            `
        };
        
        return fallbacks[id] || `<div class="component-error">Erro ao carregar componente: ${id}</div>`;
    }
});