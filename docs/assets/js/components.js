// COMPONENTES DINÂMICOS - IDs CORRETOS
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando carregamento de componentes...');
    
    // CONFIGURAÇÃO - Caminhos RELATIVOS
    const config = {
        header: './includes/header.html',
        footer: './includes/footer.html',
        sidebar: './includes/sidebar.html'
    };
    
    // 1. CARREGAR HEADER (ID: header-placeholder)
    const headerPlaceholder = document.getElementById('header-placeholder');
    if (headerPlaceholder) {
        console.log('📌 Carregando header...');
        fetch(config.header)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}: ${config.header}`);
                return response.text();
            })
            .then(html => {
                headerPlaceholder.innerHTML = html;
                console.log('✅ Header carregado!');
                initHeader();
            })
            .catch(error => {
                console.error('❌ Erro no header:', error.message);
                headerPlaceholder.innerHTML = `
                    <div style="background:#2c3e50;color:white;padding:15px;">
                        <a href="./" style="color:white;text-decoration:none;">TopOfertas</a>
                        <small style="display:block;color:#bdc3c7;">Erro: ${error.message}</small>
                    </div>
                `;
            });
    }
    
    // 2. CARREGAR FOOTER (ID: footer-placeholder)
    const footerPlaceholder = document.getElementById('footer-placeholder');
    if (footerPlaceholder) {
        console.log('📌 Carregando footer...');
        fetch(config.footer)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}: ${config.footer}`);
                return response.text();
            })
            .then(html => {
                footerPlaceholder.innerHTML = html;
                console.log('✅ Footer carregado!');
                initFooter();
            })
            .catch(error => {
                console.error('❌ Erro no footer:', error.message);
                footerPlaceholder.innerHTML = `
                    <footer style="background:#34495e;color:white;padding:20px;text-align:center;">
                        <p>&copy; ${new Date().getFullYear()} TopOfertas</p>
                        <small style="color:#bdc3c7;">Erro ao carregar footer</small>
                    </footer>
                `;
            });
    }
    
    // 3. CARREGAR SIDEBAR (ID: sidebar-container - se existir)
    const sidebarContainer = document.getElementById('sidebar-container');
    if (sidebarContainer) {
        console.log('📌 Carregando sidebar...');
        fetch(config.sidebar)
            .then(response => {
                if (!response.ok) return ''; // Sidebar é opcional
                return response.text();
            })
            .then(html => {
                if (html) {
                    sidebarContainer.innerHTML = html;
                    console.log('✅ Sidebar carregado!');
                    initSidebar();
                }
            })
            .catch(error => {
                console.warn('⚠️ Sidebar opcional não carregada');
            });
    }
    
    // FUNÇÕES DE INICIALIZAÇÃO
    function initHeader() {
        console.log('🔧 Inicializando header...');
        const mobileBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.getElementById('nav-menu');
        
        if (mobileBtn && navMenu) {
            mobileBtn.addEventListener('click', function() {
                navMenu.classList.toggle('active');
                this.innerHTML = navMenu.classList.contains('active') 
                    ? '<i class="fas fa-times"></i>' 
                    : '<i class="fas fa-bars"></i>';
            });
        }
        
        // Marcar link ativo
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || 
                (currentPage === '' && href === './index.html') ||
                (href && href.includes(currentPage.replace('.html', '')))) {
                link.classList.add('active');
            }
        });
    }
    
    function initFooter() {
        console.log('🔧 Inicializando footer...');
        // Atualizar ano automaticamente
        const yearElement = document.getElementById('current-year');
        if (yearElement) {
            yearElement.textContent = new Date().getFullYear();
        }
    }
    
    function initSidebar() {
        console.log('🔧 Inicializando sidebar...');
        const toggleBtn = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
        }
    }
});