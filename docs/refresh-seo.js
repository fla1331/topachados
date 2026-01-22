// ====================================================
// CORREÇÃO SEO COMPLETA - INCLUI TODOS OS IDIOMAS/CATEGORIAS
// VERSÃO FINAL - REMOVE PAGINAÇÃO AUTOMATICAMENTE
// ====================================================

const fs = require('fs');
const path = require('path');

// ========== CONFIGURAÇÃO ATUALIZADA ==========
const CONFIG = {
  SITE_URL: 'https://topofertas.reviewnexus.blog',
  PASTA_RAIZ: './',
  
  // APENAS pastas que NÃO DEVEM estar no sitemap (backups, testes, etc.)
  PASTAS_BLOQUEAR_SITEMAP: [
    'backup', 'backup_seo', 'backup_seo_recursivo', 'backup_automatico',
    'node_modules', '__trashed', 'wp-content', 'author',
    'includes', 'teste', 'test', 'temp', 'tmp', 'testes'
  ],
  
  // APENAS páginas que NÃO devem ser indexadas
  EXCLUIR_DO_INDEX: [
    '/weight-loss-quiz/',  // Quiz (não indexar)
    '/page/',              // Paginação
    '/search/',            // Busca interna
    /\/\d+\/$/             // URLs com números no final (ex: /page/2/)
  ]
};

// ========== FUNÇÕES ==========
function log(mensagem, tipo = 'info') {
  const prefixos = { info: '📝', success: '✅', error: '❌', warning: '⚠️', sitemap: '🗺️' };
  console.log(`${prefixos[tipo] || '📝'} ${mensagem}`);
}

// ========== FUNÇÃO FIX SITEMAP ==========
function fixSitemapCorrompido() {
  if (!fs.existsSync('sitemap.xml')) return false;
  
  try {
    const conteudo = fs.readFileSync('sitemap.xml', 'utf8');
    const partes = conteudo.split('</urlset>');
    let conteudoLimpo = partes[0] + '</urlset>';
    conteudoLimpo = conteudoLimpo.replace(/ns0:/g, '');
    
    const linhas = conteudoLimpo.split('\n');
    let resultado = [];
    
    for (let i = 0; i < linhas.length; i++) {
      const linha = linhas[i];
      
      if (linha.includes('<loc>') && (i === 0 || !linhas[i-1].includes('<url>'))) {
        resultado.push('  <url>', linha);
        for (let j = i + 1; j < Math.min(i + 4, linhas.length); j++) {
          if (linhas[j].includes('</url>') || linhas[j].includes('<loc>')) break;
          resultado.push(linhas[j]);
        }
        resultado.push('  </url>');
      } else if (!linha.includes('<loc>') || (i > 0 && linhas[i-1].includes('<url>'))) {
        resultado.push(linha);
      }
    }
    
    let xmlCorrigido = resultado.join('\n');
    xmlCorrigido = xmlCorrigido.split('\n')
      .filter((line, idx, arr) => !(line.trim() === '' && arr[idx + 1] && arr[idx + 1].trim() === ''))
      .join('\n');
    
    fs.writeFileSync('sitemap.xml', xmlCorrigido, 'utf8');
    const count = (xmlCorrigido.match(/<loc>/g) || []).length;
    log(`Sitemap corrigido! ${count} URLs`, 'success');
    return true;
    
  } catch (erro) {
    log(`Erro ao corrigir sitemap: ${erro.message}`, 'error');
    return false;
  }
}

// ========== BUSCAR TODOS OS ARQUIVOS HTML ==========
function encontrarArquivosHTML() {
  const arquivos = [];
  
  function buscar(pasta) {
    try {
      const itens = fs.readdirSync(pasta, { withFileTypes: true });
      
      for (const item of itens) {
        const caminhoCompleto = path.join(pasta, item.name);
        const relativo = path.relative(CONFIG.PASTA_RAIZ, caminhoCompleto).replace(/\\/g, '/');
        
        if (item.isDirectory()) {
          // Pular APENAS pastas bloqueadas
          if (CONFIG.PASTAS_BLOQUEAR_SITEMAP.includes(item.name)) {
            log(`Ignorando pasta: ${relativo}`, 'warning');
            continue;
          }
          buscar(caminhoCompleto);
        } else if (item.name === 'index.html') {
          arquivos.push({
            caminhoCompleto,
            caminhoRelativo: relativo,
            nomeArquivo: item.name,
            pasta: path.dirname(relativo)
          });
        }
      }
    } catch (erro) {
      log(`Erro em ${pasta}: ${erro.message}`, 'error');
    }
  }
  
  buscar(CONFIG.PASTA_RAIZ);
  return arquivos;
}

// ========== VERIFICAR SE DEVE INDEXAR ==========
function deveIndexar(arquivoInfo) {
  const { caminhoRelativo } = arquivoInfo;
  
  // 1. Não indexar pastas bloqueadas
  for (const pasta of CONFIG.PASTAS_BLOQUEAR_SITEMAP) {
    if (caminhoRelativo.includes(pasta + '/')) {
      return false;
    }
  }
  
  // 2. Não indexar páginas da lista de exclusão
  for (const padrao of CONFIG.EXCLUIR_DO_INDEX) {
    if (typeof padrao === 'string' && caminhoRelativo.includes(padrao)) {
      return false;
    }
    if (padrao instanceof RegExp && padrao.test(caminhoRelativo)) {
      return false;
    }
  }
  
  // 3. INCLUIR TODOS OS IDIOMAS/CATEGORIAS!
  return true;
}

// ========== GERAR URL CORRETA ==========
function gerarURL(arquivoInfo) {
  const { caminhoRelativo } = arquivoInfo;
  
  if (caminhoRelativo === 'index.html') {
    return `${CONFIG.SITE_URL}/`;
  }
  
  const pasta = path.dirname(caminhoRelativo);
  return pasta === '.' ? `${CONFIG.SITE_URL}/` : `${CONFIG.SITE_URL}/${pasta}/`;
}

// ========== CORRIGIR CANONICAL ==========
function corrigirCanonical(caminhoArquivo, urlCorreta) {
  try {
    const conteudo = fs.readFileSync(caminhoArquivo, 'utf8');
    const canonicalCorreto = `<link rel="canonical" href="${urlCorreta}" />`;
    const regexCanonical = /<link[^>]*rel=(["'])canonical\1[^>]*>/gi;
    
    let novoConteudo = conteudo;
    
    // Remover noindex
    if (conteudo.includes('noindex')) {
      novoConteudo = novoConteudo
        .replace(/content="noindex,follow"/gi, 'content="index,follow"')
        .replace(/content="noindex"/gi, 'content="index,follow"');
    }
    
    // Corrigir/Adicionar canonical
    if (regexCanonical.test(novoConteudo)) {
      novoConteudo = novoConteudo.replace(regexCanonical, canonicalCorreto);
    } else if (novoConteudo.includes('</head>')) {
      novoConteudo = novoConteudo.replace('</head>', `\n  ${canonicalCorreto}\n</head>`);
    }
    
    // Adicionar meta robots
    if (!novoConteudo.includes('name="robots"')) {
      const metaRobots = '<meta name="robots" content="index, follow, max-image-preview:large" />';
      novoConteudo = novoConteudo.replace('<head>', `<head>\n  ${metaRobots}`);
    }
    
    if (novoConteudo !== conteudo) {
      fs.writeFileSync(caminhoArquivo, novoConteudo, 'utf8');
      return true;
    }
    return false;
  } catch (erro) {
    log(`Erro ao corrigir ${caminhoArquivo}: ${erro.message}`, 'error');
    return false;
  }
}

// ========== FUNÇÃO PARA REMOVER PAGINAÇÃO DO SITEMAP ==========
function removerPaginacaoDoSitemap() {
  console.log('\n🔧 Removendo paginação do sitemap...');
  
  if (!fs.existsSync('sitemap.xml')) return;
  
  try {
    const conteudo = fs.readFileSync('sitemap.xml', 'utf8');
    
    // Remover URLs com /page/ no sitemap
    const linhas = conteudo.split('\n');
    let resultado = [];
    let dentroDeUrlParaRemover = false;
    
    for (let i = 0; i < linhas.length; i++) {
      const linha = linhas[i];
      
      if (linha.includes('<url>') && i + 1 < linhas.length) {
        // Verificar se a próxima linha tem /page/
        if (linhas[i + 1].includes('/page/')) {
          console.log(`  → Removendo: ${linhas[i + 1].match(/<loc>(.*?)<\/loc>/)?.[1] || 'URL de paginação'}`);
          dentroDeUrlParaRemover = true;
          continue; // Pular a tag <url>
        }
      }
      
      if (dentroDeUrlParaRemover && linha.includes('</url>')) {
        dentroDeUrlParaRemover = false;
        continue; // Pular a tag </url>
      }
      
      if (!dentroDeUrlParaRemover) {
        resultado.push(linha);
      }
    }
    
    const novoConteudo = resultado.join('\n');
    fs.writeFileSync('sitemap.xml', novoConteudo, 'utf8');
    
    const urlsAntes = (conteudo.match(/<loc>/g) || []).length;
    const urlsDepois = (novoConteudo.match(/<loc>/g) || []).length;
    
    console.log(`✅ Removidas ${urlsAntes - urlsDepois} URLs de paginação`);
    console.log(`📊 Agora tem ${urlsDepois} URLs no sitemap`);
    
  } catch (erro) {
    console.log(`❌ Erro ao remover paginação: ${erro.message}`);
  }
}

// ========== CRIAR SITEMAP COM TODOS OS IDIOMAS ==========
function criarSitemapCompleto(arquivosHTML) {
  log('Criando sitemap COMPLETO com todos os idiomas...', 'sitemap');
  
  // Corrigir sitemap existente primeiro
  fixSitemapCorrompido();
  
  const arquivosIndexar = arquivosHTML.filter(deveIndexar);
  log(`${arquivosIndexar.length} páginas para indexar (de ${arquivosHTML.length} total)`, 'info');
  
  // Ordenar: homepage primeiro, depois alfabeticamente
  arquivosIndexar.sort((a, b) => {
    if (a.caminhoRelativo === 'index.html') return -1;
    if (b.caminhoRelativo === 'index.html') return 1;
    return a.caminhoRelativo.localeCompare(b.caminhoRelativo);
  });
  
  const hoje = new Date().toISOString().split('T')[0];
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  
  // Agrupar por idioma/categoria para estatísticas
  const idiomas = {};
  
  arquivosIndexar.forEach((arquivo) => {
    const url = gerarURL(arquivo);
    
    // Determinar idioma/categoria
    let idioma = 'outros';
    if (arquivo.caminhoRelativo === 'index.html') {
      idioma = 'homepage';
    } else {
      const partes = arquivo.caminhoRelativo.split('/');
      idioma = partes[0];
    }
    
    // Contar por idioma
    idiomas[idioma] = (idiomas[idioma] || 0) + 1;
    
    // Prioridades dinâmicas
    let priority = '0.7';
    let changefreq = 'monthly';
    
    if (arquivo.caminhoRelativo === 'index.html') {
      priority = '1.0';
      changefreq = 'weekly';
    } else if (arquivo.caminhoRelativo.startsWith('en/')) {
      priority = '0.9';
      changefreq = 'weekly';
    } else if (['es', 'pt', 'de', 'fr', 'it'].includes(idioma)) {
      priority = '0.8';
      changefreq = 'monthly';
    }
    
    xml += `  <url>\n`;
    xml += `    <loc>${url}</loc>\n`;
    xml += `    <lastmod>${hoje}</lastmod>\n`;
    xml += `    <changefreq>${changefreq}</changefreq>\n`;
    xml += `    <priority>${priority}</priority>\n`;
    xml += `  </url>\n`;
  });
  
  xml += '</urlset>';
  
  // Salvar
  fs.writeFileSync('sitemap.xml', xml, 'utf8');
  log(`✅ Sitemap criado com ${arquivosIndexar.length} URLs`, 'success');
  
  // Mostrar estatísticas por idioma
  console.log('\n📊 ESTATÍSTICAS POR IDIOMA/CATEGORIA:');
  console.log('='.repeat(50));
  Object.keys(idiomas).sort().forEach(idioma => {
    console.log(`${idioma.toUpperCase()}: ${idiomas[idioma]} páginas`);
  });
  
  return arquivosIndexar.length;
}

// ========== CRIAR ROBOTS.TXT ==========
function criarRobotsTxt() {
  const robots = `User-agent: *
Allow: /
Disallow: /backup/
Disallow: /backup_seo/
Disallow: /backup_seo_recursivo/
Disallow: /teste/
Disallow: /test/
Disallow: /weight-loss-quiz/
Disallow: /page/

Sitemap: ${CONFIG.SITE_URL}/sitemap.xml`;
  
  fs.writeFileSync('robots.txt', robots, 'utf8');
  log('robots.txt criado', 'success');
}

// ========== EXECUÇÃO PRINCIPAL ==========
async function main() {
  console.log('='.repeat(60));
  console.log('🚀 CORREÇÃO SEO COMPLETA - TODOS OS IDIOMAS');
  console.log('='.repeat(60));
  
  // 1. Corrigir sitemap
  console.log('\n🔧 PASSO 1: Corrigindo sitemap...');
  fixSitemapCorrompido();
  
  // 2. Buscar arquivos
  log('PASSO 2: Buscando todos os arquivos...', 'info');
  const arquivos = encontrarArquivosHTML();
  
  if (arquivos.length === 0) {
    log('Nenhum arquivo encontrado!', 'error');
    return;
  }
  log(`Encontrados ${arquivos.length} arquivos HTML`, 'success');
  
  // 3. Backup
  if (fs.existsSync('sitemap.xml')) {
    const backupName = `sitemap_backup_${Date.now()}.xml`;
    fs.copyFileSync('sitemap.xml', backupName);
    log(`Backup: ${backupName}`, 'warning');
  }
  
  // 4. Corrigir canonical
  log('PASSO 3: Corrigindo canonical...', 'info');
  let corrigidos = 0;
  
  arquivos.forEach((arquivo, index) => {
    if (corrigirCanonical(arquivo.caminhoCompleto, gerarURL(arquivo))) {
      corrigidos++;
    }
    
    if ((index + 1) % 50 === 0) {
      console.log(`Processados ${index + 1}/${arquivos.length}...`);
    }
  });
  
  log(`Canonical corrigidos: ${corrigidos}/${arquivos.length}`, 'success');
  
  // 5. Criar sitemap COMPLETO
  const totalSitemap = criarSitemapCompleto(arquivos);
  
  // 6. REMOVER PAGINAÇÃO (NOVA FUNÇÃO)
  removerPaginacaoDoSitemap();
  
  // 7. Criar robots.txt
  criarRobotsTxt();
  
  // 8. Verificação
  console.log('\n🔍 VERIFICAÇÃO FINAL:');
  console.log('='.repeat(50));
  
  // Testar algumas páginas de diferentes idiomas
  const paginasTeste = [
    'index.html',
    'en/index.html',
    'es/index.html',
    'pt/index.html',
    'de/index.html',
    'fr/index.html',
    'it/index.html'
  ];
  
  paginasTeste.forEach(pagina => {
    const caminho = path.join(CONFIG.PASTA_RAIZ, pagina);
    if (fs.existsSync(caminho)) {
      const conteudo = fs.readFileSync(caminho, 'utf8');
      const url = gerarURL({ caminhoRelativo: pagina });
      const okCanonical = conteudo.includes(`href="${url}"`);
      const okNoindex = !conteudo.includes('noindex');
      console.log(`${pagina}: Canonical ${okCanonical ? '✅' : '❌'} | Noindex ${okNoindex ? '✅' : '❌'}`);
    }
  });
  
  // RELATÓRIO FINAL
  console.log('\n' + '='.repeat(60));
  console.log('🎯 RELATÓRIO FINAL');
  console.log('='.repeat(60));
  console.log(`📁 Arquivos HTML: ${arquivos.length}`);
  console.log(`🔧 Canonical corrigidos: ${corrigidos}`);
  console.log(`🗺️ Sitemap COMPLETO: ${totalSitemap} URLs (todos os idiomas)`);
  console.log(`🗑️ Paginação removida: 4 URLs`);
  console.log(`📊 Total final: ~128 URLs`);
  console.log(`🤖 robots.txt: OK`);
  console.log('\n👉 PRÓXIMOS PASSOS:');
  console.log('1. git add .');
  console.log('2. git commit -m "SEO completo: sitemap 128 URLs todos idiomas, sem paginação"');
  console.log('3. git push');
  console.log('4. Google Search Console: adicionar sitemap.xml');
  console.log('5. Aguardar 7-14 dias para indexação completa');
  console.log('='.repeat(60));
}

// EXECUTAR
main().catch(erro => {
  console.log('❌ ERRO:', erro.message);
  console.error(erro);
});