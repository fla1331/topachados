/**
 * COMPONENTES DINÂMICOS 
 */
(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Iniciando componentes dinâmicos...');
        
        // Carrega componentes principais
        loadComponent('header-placeholder', 'includes/header.html', initHeader);
        loadComponent('footer-placeholder', 'includes/footer.html');
        
        // Carrega sidebar como conteúdo estático (SEM inicialização)
        loadComponent('sidebar-placeholder', 'includes/sidebar.html');
    });
    
    async function loadComponent(elementId, filePath, onSuccess) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.log(`⏭️ ${elementId} não encontrado`);
            return;
        }
        
        // Tenta múltiplos caminhos
        const paths = [
            filePath,                    // includes/header.html
            './' + filePath,            // ./includes/header.html  
            '/' + filePath,             // /includes/header.html
            '../' + filePath,           // ../includes/header.html
            '../../' + filePath         // ../../includes/header.html
        ];
        
        for (const path of paths) {
            try {
                const response = await fetch(path);
                if (response.ok) {
                    const html = await response.text();
                    element.innerHTML = html;
                    console.log(`✅ ${elementId} carregado de: ${path}`);
                    
                    // Executa scripts internos
                    element.querySelectorAll('script').forEach(oldScript => {
                        const newScript = document.createElement('script');
                        newScript.textContent = oldScript.textContent;
                        oldScript.parentNode.replaceChild(newScript, oldScript);
                    });
                    
                    // Callback de sucesso (só para header)
                    if (onSuccess) onSuccess();
                    return;
                }
            } catch (error) {
                continue;
            }
        }
        
        console.log(`❌ ${filePath} não encontrado`);
    }
    
    /**
     * INICIALIZA O HEADER COM SEUS IDs ESPECÍFICOS
     */
    function initHeader() {
        console.log('🔧 Inicializando header...');
        
        // SEUS IDs ESPECÍFICOS:
        const menuToggle = document.getElementById('menuToggle');
        const mainNav = document.getElementById('mainNav');
        
        console.log('MenuToggle encontrado?', !!menuToggle);
        console.log('MainNav encontrado?', !!mainNav);
        
        if (menuToggle && mainNav) {
            console.log('✅ Configurando menu mobile...');
            
            // Elementos de ícone dentro do botão
            const barsIcon = menuToggle.querySelector('.fa-bars');
            const timesIcon = menuToggle.querySelector('.fa-times');
            
            // Inicialmente esconde o "X"
            if (timesIcon) timesIcon.style.display = 'none';
            
            menuToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('🖱️ MenuToggle clicado!');
                
                // Alterna classe no menu
                mainNav.classList.toggle('active');
                
                // Alterna ícones
                if (barsIcon && timesIcon) {
                    if (mainNav.classList.contains('active')) {
                        barsIcon.style.display = 'none';
                        timesIcon.style.display = 'inline-block';
                    } else {
                        barsIcon.style.display = 'inline-block';
                        timesIcon.style.display = 'none';
                    }
                }
                
                // Alterna aria-label
                const isExpanded = mainNav.classList.contains('active');
                menuToggle.setAttribute('aria-expanded', isExpanded);
                menuToggle.setAttribute('aria-label', isExpanded ? 
                    'Fechar menu de navegação' : 'Abrir menu de navegação');
                
                console.log('Menu está:', isExpanded ? 'ABERTO' : 'FECHADO');
            });
            
            // Fecha menu ao clicar fora (OPCIONAL)
            document.addEventListener('click', function(e) {
                if (!mainNav.contains(e.target) && !menuToggle.contains(e.target)) {
                    mainNav.classList.remove('active');
                    if (barsIcon && timesIcon) {
                        barsIcon.style.display = 'inline-block';
                        timesIcon.style.display = 'none';
                    }
                    menuToggle.setAttribute('aria-expanded', 'false');
                    menuToggle.setAttribute('aria-label', 'Abrir menu de navegação');
                }
            });
            
            // Fecha menu ao pressionar ESC
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && mainNav.classList.contains('active')) {
                    mainNav.classList.remove('active');
                    if (barsIcon && timesIcon) {
                        barsIcon.style.display = 'inline-block';
                        timesIcon.style.display = 'none';
                    }
                }
            });
        } else {
            console.error('❌ Elementos do menu não encontrados!');
            console.log('Procurando por: #menuToggle e #mainNav');
        }
        
        // Marca link ativo na navegação
        markActiveNavLinks();
    }
    
    /**
     * MARCA O LINK ATIVO BASEADO NA URL
     */
    function markActiveNavLinks() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('#mainNav a, .main-nav a');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath === new URL(href, window.location.origin).pathname) {
                link.classList.add('active');
                link.parentElement.classList.add('active');
            }
        });
    }
})();