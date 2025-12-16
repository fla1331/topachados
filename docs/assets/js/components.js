// COMPONENTES DINÂMICOS - Carrega header, footer e sidebar
document.addEventListener('DOMContentLoaded', function() {
    
    // Configuração interna
    const config = window.SITE_CONFIG || {
        components: {
            header: 'includes/header.html',
            footer: 'includes/footer.html',
            sidebar: 'includes/sidebar.html'
        }
    };
    
    // Mapeamento de componentes
    const componentsMap = {
        'header-container': config.components.header,
        'footer-placeholder': config.components.footer,
        'sidebar-container': config.components.sidebar
    };
    
    // Carregar todos os componentes
    Object.entries(componentsMap).forEach(([id, url]) => {
        const element = document.getElementById(id);
        if (!element) {
            if (id !== 'sidebar-container') {
                console.warn(`Elemento #${id} não encontrado`);
            }
            return;
        }
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                element.innerHTML = html;
                
                // Executar scripts dentro do componente
                executeScripts(element);
                
                // Inicializar componentes específicos
                if (id === 'header-container') initHeader();
                if (id === 'sidebar-container') initSidebar();
            })
            .catch(error => {
                element.innerHTML = getFallbackHTML(id);
            });
    });
    
    // Função para executar scripts
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
    
    // Inicializar header
    function initHeader() {
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
        
        // Busca toggle
        document.querySelectorAll('.search-toggle').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelector('.search-bar').classList.toggle('active');
            });
        });
        
        // Marcar link ativo
        markActiveNavLink();
    }
    
    // Marcar link de navegação ativo
    function markActiveNavLink() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || 
                (currentPage === '' && href === 'index.html') ||
                (currentPage === 'index.html' && href === '') ||
                (href.includes(currentPage.replace('.html', '')) && currentPage !== 'index.html')) {
                link.classList.add('active');
            }
        });
    }
    
    // Inicializar sidebar
    function initSidebar() {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
        }
        
        // Filtros da sidebar
        document.querySelector('.btn-apply-filters')?.addEventListener('click', function() {
            const price = document.querySelector('.price-slider')?.value || '0';
            alert(`Filtros aplicados! Preço máximo: R$ ${price}`);
        });
        
        document.querySelector('.btn-clear-filters')?.addEventListener('click', function() {
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            document.querySelector('.price-slider').value = 2500;
        });
    }
    
    // HTML de fallback
    function getFallbackHTML(id) {
        const currentYear = new Date().getFullYear();
        
        switch(id) {
            case 'header-container':
                return `
                    <header class="site-header">
                        <div class="header-content">
                            <a href="index.html" class="logo">
                                <i class="fas fa-star"></i>
                                <span>TopOfertas</span>
                            </a>
                            <button id="mobile-menu-btn" class="mobile-menu-btn">
                                <i class="fas fa-bars"></i>
                            </button>
                            <nav id="nav-menu" class="nav-menu">
                                <a href="index.html" class="nav-link active">Início</a>
                                <a href="eletrodomesticos.html" class="nav-link">Eletrodomésticos</a>
                                <a href="#" class="nav-link">Tecnologia</a>
                                <a href="sobre.html" class="nav-link">Sobre</a>
                            </nav>
                        </div>
                    </header>
                `;
                
            case 'footer-placeholder':
                return `
                    <footer class="site-footer">
                        <div class="footer-content">
                            <div class="footer-section">
                                <h3>TopOfertas</h3>
                                <p>Encontre as melhores ofertas online.</p>
                            </div>
                            <div class="footer-section">
                                <h4>Links</h4>
                                <a href="index.html">Início</a>
                                <a href="eletrodomesticos.html">Eletrodomésticos</a>
                                <a href="sobre.html">Sobre</a>
                            </div>
                        </div>
                        <div class="footer-bottom">
                            <p>&copy; ${currentYear} TopOfertas</p>
                        </div>
                    </footer>
                `;
                
            case 'sidebar-container':
                return `
                    <aside id="sidebar" class="sidebar">
                        <button id="sidebar-toggle" class="sidebar-toggle">
                            <i class="fas fa-times"></i>
                        </button>
                        <div class="sidebar-content">
                            <h3>Categorias</h3>
                            <ul class="sidebar-menu">
                                <li><a href="eletrodomesticos.html"><i class="fas fa-blender"></i> Eletrodomésticos</a></li>
                                <li><a href="#"><i class="fas fa-laptop"></i> Tecnologia</a></li>
                            </ul>
                        </div>
                    </aside>
                `;
                
            default:
                return `<div>Componente ${id} indisponível</div>`;
        }
    }
});