/**
 * COMPONENTES DINÂMICOS UNIVERSAL
 * Funciona em: GitHub Pages, WordPress, HTML estático, Localhost, Netlify, etc.
 * Não precisa de configuração - detecta automaticamente
 */
(function() {
    'use strict';
    
    // Aguarda o DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initComponents);
    } else {
        initComponents();
    }
    
    function initComponents() {
        console.log('🔄 Componentes Dinâmicos v2.0');
        
        // Lista de componentes para carregar (pode estender)
        const components = [
            { id: 'header-placeholder', file: 'includes/header.html' },
            { id: 'footer-placeholder', file: 'includes/footer.html' },
            { id: 'sidebar-container', file: 'includes/sidebar.html', optional: true },
            { id: 'sidebar-placeholder', file: 'includes/sidebar.html', optional: true }
        ];
        
        // Para cada componente
        components.forEach(component => {
            const element = document.getElementById(component.id);
            if (!element) {
                if (!component.optional) {
                    console.log(`⚠️ ${component.id} não encontrado no DOM`);
                }
                return;
            }
            
            // Tenta carregar o componente
            loadComponent(element, component.file)
                .then(success => {
                    if (success && component.id === 'header-placeholder') {
                        initHeader(); // Inicializa menu mobile
                    }
                })
                .catch(err => {
                    // Silencioso - não mostra erro
                });
        });
    }
    
    /**
     * FUNÇÃO PRINCIPAL - Tenta múltiplos caminhos automaticamente
     */
    async function loadComponent(element, filename) {
        console.log(`📦 Tentando carregar: ${filename}`);
        
        // Lista de caminhos possíveis (em ordem de tentativa)
        const possiblePaths = generatePossiblePaths(filename);
        
        // Tenta cada caminho até um funcionar
        for (const path of possiblePaths) {
            try {
                console.log(`  🔍 Tentando: ${path}`);
                const response = await fetch(path);
                
                if (response.ok) {
                    const html = await response.text();
                    element.innerHTML = html;
                    executeScripts(element);
                    console.log(`  ✅ Carregado de: ${path}`);
                    return true;
                }
            } catch (error) {
                // Silencioso - continua para próximo caminho
                continue;
            }
        }
        
        console.log(`  ❌ ${filename} não encontrado em nenhum caminho`);
        return false;
    }
    
    /**
     * GERA TODOS OS CAMINHOS POSSÍVEIS automaticamente
     */
    function generatePossiblePaths(filename) {
        const currentPath = window.location.pathname;
        const paths = [];
        
        // 1. Caminho relativo à página atual
        paths.push(filename); // includes/header.html
        
        // 2. Com ./ no início
        paths.push('./' + filename);
        
        // 3. Caminho absoluto a partir da raiz
        paths.push('/' + filename);
        
        // 4. Se estiver em subpasta, calcula quantos ../ precisa
        if (currentPath !== '/') {
            const depth = currentPath.split('/').length - 2;
            if (depth > 0) {
                const backPath = '../'.repeat(depth) + filename;
                paths.push(backPath);
            }
        }
        
        // 5. Para GitHub Pages /docs/
        if (currentPath.includes('/docs/')) {
            paths.push('/docs/' + filename);
        }
        
        // 6. Caminho completo (útil para CDN ou domínios diferentes)
        const fullUrl = new URL(filename, window.location.origin);
        paths.push(fullUrl.href);
        
        // Remove duplicados
        return [...new Set(paths)];
    }
    
    /**
     * Executa scripts dentro do HTML carregado
     */
    function executeScripts(container) {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            
            // Copia todos os atributos
            Array.from(oldScript.attributes).forEach(attr => {
                newScript.setAttribute(attr.name, attr.value);
            });
            
            // Copia o conteúdo
            newScript.textContent = oldScript.textContent;
            
            // Substitui
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }
    
    /**
     * INICIALIZAÇÃO DO HEADER (menu mobile)
     * Procura por elementos comuns de menu
     */
    function initHeader() {
        console.log('🔧 Inicializando componentes do header...');
        
        // 1. Menu mobile toggle (várias formas comuns)
        const mobileSelectors = [
            '#mobile-menu-btn',
            '.mobile-menu-btn',
            '.menu-toggle',
            '[aria-label="Toggle menu"]',
            '.navbar-toggler'
        ];
        
        const menuSelectors = [
            '#nav-menu',
            '.nav-menu',
            '.navbar-collapse',
            '.main-navigation',
            '.site-navigation'
        ];
        
        let mobileBtn = null;
        let navMenu = null;
        
        // Encontra o botão mobile
        for (const selector of mobileSelectors) {
            const el = document.querySelector(selector);
            if (el) {
                mobileBtn = el;
                break;
            }
        }
        
        // Encontra o menu
        for (const selector of menuSelectors) {
            const el = document.querySelector(selector);
            if (el) {
                navMenu = el;
                break;
            }
        }
        
        // Configura o toggle se ambos existirem
        if (mobileBtn && navMenu) {
            mobileBtn.addEventListener('click', function(e) {
                e.preventDefault();
                navMenu.classList.toggle('active');
                navMenu.classList.toggle('show');
                
                // Alterna ícone se for um ícone
                if (this.innerHTML.includes('fa-bars')) {
                    this.innerHTML = this.innerHTML.replace('fa-bars', 'fa-times');
                } else if (this.innerHTML.includes('fa-times')) {
                    this.innerHTML = this.innerHTML.replace('fa-times', 'fa-bars');
                }
                
                // Acessibilidade
                const expanded = navMenu.classList.contains('active');
                this.setAttribute('aria-expanded', expanded);
                navMenu.setAttribute('aria-hidden', !expanded);
            });
            
            console.log('✅ Menu mobile configurado');
        }
        
        // 2. Marca link ativo (opcional)
        markActiveLinks();
    }
    
    /**
     * Marca o link de navegação ativo baseado na URL
     */
    function markActiveLinks() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link, .menu-item a, .nav a');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            
            // Remove .html e query strings para comparação
            const linkPath = href.split('?')[0].replace('.html', '');
            const current = currentPath.replace('.html', '');
            
            if (current.endsWith(linkPath) || linkPath === current || 
                (current === '/' && (linkPath === '' || linkPath === '/index' || linkPath === 'index'))) {
                link.classList.add('active', 'current-menu-item');
            }
        });
    }
    
    /**
     * INICIALIZAÇÃO DO SIDEBAR (se existir)
     */
    function initSidebar() {
        const toggleBtn = document.querySelector('#sidebar-toggle, .sidebar-toggle');
        const sidebar = document.querySelector('#sidebar, .sidebar');
        
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }
    }
    
    // Expõe funções públicas se necessário (opcional)
    window.DynamicComponents = {
        reload: function(componentId) {
            const element = document.getElementById(componentId);
            if (element) {
                // Encontra o filename original (precisa de algum mapeamento)
                console.log('Recarregando componente:', componentId);
            }
        }
    };
    
})();