// COMPONENTES DINÂMICOS - VERSÃO FUNCIONAL
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Iniciando carregamento de componentes...');

    // 1. CARREGAR HEADER
    const headerEl = document.getElementById('header-placeholder');
    if (headerEl) {
        // Tenta carregar o arquivo REAL
        fetch('includes/header.html')
            .then(response => {
                if (!response.ok) {
                    // Se falhar, NÃO jogue erro, apenas retorne vazio
                    console.warn('Arquivo header.html não encontrado.');
                    return '';
                }
                return response.text();
            })
            .then(html => {
                if (html) {
                    console.log('✅ Header carregado do arquivo.');
                    headerEl.innerHTML = html;
                    initHeader(); // Inicializa o menu mobile
                }
                // Se html for vazio, não faz nada (não coloca fallback)
            })
            .catch(error => {
                console.error('Erro na rede:', error);
                // IMPORTANTE: NÃO insere fallback aqui. Deixa vazio.
            });
    }

    // 2. CARREGAR FOOTER
    const footerEl = document.getElementById('footer-placeholder');
    if (footerEl) {
        fetch('includes/footer.html')
            .then(response => response.ok ? response.text() : '')
            .then(html => {
                if (html) {
                    console.log('✅ Footer carregado do arquivo.');
                    footerEl.innerHTML = html;
                }
            })
            .catch(error => console.error('Erro footer:', error));
    }

    // 3. CARREGAR SIDEBAR (se o ID no HTML for "sidebar-container")
    // Se você não vai usar sidebar, pode remover esta parte
    const sidebarEl = document.getElementById('sidebar-container'); // <<< Note o ID
    if (sidebarEl) {
        fetch('includes/sidebar.html')
            .then(response => response.ok ? response.text() : '')
            .then(html => { if (html) sidebarEl.innerHTML = html; })
            .catch(e => console.log('Sidebar opcional não carregada.'));
    }

    // Função para menu mobile (só roda se o header real carregar)
    function initHeader() {
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
    }
});