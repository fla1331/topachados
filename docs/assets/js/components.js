// VERSÃO SUPER SIMPLES COM CAMINHOS ABSOLUTOS
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Carregando componentes...');
    
    // CARREGAR HEADER
    const headerEl = document.getElementById('header-placeholder');
    if (headerEl) {
        // CAMINHO ABSOLUTO DO GITHUB PAGES
        fetch('/docs/includes/header.html')
            .then(r => r.ok ? r.text() : '')
            .then(html => {
                if (html) {
                    headerEl.innerHTML = html;
                    
                    // Menu mobile
                    const btn = document.getElementById('mobile-menu-btn');
                    const menu = document.getElementById('nav-menu');
                    if (btn && menu) {
                        btn.addEventListener('click', () => menu.classList.toggle('active'));
                    }
                }
            });
    }
    
    // CARREGAR FOOTER
    const footerEl = document.getElementById('footer-placeholder');
    if (footerEl) {
        fetch('/docs/includes/footer.html')
            .then(r => r.ok ? r.text() : '')
            .then(html => { if (html) footerEl.innerHTML = html; });
    }
});