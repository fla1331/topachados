// Obtém referências aos elementos do banner
const cookieBanner = document.getElementById('cookie-banner');
const acceptButton = document.getElementById('acceptCookies');
const declineButton = document.getElementById('declineCookies');

// Chave no localStorage para armazenar o consentimento
const consentKey = 'cookieConsentGiven';

// 1. Função para verificar e exibir o banner
function checkCookieConsent() {
    // Se o usuário já deu o consentimento, não faz nada
    if (localStorage.getItem(consentKey) === 'true') {
        cookieBanner.style.display = 'none';
    } else {
        // Se ainda não deu, mostra o banner (o padrão no CSS deve ser 'flex')
        cookieBanner.style.display = 'flex';
    }
}

// 2. Função para salvar o consentimento (independente da escolha)
function giveConsent() {
    localStorage.setItem(consentKey, 'true');
    cookieBanner.style.display = 'none';
    // Se precisar carregar scripts de rastreamento (Google Analytics, etc.), o código iria aqui!
}

// 3. Funções para lidar com os cliques
acceptButton.addEventListener('click', () => {
    giveConsent();
    console.log('Cookies aceitos.');
});

declineButton.addEventListener('click', () => {
    giveConsent(); // Salva que a escolha foi feita (mesmo que seja recusar)
    console.log('Cookies recusados. Nenhum script de rastreamento foi carregado.');
});

// Executa a verificação ao carregar a página
document.addEventListener('DOMContentLoaded', checkCookieConsent);