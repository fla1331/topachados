// load-components-failproof.js
(function() {
  'use strict';
  
  const COMPONENTS = {
    'header-container': 'includes/header.html',
    'footer-placeholder': 'includes/footer.html'
  };
  
  function loadComponent(id, url) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            resolve(xhr.responseText);
          } else {
            reject(new Error(`HTTP ${xhr.status}: ${url}`));
          }
        }
      };
      xhr.send();
    });
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    Object.entries(COMPONENTS).forEach(([id, url]) => {
      const element = document.getElementById(id);
      if (element) {
        loadComponent(id, url)
          .then(html => {
            element.innerHTML = html;
            console.log(`✓ ${id} loaded`);
          })
          .catch(error => {
            console.warn(`✗ ${id} failed:`, error.message);
            // Mostra link para debug
            element.innerHTML = `
              <div style="border: 2px dashed red; padding: 10px; margin: 10px;">
                <p><strong>Erro ao carregar ${id}</strong></p>
                <p>Tentou carregar: ${url}</p>
                <p><a href="${url}" target="_blank">Clique para testar se o arquivo existe</a></p>
              </div>
            `;
          });
      }
    });
  });
})();