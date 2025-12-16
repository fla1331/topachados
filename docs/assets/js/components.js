// COMPONENTES DINÂMICOS - VERSÃO RECOMENDADA
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. CARREGAR HEADER
    const headerEl = document.getElementById('header-placeholder');
    if (headerEl) {
        fetch('includes/header.html')
            .then(response => response.text())
            .then(html => {
                headerEl.innerHTML = html;
                
                // Menu mobile
                const menuBtn = document.getElementById('mobile-menu-btn');
                const navMenu = document.getElementById('nav-menu');
                if (menuBtn && navMenu) {
                    menuBtn.addEventListener('click', function() {
                        navMenu.classList.toggle('active');
                        this.innerHTML = navMenu.classList.contains('active') 
                            ? '<i class="fas fa-times"></i>' 
                            : '<i class="fas fa-bars"></i>';
                    });
                }
            })
            .catch(() => {
                console.log('Header não carregado (opcional)');
            });
    }
    
    // 2. CARREGAR FOOTER
    const footerEl = document.getElementById('footer-placeholder');
    if (footerEl) {
        fetch('includes/footer.html')
            .then(response => response.text())
            .then(html => footerEl.innerHTML = html)
            .catch(() => {
                console.log('Footer não carregado (opcional)');
            });
    }
});