/**
 * SCRIPT PRINCIPAL - Top Ofertas
 * Inclui: Menu mobile + Cookie Banner + Outras funcionalidades
 */

// ========== MENU MOBILE ==========
function initMobileMenu() {
    console.log('🔧 Inicializando menu mobile...');
    
    const menuToggle = document.getElementById('menuToggle');
    const mainNav = document.getElementById('mainNav');
    const navOverlay = document.getElementById('navOverlay');
    const body = document.body;

    if (!menuToggle || !mainNav) {
        console.log('⚠️ Elementos do menu não encontrados');
        return;
    }

    // Se não existir overlay, cria um dinamicamente
    if (!navOverlay) {
        const overlay = document.createElement('div');
        overlay.id = 'navOverlay';
        overlay.className = 'nav-overlay';
        document.body.appendChild(overlay);
    }

    const overlay = document.getElementById('navOverlay');

    // TOGGLE MENU
    menuToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        mainNav.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // Previne scroll quando menu aberto
        if (mainNav.classList.contains('active')) {
            body.style.overflow = 'hidden';
        } else {
            body.style.overflow = '';
        }
    });

    // FECHA MENU AO CLICAR NO OVERLAY
    overlay.addEventListener('click', function() {
        mainNav.classList.remove('active');
        overlay.classList.remove('active');
        body.style.overflow = '';
    });

    // FECHA MENU AO CLICAR EM UM LINK (MOBILE)
    const navLinks = document.querySelectorAll('.main-nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            mainNav.classList.remove('active');
            overlay.classList.remove('active');
            body.style.overflow = '';
        });
    });

    // FECHA MENU AO REDIMENSIONAR A TELA
    window.addEventListener('resize', function() {
        if (window.innerWidth > 600) {
            mainNav.classList.remove('active');
            overlay.classList.remove('active');
            body.style.overflow = '';
        }
    });

    console.log('✅ Menu mobile configurado');
}

// ========== COOKIE BANNER ==========
function initCookieBanner() {
    console.log('🍪 Inicializando cookie banner...');
    
    const cookieBanner = document.getElementById('cookie-banner');
    const acceptButton = document.getElementById('acceptCookies');
    const declineButton = document.getElementById('declineCookies');
    const consentKey = 'cookieConsentGiven';

    if (!cookieBanner || !acceptButton || !declineButton) {
        console.log('⚠️ Elementos do cookie banner não encontrados');
        return;
    }

    // VERIFICA CONSENTIMENTO
    function checkCookieConsent() {
        if (localStorage.getItem(consentKey) === 'true') {
            cookieBanner.style.display = 'none';
        } else {
            cookieBanner.style.display = 'flex';
        }
    }

    // SALVA CONSENTIMENTO
    function giveConsent() {
        localStorage.setItem(consentKey, 'true');
        cookieBanner.style.display = 'none';
        // Adicione scripts de rastreamento aqui se necessário
    }

    // EVENT LISTENERS
    acceptButton.addEventListener('click', () => {
        giveConsent();
        console.log('Cookies aceitos.');
    });

    declineButton.addEventListener('click', () => {
        giveConsent(); // Salva que a escolha foi feita
        console.log('Cookies recusados.');
    });

    // INICIALIZA
    checkCookieConsent();
    console.log('✅ Cookie banner configurado');
}

// ========== INICIALIZAÇÃO GERAL ==========
function initAll() {
    console.log('🚀 Inicializando todas as funcionalidades...');
    
    // Menu mobile (só se os elementos existirem)
    if (document.getElementById('menuToggle') && document.getElementById('mainNav')) {
        initMobileMenu();
    }
    
    // Cookie banner (só se os elementos existirem)
    if (document.getElementById('cookie-banner')) {
        initCookieBanner();
    }
    
    // Adicione outras inicializações aqui...
    // initNewsletter();
    // initProductFilters();
    // initScrollAnimations();
}

// ========== EXECUÇÃO ==========
// Opção 1: Aguarda componentes carregarem (RECOMENDADO)
document.addEventListener('DOMContentLoaded', function() {
    // Pequeno delay para garantir que componentes.js já carregou os elementos
    setTimeout(initAll, 100);
});

// Opção 2: Se quiser expor funções globalmente (opcional)
window.Topofertas = {
    initMobileMenu: initMobileMenu,
    initCookieBanner: initCookieBanner,
    initAll: initAll
};

console.log('📁 script.js carregado');