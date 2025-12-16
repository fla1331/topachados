// VERSÃO MÍNIMA - Só carrega, sem fallback
document.addEventListener('DOMContentLoaded', function() {
    
    // Carrega header
    const headerEl = document.getElementById('header-placeholder');
    if (headerEl) {
        fetch('./includes/header.html')
            .then(r => r.text())
            .then(html => {
                headerEl.innerHTML = html;
                // Menu mobile
                const btn = document.getElementById('mobile-menu-btn');
                const menu = document.getElementById('nav-menu');
                if (btn && menu) {
                    btn.addEventListener('click', () => menu.classList.toggle('active'));
                }
            })
            .catch(e => console.log('Header não carregado'));
    }
    
    // Carrega footer
    const footerEl = document.getElementById('footer-placeholder');
    if (footerEl) {
        fetch('./includes/footer.html')
            .then(r => r.text())
            .then(html => footerEl.innerHTML = html)
            .catch(e => console.log('Footer não carregado'));
    }
});