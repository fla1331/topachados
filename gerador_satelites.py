#!/usr/bin/env python3
"""
GERADOR DE ARTIGOS SATÉLITE - SISTEMA 11/10
Versão Final: Gestão completa de satélites com correções e sitemap automático
"""

import os
import re
import requests
import time
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import shutil

# Carrega variáveis do .env
load_dotenv()

# Configurações
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat"
DOCS_DIR = Path.cwd() / "docs"
SITEMAP_PATH = DOCS_DIR / "sitemap.xml"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Gerador Satélites v3.0"
}

# Tipos de artigos satélite OTIMIZADOS (3 por produto)
SATELLITE_TYPES = [
    {
        "slug": "vale-a-pena-e-bom",
        "nome": "Vale a Pena? É Bom?",
        "intent": "Avaliar custo-benefício E qualidade do produto",
        "title_hint": "{PRODUTO} Vale a Pena? É Bom? Análise Completa e Honesta {ANO_ATUAL}",
        "focus": "custo-benefício, qualidade, durabilidade, prós e contras, experiência real",
        "sidebar_title": "Análise do Produto",
        "sidebar_content": "Avaliação detalhada sobre qualidade e custo-benefício"
    },
    {
        "slug": "como-escolher-guia",
        "nome": "Como Escolher - Guia",
        "intent": "Guia completo para escolher o melhor produto na categoria",
        "title_hint": "Como Escolher {CATEGORIA} Ideal em {ANO_ATUAL} - Guia Definitivo",
        "focus": "critérios de escolha, especificações técnicas, dicas práticas, erros a evitar",
        "sidebar_title": "Guia de Compra",
        "sidebar_content": "Aprenda a escolher o melhor produto para suas necessidades"
    },
    {
        "slug": "funciona-comparativo",
        "nome": "Funciona? Comparativo",
        "intent": "Analisar eficácia e comparar com alternativas do mercado",
        "title_hint": "{PRODUTO} Funciona Mesmo? Comparativo com Melhores Marcas {ANO_ATUAL}",
        "focus": "efetividade, resultados reais, comparação com concorrentes, alternativas",
        "sidebar_title": "Comparativos",
        "sidebar_content": "Veja como se compara com outras opções do mercado"
    }
]

PROMPT_SATELITE = """Você é um redator especialista em SEO e criação de conteúdo informativo para blogs.

Crie UM artigo satélite completo, aprofundado e OTIMIZADO PARA SEO.

🎯 OBJETIVO DO ARTIGO SATÉLITE:
- Gerar tráfego orgânico com palavras-chave de longa cauda
- Responder dúvidas específicas do usuário
- Educar e informar SEM vender diretamente
- Conduzir naturalmente para o review principal
- Estabelecer autoridade no tópico

🔍 OTTIMIZAÇÃO SEO OBRIGATÓRIA:
1. Título: Incluir palavra-chave principal + termos como "guia completo", "análise detalhada"
2. Meta Description: 150-160 caracteres com CTA para ler review
3. Conteúdo: Mínimo 1800 palavras
4. Links: 3-4 links NATURAIS para o review principal
5. FAQ: 4-6 perguntas otimizadas
6. Conclusão: CTA forte para o review completo

🧠 REGRAS ESTRITAS:
- NUNCA mencionar afiliados, comissões ou vendas
- Foco 100% em informação e educação
- Texto ORIGINAL (não copiar do review)
- Linguagem natural e envolvente (português BR)
- Incluir dados, exemplos e informações úteis

📎 LINKS OBRIGATÓRIOS PARA O REVIEW:
1. No mínimo 3 links contextuais durante o texto
   Exemplo: "Para ver todos os testes que fizemos, <a href="LINK_REVIEW">leia nosso review completo</a>"
2. Um link no final de cada seção importante
3. CTA explícito na conclusão
4. Menção no FAQ

📋 ESTRUTURA DO ARTICLE:
<article class="content">
  <h1>Título Principal Aqui</h1>
  
  <div class="article-meta">
    <span><i class="far fa-calendar-alt"></i> DATA_ATUAL</span>
    <span><i class="far fa-user"></i> Equipe TechReviews</span>
    <span><i class="far fa-clock"></i> X min de leitura</span>
    <span><i class="fas fa-tag"></i> CATEGORIA</span>
  </div>
  
  <h2>Introdução</h2>
  <p>Contexto da dúvida. Inclua palavra-chave no primeiro parágrafo. 
  <strong>Importante:</strong> Este artigo complementa nosso <a href="LINK_REVIEW">review completo do produto</a>.</p>
  
  <h2>Análise Detalhada</h2>
  <p>Responda à pergunta principal com profundidade.
  Para uma análise mais técnica com todos os testes, <a href="LINK_REVIEW">consulte nosso review detalhado</a>.</p>
  
  <h3>Subtópico importante</h3>
  <p>Desenvolva com exemplos.</p>
  
  <h2>Fatores Cruciais</h2>
  <p>Liste pontos importantes a considerar.</p>
  
  <h2>Comparações (se aplicável)</h2>
  <p>Compare com alternativas.</p>
  
  <h2>Conclusão</h2>
  <p><strong>Em resumo</strong>, após analisar todos os aspectos, [conclusão específica]. 
  <strong>Para tomar a melhor decisão</strong>, recomendo que você <a href="LINK_REVIEW">acesse nosso review completo</a> 
  onde detalhamos todos os testes práticos, comparativos e avaliações técnicas que realizamos.</p>
  
  <h2>FAQ - Perguntas Frequentes</h2>
  <div class="faq-item">
    <h3>Este artigo substitui o review completo?</h3>
    <p>Não! Este artigo foca em aspectos específicos. Para uma análise completa, 
    <a href="LINK_REVIEW">veja nosso review detalhado</a> com todos os testes e avaliações.</p>
  </div>
  <div class="faq-item">
    <h3>Onde posso ver os testes práticos?</h3>
    <p>Todos os testes práticos, comparações e análises técnicas estão no 
    <a href="LINK_REVIEW">nosso review principal</a>.</p>
  </div>
  <div class="faq-item">
    <h3>Vocês recomendam a compra?</h3>
    <p>A recomendação final com prós, contras e alternativas está no 
    <a href="LINK_REVIEW">review completo</a>.</p>
  </div>
  
  <div class="cta-final">
    <h3>Quer Saber Todos os Detalhes?</h3>
    <p>Para uma análise completa com todos os testes, fotos exclusivas e avaliação técnica detalhada, 
    <a href="LINK_REVIEW" class="btn-review">Leia nosso Review Completo</a></p>
  </div>
</article>

📊 FORMATO DE SAÍDA:
TITLE:
<título otimizado para SEO>

DESCRIPTION:
<meta description otimizada com CTA para review>

ARTICLE:
<conteúdo completo do article como mostrado acima>
"""

def calcular_tempo_leitura(texto):
    """Calcula tempo estimado de leitura (palavras/200)"""
    palavras = len(texto.split())
    minutos = max(7, palavras // 200)
    return f"{minutos} min"

def criar_sidebar_satelite(categoria, produto_slug, produto_nome, tipo_satelite, outros_satelites, link_review):
    """Cria sidebar personalizada para artigos satélite"""
    
    links_satelites = ""
    for sat in outros_satelites:
        if sat['slug'] != tipo_satelite['slug']:
            links_satelites += f'<li><a href="../{sat["slug_completo"]}/index.html">{sat["nome"]}</a></li>\n'
    
    sidebar = f'''<aside class="sidebar">
    <div class="widget">
        <h3><i class="fas fa-info-circle"></i> Informações</h3>
        <ul class="site-links">
            <li><a href="../../sobre-nos.html">Sobre Nós</a></li>
            <li><a href="../../politica-de-privacidade.html">Política de Privacidade</a></li>
            <li><a href="../../contato.html">Contato</a></li>
        </ul>
    </div>

    <div class="widget">
        <h3><i class="fas fa-link"></i> Mais {categoria.title()}</h3>
        <p><a href="{link_review}"><strong>📋 Review Principal</strong></a></p>
        {links_satelites if links_satelites else ''}
    </div>
    
    <div class="widget">
        <h3><i class="fas fa-star"></i> Por que Escolher a Gente?</h3>
        <ul class="benefits-list">
            <li>✅ Reviews honestos e imparciais</li>
            <li>✅ Análises detalhadas e aprofundadas</li>
            <li>✅ Guias especializados</li>
            <li>✅ Conteúdo 100% informativo</li>
        </ul>
    </div>
</aside>'''
    
    return sidebar

def processar_resposta_ia(resultado, review_url, produto_slug, produto_nome):
    """Processa a resposta da IA e garante links para o review"""
    
    # Extrai título e description
    titulo_match = re.search(r"TITLE:\s*(.+?)(?:\n|$)", resultado, re.IGNORECASE | re.MULTILINE)
    desc_match = re.search(r"DESCRIPTION:\s*(.+?)(?:\n|$)", resultado, re.IGNORECASE | re.MULTILINE)
    
    # Encontra o conteúdo do article
    artigo_conteudo = None
    article_match = re.search(r"<article[^>]*>.*?</article>", resultado, re.IGNORECASE | re.DOTALL)
    
    if article_match:
        artigo_conteudo = article_match.group(0)
    else:
        # Tenta encontrar conteúdo depois de ARTICLE:
        article_start = resultado.find("ARTICLE:")
        if article_start != -1:
            artigo_conteudo = resultado[article_start + 8:].strip()
            if not artigo_conteudo.startswith('<article'):
                artigo_conteudo = f'<article class="content">\n{artigo_conteudo}\n</article>'
    
    if not artigo_conteudo:
        return None, None, None
    
    # Garante links para o review
    link_review = review_url
    
    # Conta quantos links tem antes de adicionar
    links_antes = len(re.findall(r'href\s*=\s*["\'][^"\']*review[^"\']*["\']', artigo_conteudo, re.IGNORECASE))
    
    # Se não tem links suficientes, adiciona
    if links_antes < 3:
        # Adiciona link na introdução
        if '<h2>Introdução' in artigo_conteudo:
            intro_start = artigo_conteudo.find('<h2>Introdução')
            if intro_start != -1:
                first_p = artigo_conteudo.find('<p>', intro_start)
                if first_p != -1:
                    primeiro_paragrafo = artigo_conteudo.find('</p>', first_p)
                    if primeiro_paragrafo != -1:
                        link_text = f' Para ver nossa análise completa com todos os testes, <a href="{link_review}">acesse o review detalhado</a>.'
                        artigo_conteudo = artigo_conteudo[:primeiro_paragrafo] + link_text + artigo_conteudo[primeiro_paragrafo:]
        
        # Adiciona link em subtítulos
        for h2_tag in ['<h2>', '</h2>']:
            if h2_tag in artigo_conteudo:
                h2_pos = artigo_conteudo.find(h2_tag)
                if h2_pos != -1:
                    next_p = artigo_conteudo.find('<p>', h2_pos)
                    if next_p != -1:
                        p_end = artigo_conteudo.find('</p>', next_p)
                        if p_end != -1:
                            link_text = f' Confira todos os detalhes no <a href="{link_review}">nosso review principal</a>.'
                            artigo_conteudo = artigo_conteudo[:p_end] + link_text + artigo_conteudo[p_end:]
                            break
    
    # Substitui placeholder LINK_REVIEW pelo link real
    artigo_conteudo = artigo_conteudo.replace('LINK_REVIEW', link_review)
    
    # Título e description
    titulo = titulo_match.group(1).strip() if titulo_match else ""
    descricao = desc_match.group(1).strip() if desc_match else f"Descubra se {produto_nome} vale a pena. Análise completa. Leia nosso review detalhado para mais informações."
    
    # Limpa marcações do markdown
    titulo = re.sub(r'\*\*(.*?)\*\*', r'\1', titulo)
    descricao = re.sub(r'\*\*(.*?)\*\*', r'\1', descricao)
    
    # Remove HTML do título se houver
    titulo = re.sub(r'<[^>]+>', '', titulo)
    
    # Garante CTA na description
    if "review" not in descricao.lower() and "leia" not in descricao.lower():
        descricao += f" Leia nosso review completo do {produto_nome} para análise detalhada."
    
    # Limita description a 160 caracteres
    if len(descricao) > 160:
        descricao = descricao[:157] + "..."
    
    return titulo, descricao, artigo_conteudo

def criar_html_satelite(review_html, titulo, descricao, artigo_conteudo, categoria, produto_slug, produto_nome, tipo_satelite, outros_satelites, link_review):
    """Substitui apenas o conteúdo mantendo estrutura original"""
    
    # Data atual formatada
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Calcula tempo de leitura
    tempo_leitura = calcular_tempo_leitura(artigo_conteudo)
    
    # Atualiza meta dados no artigo
    artigo_conteudo = artigo_conteudo.replace("DATA_ATUAL", data_atual)
    artigo_conteudo = artigo_conteudo.replace("X min de leitura", tempo_leitura)
    artigo_conteudo = artigo_conteudo.replace("CATEGORIA", categoria.title())
    
    # Cria sidebar personalizada
    sidebar = criar_sidebar_satelite(categoria, produto_slug, produto_nome, tipo_satelite, outros_satelites, link_review)
    
    # Encontra o main container e substitui o conteúdo
    # Primeiro, extrai o cabeçalho até o início do <main>
    header_end = review_html.find('<main')
    header = review_html[:header_end]
    
    # Encontra o fim do main
    main_start = review_html.find('<main')
    main_end = review_html.find('</main>', main_start) + 7
    
    # Encontra o rodapé
    footer_start = review_html.find('<footer')
    footer = review_html[footer_start:]
    
    # Cria o novo main com estrutura correta
    novo_main = f'''<main class="container main-container">
        {artigo_conteudo}

        {sidebar}
    </main>'''
    
    # Reconstroi o HTML completo
    html_atualizado = header + novo_main + footer
    
    # Atualiza o título
    title_pattern = r'<title>[^<]+</title>'
    if re.search(title_pattern, html_atualizado, re.IGNORECASE):
        html_atualizado = re.sub(title_pattern, f'<title>{titulo}</title>', html_atualizado, flags=re.IGNORECASE)
    
    # Atualiza meta description
    desc_pattern = r'<meta\s+name="description"\s+content="[^"]*"'
    desc_match = re.search(desc_pattern, html_atualizado, re.IGNORECASE)
    if desc_match:
        nova_desc = f'<meta name="description" content="{descricao}"'
        html_atualizado = html_atualizado[:desc_match.start()] + nova_desc + html_atualizado[desc_match.end():]
    else:
        # Adiciona meta description se não existir
        head_end = html_atualizado.find('</head>')
        if head_end != -1:
            meta_desc = f'\n    <meta name="description" content="{descricao}">'
            html_atualizado = html_atualizado[:head_end] + meta_desc + html_atualizado[head_end:]
    
    # Atualiza og:title
    og_title_pattern = r'<meta\s+property="og:title"\s+content="[^"]*"'
    og_title_match = re.search(og_title_pattern, html_atualizado, re.IGNORECASE)
    if og_title_match:
        nova_og_title = f'<meta property="og:title" content="{titulo}"'
        html_atualizado = html_atualizado[:og_title_match.start()] + nova_og_title + html_atualizado[og_title_match.end():]
    
    # Atualiza og:description
    og_desc_pattern = r'<meta\s+property="og:description"\s+content="[^"]*"'
    og_desc_match = re.search(og_desc_pattern, html_atualizado, re.IGNORECASE)
    if og_desc_match:
        nova_og_desc = f'<meta property="og:description" content="{descricao}"'
        html_atualizado = html_atualizado[:og_desc_match.start()] + nova_og_desc + html_atualizado[og_desc_match.end():]
    
    # Atualiza twitter:title
    twitter_title_pattern = r'<meta\s+name="twitter:title"\s+content="[^"]*"'
    twitter_title_match = re.search(twitter_title_pattern, html_atualizado, re.IGNORECASE)
    if twitter_title_match:
        nova_twitter_title = f'<meta name="twitter:title" content="{titulo}"'
        html_atualizado = html_atualizado[:twitter_title_match.start()] + nova_twitter_title + html_atualizado[twitter_title_match.end():]
    
    # Atualiza twitter:description
    twitter_desc_pattern = r'<meta\s+name="twitter:description"\s+content="[^"]*"'
    twitter_desc_match = re.search(twitter_desc_pattern, html_atualizado, re.IGNORECASE)
    if twitter_desc_match:
        nova_twitter_desc = f'<meta name="twitter:description" content="{descricao}"'
        html_atualizado = html_atualizado[:twitter_desc_match.start()] + nova_twitter_desc + html_atualizado[twitter_desc_match.end():]
    
    # Remove ofertas e widgets de afiliados da sidebar
    html_atualizado = re.sub(r'<div class="widget">\s*<h3>.*?Oferta.*?</h3>.*?</div>', '', html_atualizado, flags=re.DOTALL | re.IGNORECASE)
    html_atualizado = re.sub(r'<a[^>]*class="[^"]*btn-sidebar[^"]*"[^>]*>.*?</a>', '', html_atualizado, flags=re.DOTALL)
    
    return html_atualizado

def atualizar_sitemap(categoria, produto_slug, tipo_satelite):
    """Atualiza o sitemap.xml com o novo artigo satélite"""
    
    if not SITEMAP_PATH.exists():
        print("   ⚠️ Sitemap não encontrado, criando novo...")
        criar_sitemap_inicial()
    
    try:
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()
        
        # Namespace do sitemap
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # URL do artigo satélite
        url_satelite = f"https://topofertas.reviewnexus.blog/{categoria}/{produto_slug}-{tipo_satelite['slug']}/"
        
        # Verifica se já existe
        urls_existentes = root.findall('.//ns:loc', ns)
        for url_elem in urls_existentes:
            if url_satelite in url_elem.text:
                print(f"   🔍 URL já existe no sitemap")
                return
        
        # Cria novo elemento URL
        url_element = ET.SubElement(root, 'url')
        
        loc = ET.SubElement(url_element, 'loc')
        loc.text = url_satelite
        
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = datetime.now().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = "monthly"
        
        priority = ET.SubElement(url_element, 'priority')
        priority.text = "0.7"
        
        # Salva o sitemap
        tree.write(SITEMAP_PATH, encoding='utf-8', xml_declaration=True)
        print(f"   ✅ Sitemap atualizado")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao atualizar sitemap: {e}")

def criar_sitemap_inicial():
    """Cria um sitemap.xml inicial"""
    
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    tree = ET.ElementTree(urlset)
    
    # Adiciona páginas principais
    paginas_principais = [
        "https://topofertas.reviewnexus.blog/",
        "https://topofertas.reviewnexus.blog/sobre-nos/",
        "https://topofertas.reviewnexus.blog/contato/",
        "https://topofertas.reviewnexus.blog/politica-privacidade/"
    ]
    
    for pagina in paginas_principais:
        url_element = ET.SubElement(urlset, 'url')
        
        loc = ET.SubElement(url_element, 'loc')
        loc.text = pagina
        
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = datetime.now().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = "weekly"
        
        priority = ET.SubElement(url_element, 'priority')
        priority.text = "1.0" if pagina.endswith('/') else "0.8"
    
    # Formatação bonita
    ET.indent(tree, space="  ", level=0)
    
    # Salva
    with open(SITEMAP_PATH, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding='utf-8')
    
    print("   ✅ Sitemap inicial criado")

def verificar_qualidade_artigo(caminho_artigo):
    """Verifica a qualidade de um artigo existente"""
    
    try:
        with open(caminho_artigo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        problemas = []
        
        # Verifica tamanho
        palavras = len(conteudo.split())
        if palavras < 1500:
            problemas.append(f"Artigo muito curto ({palavras} palavras)")
        
        # Verifica links para review
        links_review = len(re.findall(r'href=["\'][^"\']*review[^"\']*["\']', conteudo, re.IGNORECASE))
        if links_review < 3:
            problemas.append(f"Poucos links para review ({links_review})")
        
        # Verifica FAQ
        if 'faq' not in conteudo.lower() and 'perguntas frequentes' not in conteudo.lower():
            problemas.append("FAQ ausente")
        
        # Verifica CTA final
        if 'btn-review' not in conteudo and 'Leia nosso Review' not in conteudo:
            problemas.append("CTA final ausente")
        
        return problemas if problemas else ["Artigo OK"]
        
    except Exception as e:
        return [f"Erro na verificação: {e}"]

def corrigir_artigo_existente(caminho_artigo, review_url, produto_nome):
    """Corrige um artigo existente que tem problemas"""
    
    print(f"\n   🔧 Corrigindo artigo existente...")
    
    try:
        with open(caminho_artigo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        # Extrai título atual
        title_match = re.search(r'<title>(.*?)</title>', conteudo, re.IGNORECASE)
        titulo_atual = title_match.group(1) if title_match else ""
        
        # Conta links atuais
        links_atuais = len(re.findall(rf'href=["\'][^"\']*{re.escape(review_url)}[^"\']*["\']', conteudo))
        
        # Adiciona links se necessário
        if links_atuais < 3:
            # Adiciona link na conclusão
            conclusao_pattern = r'<h2>Conclusão</h2>.*?</article>'
            conclusao_match = re.search(conclusao_pattern, conteudo, re.IGNORECASE | re.DOTALL)
            
            if conclusao_match:
                conclusao_text = conclusao_match.group(0)
                cta_text = f'''<div class="cta-final">
    <h3>Quer Saber Todos os Detalhes?</h3>
    <p>Para uma análise completa com todos os testes, fotos exclusivas e avaliação técnica detalhada, 
    <a href="{review_url}" class="btn-review">Leia nosso Review Completo</a></p>
</div>'''
                
                # Insere antes do fechamento do article
                if '</article>' in conclusao_text:
                    nova_conclusao = conclusao_text.replace('</article>', f'{cta_text}\n</article>')
                    conteudo = conteudo.replace(conclusao_text, nova_conclusao)
        
        # Salva correção
        with open(caminho_artigo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        
        print(f"   ✅ Artigo corrigido")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao corrigir: {e}")
        return False

def processar_review(caminho_review, opcao_correcao=False):
    """Processa um review e cria artigos satélite"""
    
    try:
        with open(caminho_review, "r", encoding="utf-8") as f:
            review_html = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler review: {e}")
        return
    
    caminho_rel = Path(caminho_review).relative_to(DOCS_DIR)
    partes = caminho_rel.parts
    
    if len(partes) != 3:
        print(f"⚠️ Pula: {caminho_rel} - estrutura inválida")
        return
    
    categoria = partes[0]
    produto_slug = partes[1]
    
    # Ignora pastas especiais
    pastas_ignorar = ['includes', 'sobre-nos', 'contato', 'politica-privacidade', 
                     'css', 'js', 'img', 'assets', 'index.html']
    if categoria.lower() in pastas_ignorar or produto_slug.lower() in pastas_ignorar:
        print(f"⚠️ Pula: {caminho_rel} - pasta ignorada")
        return
    
    # Extrai nome do produto
    title_match = re.search(r"<title>(.*?)</title>", review_html, re.IGNORECASE)
    if title_match:
        produto_nome = title_match.group(1).strip()
        produto_nome = re.sub(r'\s*-\s*Review.*$', '', produto_nome, flags=re.IGNORECASE)
        produto_nome = re.sub(r'\s*\|.*$', '', produto_nome).strip()
    else:
        produto_nome = produto_slug.replace("-", " ").title()
    
    ano_atual = time.strftime("%Y")
    link_review = f"../{produto_slug}/index.html"
    
    print(f"\n🎯 PROCESSANDO: {produto_nome}")
    print(f"   📁 Categoria: {categoria}")
    print(f"   📋 Review: {produto_slug}/index.html")
    
    # Verifica satélites existentes
    satelites_existentes = []
    satelites_info = []
    
    for satelite in SATELLITE_TYPES:
        slug_completo = f"{produto_slug}-{satelite['slug']}"
        pasta_satelite = DOCS_DIR / categoria / slug_completo
        arquivo_satelite = pasta_satelite / "index.html"
        
        info = {
            'tipo': satelite['nome'],
            'slug': satelite['slug'],
            'slug_completo': slug_completo,
            'caminho': arquivo_satelite,
            'existe': arquivo_satelite.exists()
        }
        
        if info['existe']:
            satelites_existentes.append(satelite['nome'])
            # Verifica qualidade
            problemas = verificar_qualidade_artigo(arquivo_satelite)
            info['problemas'] = problemas
            info['precisa_correcao'] = any("Artigo muito curto" in p or "Poucos links" in p or "CTA final ausente" in p for p in problemas)
        
        satelites_info.append(info)
    
    print(f"   📊 Satélites existentes: {len(satelites_existentes)}/{len(SATELLITE_TYPES)}")
    
    # Mostra status dos existentes
    for info in satelites_info:
        if info['existe']:
            status = "✅ OK" if info['problemas'] == ["Artigo OK"] else "⚠️ Problemas"
            print(f"      • {info['tipo']}: {status}")
            if info['problemas'] != ["Artigo OK"]:
                for prob in info['problemas']:
                    print(f"        ⚠️ {prob}")
    
    # Opções de correção
    if opcao_correcao and satelites_existentes:
        print(f"\n   🔧 OPÇÕES DE CORREÇÃO:")
        
        for i, info in enumerate(satelites_info, 1):
            if info['existe'] and info['precisa_correcao']:
                print(f"      {i}. Corrigir: {info['tipo']}")
        
        print(f"      A. Corrigir todos com problemas")
        print(f"      N. Não corrigir, apenas criar novos")
        
        escolha_correcao = input("\n   Escolha: ").strip().upper()
        
        if escolha_correcao == 'A':
            for info in satelites_info:
                if info['existe'] and info['precisa_correcao']:
                    corrigir_artigo_existente(info['caminho'], link_review, produto_nome)
        elif escolha_correcao.isdigit():
            idx = int(escolha_correcao) - 1
            if 0 <= idx < len(satelites_info):
                info = satelites_info[idx]
                if info['existe'] and info['precisa_correcao']:
                    corrigir_artigo_existente(info['caminho'], link_review, produto_nome)
    
    # Se todos já existem e não quer corrigir, pergunta
    if len(satelites_existentes) >= len(SATELLITE_TYPES) and not opcao_correcao:
        print(f"\n   ⚠️ Todos os satélites já existem")
        resposta = input("   Deseja recriar algum? (S/N): ").strip().upper()
        
        if resposta == 'S':
            print("\n   Qual satélite recriar?")
            for i, sat in enumerate(SATELLITE_TYPES, 1):
                print(f"      {i}. {sat['nome']}")
            print(f"      T. Todos")
            print(f"      N. Nenhum (pular)")
            
            escolha = input("\n   Escolha: ").strip().upper()
            
            if escolha == 'T':
                # Remove todos para recriar
                for sat in SATELLITE_TYPES:
                    slug_completo = f"{produto_slug}-{sat['slug']}"
                    pasta_satelite = DOCS_DIR / categoria / slug_completo
                    if pasta_satelite.exists():
                        shutil.rmtree(pasta_satelite)
                        print(f"   🗑️ Removido: {sat['nome']}")
            elif escolha.isdigit():
                idx = int(escolha) - 1
                if 0 <= idx < len(SATELLITE_TYPES):
                    sat = SATELLITE_TYPES[idx]
                    slug_completo = f"{produto_slug}-{sat['slug']}"
                    pasta_satelite = DOCS_DIR / categoria / slug_completo
                    if pasta_satelite.exists():
                        shutil.rmtree(pasta_satelite)
                        print(f"   🗑️ Removido: {sat['nome']}")
            else:
                print(f"   ⏸️ Mantendo existentes, pulando...")
                return
        else:
            print(f"   ⏸️ Mantendo existentes, pulando...")
            return
    
    # Prepara lista de outros satélites para sidebar
    outros_satelites_info = []
    for sat in SATELLITE_TYPES:
        outros_satelites_info.append({
            'slug': sat['slug'],
            'slug_completo': f"{produto_slug}-{sat['slug']}",
            'nome': sat['nome']
        })
    
    # Cria cada satélite
    satelites_criados = 0
    for satelite in SATELLITE_TYPES:
        slug_completo = f"{produto_slug}-{satelite['slug']}"
        pasta_destino = DOCS_DIR / categoria / slug_completo
        arquivo_final = pasta_destino / "index.html"
        
        # Se já existe e não estamos em modo correção, pula
        if arquivo_final.exists() and not opcao_correcao:
            continue
        
        print(f"\n   🛰️ Criando: {satelite['nome']}")
        print(f"   📂 Pasta: {categoria}/{slug_completo}/")
        
        # Prompt personalizado
        prompt_personalizado = PROMPT_SATELITE + f"""

🎯 INFORMAÇÕES ESPECÍFICAS:

PRODUTO: {produto_nome}
CATEGORIA: {categoria}
TIPO DE ARTIGO: {satelite['intent']}
FOCO: {satelite['focus']}
ANO: {ano_atual}

📎 LINK DO REVIEW (USE 3-4 VEZES):
<a href="{link_review}">Review completo do {produto_nome}</a>

🧠 INSTRUÇÕES CRÍTICAS:
1. INCLUA pelo menos 3 links diferentes para o review
2. Use CTA claro na conclusão (com class="btn-review")
3. Mencione o review no FAQ
4. Texto mínimo 1800 palavras
5. NÃO seja comercial - seja informativo
6. INCLUA um CTA final com a classe "cta-final" e "btn-review"

CRIE um artigo ORIGINAL sobre "{satelite['intent'].lower()}" para {produto_nome}.
O artigo deve naturalmente levar o leitor ao review principal.
"""
        
        try:
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "Você é um redator especialista em conteúdo informativo para blogs. Seu foco é educar e informar, não vender. Crie conteúdo que naturalmente leve ao review principal."},
                    {"role": "user", "content": prompt_personalizado}
                ],
                "temperature": 0.7,
                "max_tokens": 6000
            }
            
            print(f"   🤖 Chamando IA...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=HEADERS,
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            resultado = response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"   ❌ Erro na IA: {e}")
            continue
        
        # Salva resposta bruta
        debug_dir = Path("debug")
        debug_dir.mkdir(exist_ok=True)
        debug_file = debug_dir / f"{slug_completo}_raw.txt"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(resultado)
        
        # Processa resposta
        titulo, descricao, artigo_conteudo = processar_resposta_ia(resultado, link_review, produto_slug, produto_nome)
        
        if not artigo_conteudo:
            print(f"   ❌ Não extraiu conteúdo válido")
            
            # Tenta fallback
            print(f"   🔍 Tentando fallback...")
            try:
                # Extrai conteúdo da resposta bruta
                artigo_conteudo = resultado
                
                # Adiciona estrutura básica
                artigo_conteudo = f'''<article class="content">
    <h1>{produto_nome} {satelite['nome']} - Análise Completa {ano_atual}</h1>
    
    <div class="article-meta">
        <span><i class="far fa-calendar-alt"></i> DATA_ATUAL</span>
        <span><i class="far fa-user"></i> Equipe TechReviews</span>
        <span><i class="far fa-clock"></i> X min de leitura</span>
        <span><i class="fas fa-tag"></i> CATEGORIA</span>
    </div>
    
    {artigo_conteudo}
    
    <div class="cta-final">
        <h3>Quer Saber Todos os Detalhes?</h3>
        <p>Para uma análise completa com todos os testes, fotos exclusivas e avaliação técnica detalhada, 
        <a href="{link_review}" class="btn-review">Leia nosso Review Completo</a></p>
    </div>
</article>'''
                
                titulo = satelite['title_hint'].replace("{PRODUTO}", produto_nome).replace("{CATEGORIA}", categoria).replace("{ANO_ATUAL}", ano_atual)
                descricao = f"Análise completa sobre {produto_nome}. Descubra se vale a pena. Leia nosso review detalhado para mais informações."
                
            except Exception as e2:
                print(f"   ❌ Fallback falhou: {e2}")
                continue
        
        # Garante título se vazio
        if not titulo or len(titulo) < 10:
            titulo = satelite['title_hint'].replace("{PRODUTO}", produto_nome).replace("{CATEGORIA}", categoria).replace("{ANO_ATUAL}", ano_atual)
        
        # Limpa título
        titulo = re.sub(r'\*\*(.*?)\*\*', r'\1', titulo).strip()
        titulo = re.sub(r'<[^>]+>', '', titulo)
        
        # Remove asteriscos do início
        titulo = re.sub(r'^\*\s*', '', titulo)
        
        print(f"   📝 Título: {titulo[:80]}...")
        print(f"   📊 Conteúdo: {len(artigo_conteudo)} caracteres")
        
        # Conta links para review
        links_review = len(re.findall(rf'href=["\'][^"\']*{re.escape(link_review)}[^"\']*["\']', artigo_conteudo))
        print(f"   📎 Links para review: {links_review}")
        
        # Verifica se tem CTA final
        tem_cta_final = 'cta-final' in artigo_conteudo.lower() or 'btn-review' in artigo_conteudo.lower()
        print(f"   🎯 CTA final: {'✅ Sim' if tem_cta_final else '❌ Não'}")
        
        # Cria HTML completo
        html_final = criar_html_satelite(review_html, titulo, descricao, artigo_conteudo, 
                                        categoria, produto_slug, produto_nome, satelite, outros_satelites_info, link_review)
        
        if not html_final:
            print(f"   ❌ Erro ao criar HTML")
            continue
        
        # Cria diretório e salva
        pasta_destino.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(arquivo_final, "w", encoding="utf-8") as f:
                f.write(html_final)
            
            # Verifica tamanho
            with open(arquivo_final, "r", encoding="utf-8") as f:
                conteudo = f.read()
                palavras = len(conteudo.split())
            
            print(f"   ✅ SALVO: {slug_completo}/index.html")
            print(f"   📈 Estatísticas: {palavras} palavras, {links_review} links para review")
            
            # Atualiza sitemap
            atualizar_sitemap(categoria, produto_slug, satelite)
            
            satelites_criados += 1
            
        except Exception as e:
            print(f"   ❌ Erro ao salvar: {e}")
            continue
        
        print(f"   ⏳ Aguardando 5 segundos...")
        time.sleep(5)
    
    return satelites_criados

def encontrar_reviews():
    """Encontra todos os reviews"""
    reviews = []
    
    pastas_ignorar = ['includes', 'sobre-nos', 'contato', 'politica-privacidade', 
                     'css', 'js', 'img', 'assets', 'index.html']
    
    print("🔍 Procurando reviews...")
    
    for categoria in os.listdir(DOCS_DIR):
        cat_path = DOCS_DIR / categoria
        
        if not cat_path.is_dir() or categoria.lower() in pastas_ignorar:
            continue
        
        print(f"   📂 Verificando categoria: {categoria}")
        
        for item in os.listdir(cat_path):
            item_path = cat_path / item
            
            if not item_path.is_dir() or item.lower() in pastas_ignorar:
                continue
            
            # Ignora satélites (contém qualquer slug de satélite)
            is_satelite = False
            for satelite in SATELLITE_TYPES:
                if satelite['slug'] in item:
                    is_satelite = True
                    break
            
            if is_satelite:
                continue
            
            index_path = item_path / "index.html"
            if index_path.exists() and item.lower() != categoria.lower():
                reviews.append({
                    'caminho': str(index_path),
                    'categoria': categoria,
                    'slug': item,
                    'nome': item.replace("-", " ").title()
                })
    
    return reviews

def mostrar_menu_avancado():
    """Mostra menu avançado de opções"""
    
    print("\n" + "="*70)
    print("🛠️ MENU AVANÇADO - GERENCIAMENTO COMPLETO")
    print("="*70)
    
    print("""
    1. 🔍 Listar todos os reviews encontrados
    2. 🛰️ Verificar qualidade dos satélites existentes
    3. 🔧 Corrigir satélites com problemas
    4. 🗑️ Remover satélites específicos
    5. 📊 Estatísticas completas do site
    6. 🔄 Atualizar sitemap com tudo
    7. 🚀 Criar novos satélites (modo normal)
    8. ❌ Sair
    """)
    
    escolha = input("Escolha uma opção (1-8): ").strip()
    
    return escolha

def executar_menu_avancado(escolha, reviews):
    """Executa a opção escolhida no menu avançado"""
    
    if escolha == '1':
        print(f"\n📋 LISTA DE REVIEWS ({len(reviews)} encontrados):")
        for i, review in enumerate(reviews, 1):
            print(f"   {i}. {review['nome']} ({review['categoria']})")
            print(f"      📁 {review['caminho']}")
        
        input("\nPressione Enter para continuar...")
        return True
        
    elif escolha == '2':
        print(f"\n🔍 VERIFICANDO QUALIDADE DOS SATÉLITES")
        
        total_satelites = 0
        problemas_encontrados = 0
        
        for categoria in os.listdir(DOCS_DIR):
            cat_path = DOCS_DIR / categoria
            
            if not cat_path.is_dir() or categoria in ['includes', 'css', 'js', 'img', 'assets']:
                continue
            
            for item in os.listdir(cat_path):
                item_path = cat_path / item
                
                if not item_path.is_dir():
                    continue
                
                # Verifica se é satélite
                is_satelite = False
                for satelite in SATELLITE_TYPES:
                    if satelite['slug'] in item:
                        is_satelite = True
                        break
                
                if is_satelite:
                    total_satelites += 1
                    arquivo = item_path / "index.html"
                    
                    if arquivo.exists():
                        problemas = verificar_qualidade_artigo(arquivo)
                        if problemas != ["Artigo OK"]:
                            problemas_encontrados += 1
                            print(f"\n   ⚠️ {categoria}/{item}/")
                            for prob in problemas:
                                print(f"      • {prob}")
        
        print(f"\n📊 RESUMO:")
        print(f"   Total de satélites: {total_satelites}")
        print(f"   Com problemas: {problemas_encontrados}")
        print(f"   OK: {total_satelites - problemas_encontrados}")
        
        input("\nPressione Enter para continuar...")
        return True
        
    elif escolha == '3':
        print(f"\n🔧 MODO CORREÇÃO DE SATÉLITES")
        print("Este modo corrige artigos existentes que têm problemas.")
        
        # Encontra reviews que têm satélites
        reviews_com_satelites = []
        
        for review in reviews:
            categoria = review['categoria']
            produto_slug = review['slug']
            
            tem_satelites = False
            for satelite in SATELLITE_TYPES:
                pasta_satelite = DOCS_DIR / categoria / f"{produto_slug}-{satelite['slug']}"
                if pasta_satelite.exists():
                    tem_satelites = True
                    break
            
            if tem_satelites:
                reviews_com_satelites.append(review)
        
        if not reviews_com_satelites:
            print("   ❓ Nenhum review com satélites encontrado.")
            input("\nPressione Enter para continuar...")
            return True
        
        print(f"\n📋 Reviews com satélites ({len(reviews_com_satelites)}):")
        for i, review in enumerate(reviews_com_satelites, 1):
            print(f"   {i}. {review['nome']}")
        
        escolha_review = input("\nEscolha o número do review (ou A para todos): ").strip().upper()
        
        if escolha_review == 'A':
            # Correção para todos
            for review in reviews_com_satelites:
                processar_review(review['caminho'], opcao_correcao=True)
        elif escolha_review.isdigit():
            idx = int(escolha_review) - 1
            if 0 <= idx < len(reviews_com_satelites):
                processar_review(reviews_com_satelites[idx]['caminho'], opcao_correcao=True)
        
        return True
        
    elif escolha == '4':
        print(f"\n🗑️ REMOVER SATÉLITES")
        print("CUIDADO: Esta ação não pode ser desfeita!")
        
        # Lista todos os satélites
        todos_satelites = []
        
        for categoria in os.listdir(DOCS_DIR):
            cat_path = DOCS_DIR / categoria
            
            if not cat_path.is_dir() or categoria in ['includes', 'css', 'js', 'img', 'assets']:
                continue
            
            for item in os.listdir(cat_path):
                item_path = cat_path / item
                
                if not item_path.is_dir():
                    continue
                
                # Verifica se é satélite
                is_satelite = False
                tipo_satelite = None
                for satelite in SATELLITE_TYPES:
                    if satelite['slug'] in item:
                        is_satelite = True
                        tipo_satelite = satelite['nome']
                        break
                
                if is_satelite:
                    todos_satelites.append({
                        'categoria': categoria,
                        'slug': item,
                        'tipo': tipo_satelite,
                        'caminho': item_path
                    })
        
        if not todos_satelites:
            print("   ❓ Nenhum satélite encontrado.")
            input("\nPressione Enter para continuar...")
            return True
        
        print(f"\n📋 Satélites encontrados ({len(todos_satelites)}):")
        for i, sat in enumerate(todos_satelites, 1):
            print(f"   {i}. {sat['categoria']}/{sat['slug']} ({sat['tipo']})")
        
        escolha = input("\nEscolha o número para remover (ou A para todos, N para cancelar): ").strip().upper()
        
        if escolha == 'A':
            confirmacao = input("Tem certeza que quer remover TODOS os satélites? (S/N): ").strip().upper()
            if confirmacao == 'S':
                for sat in todos_satelites:
                    shutil.rmtree(sat['caminho'])
                    print(f"   🗑️ Removido: {sat['categoria']}/{sat['slug']}")
        elif escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(todos_satelites):
                sat = todos_satelites[idx]
                confirmacao = input(f"Remover {sat['categoria']}/{sat['slug']}? (S/N): ").strip().upper()
                if confirmacao == 'S':
                    shutil.rmtree(sat['caminho'])
                    print(f"   🗑️ Removido: {sat['categoria']}/{sat['slug']}")
        
        return True
        
    elif escolha == '5':
        print(f"\n📊 ESTATÍSTICAS COMPLETAS DO SITE")
        
        total_reviews = len(reviews)
        total_satelites = 0
        total_palavras = 0
        categorias = {}
        
        # Conta por categoria
        for review in reviews:
            cat = review['categoria']
            if cat not in categorias:
                categorias[cat] = {'reviews': 0, 'satelites': 0}
            categorias[cat]['reviews'] += 1
        
        # Conta satélites
        for categoria in os.listdir(DOCS_DIR):
            cat_path = DOCS_DIR / categoria
            
            if not cat_path.is_dir() or categoria in ['includes', 'css', 'js', 'img', 'assets']:
                continue
            
            if categoria not in categorias:
                continue
            
            for item in os.listdir(cat_path):
                item_path = cat_path / item
                
                if not item_path.is_dir():
                    continue
                
                # Verifica se é satélite
                is_satelite = False
                for satelite in SATELLITE_TYPES:
                    if satelite['slug'] in item:
                        is_satelite = True
                        break
                
                if is_satelite:
                    total_satelites += 1
                    categorias[categoria]['satelites'] += 1
        
        print(f"\n👁️ VISÃO GERAL:")
        print(f"   📋 Total de reviews: {total_reviews}")
        print(f"   🛰️ Total de satélites: {total_satelites}")
        print(f"   ⚖️ Ratio: {total_satelites/total_reviews:.1f} satélites por review")
        
        print(f"\n📁 POR CATEGORIA:")
        for cat, stats in categorias.items():
            print(f"   📂 {cat}:")
            print(f"      • Reviews: {stats['reviews']}")
            print(f"      • Satélites: {stats['satelites']}")
            if stats['reviews'] > 0:
                print(f"      • Ratio: {stats['satelites']/stats['reviews']:.1f}")
        
        # Verifica sitemap
        if SITEMAP_PATH.exists():
            try:
                tree = ET.parse(SITEMAP_PATH)
                root = tree.getroot()
                urls = len(root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'))
                print(f"\n🗺️ SITEMAP:")
                print(f"   URLs no sitemap: {urls}")
                print(f"   URLs esperadas: {total_reviews + total_satelites + 4} (reviews + satélites + páginas)")
                if urls < (total_reviews + total_satelites):
                    print(f"   ⚠️ Sitemap está incompleto!")
                else:
                    print(f"   ✅ Sitemap está completo!")
            except:
                print(f"\n🗺️ SITEMAP: ⚠️ Erro ao ler sitemap")
        else:
            print(f"\n🗺️ SITEMAP: ❌ Arquivo não encontrado")
        
        input("\nPressione Enter para continuar...")
        return True
        
    elif escolha == '6':
        print(f"\n🔄 ATUALIZANDO SITEMAP COMPLETO")
        
        if not SITEMAP_PATH.exists():
            criar_sitemap_inicial()
        
        # Adiciona todos os reviews e satélites
        urls_adicionadas = 0
        
        try:
            tree = ET.parse(SITEMAP_PATH)
            root = tree.getroot()
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # URLs existentes
            urls_existentes = [elem.text for elem in root.findall('.//ns:loc', ns)]
            
            # Adiciona reviews
            for review in reviews:
                url_review = f"https://topofertas.reviewnexus.blog/{review['categoria']}/{review['slug']}/"
                
                if url_review not in urls_existentes:
                    url_element = ET.SubElement(root, 'url')
                    
                    loc = ET.SubElement(url_element, 'loc')
                    loc.text = url_review
                    
                    lastmod = ET.SubElement(url_element, 'lastmod')
                    lastmod.text = datetime.now().strftime("%Y-%m-%d")
                    
                    changefreq = ET.SubElement(url_element, 'changefreq')
                    changefreq.text = "monthly"
                    
                    priority = ET.SubElement(url_element, 'priority')
                    priority.text = "0.8"
                    
                    urls_adicionadas += 1
            
            # Adiciona satélites
            for categoria in os.listdir(DOCS_DIR):
                cat_path = DOCS_DIR / categoria
                
                if not cat_path.is_dir() or categoria in ['includes', 'css', 'js', 'img', 'assets']:
                    continue
                
                for item in os.listdir(cat_path):
                    item_path = cat_path / item
                    
                    if not item_path.is_dir():
                        continue
                    
                    # Verifica se é satélite
                    is_satelite = False
                    for satelite in SATELLITE_TYPES:
                        if satelite['slug'] in item:
                            is_satelite = True
                            break
                    
                    if is_satelite:
                        url_satelite = f"https://topofertas.reviewnexus.blog/{categoria}/{item}/"
                        
                        if url_satelite not in urls_existentes:
                            url_element = ET.SubElement(root, 'url')
                            
                            loc = ET.SubElement(url_element, 'loc')
                            loc.text = url_satelite
                            
                            lastmod = ET.SubElement(url_element, 'lastmod')
                            lastmod.text = datetime.now().strftime("%Y-%m-%d")
                            
                            changefreq = ET.SubElement(url_element, 'changefreq')
                            changefreq.text = "monthly"
                            
                            priority = ET.SubElement(url_element, 'priority')
                            priority.text = "0.7"
                            
                            urls_adicionadas += 1
            
            # Salva
            ET.indent(tree, space="  ", level=0)
            tree.write(SITEMAP_PATH, encoding='utf-8', xml_declaration=True)
            
            print(f"   ✅ Sitemap atualizado com {urls_adicionadas} novas URLs")
            
        except Exception as e:
            print(f"   ❌ Erro ao atualizar sitemap: {e}")
        
        input("\nPressione Enter para continuar...")
        return True
        
    elif escolha == '7':
        # Modo normal de criação
        return False
        
    elif escolha == '8':
        print("\n👋 Até logo!")
        exit(0)
        
    else:
        print("❌ Opção inválida")
        return True

def main():
    print("=" * 70)
    print("🚀 GERADOR DE ARTIGOS SATÉLITE - SISTEMA 11/10")
    print("=" * 70)
    print("📊 VERSÃO FINAL: Gestão completa com correções e sitemap automático")
    print("=" * 70)
    
    if not OPENROUTER_API_KEY:
        print("❌ ERRO: OPENROUTER_API_KEY não encontrada")
        print("🔑 Crie um arquivo .env com: OPENROUTER_API_KEY=sua_chave_aqui")
        exit(1)
    
    print("✅ API Key carregada do .env")
    print(f"📁 Diretório base: {DOCS_DIR}")
    print(f"🤖 Modelo: {MODEL}")
    print(f"🎯 Artigos por produto: {len(SATELLITE_TYPES)} (Otimizado)")
    print("🔑 Sistema 11/10 - Gestão completa com correções automáticas")
    
    # Cria pasta debug se não existir
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)
    
    # Verifica sitemap
    if not SITEMAP_PATH.exists():
        print("⚠️ Sitemap não encontrado, será criado automaticamente")
    
    # Menu principal
    print("\n" + "="*70)
    print("📋 MENU PRINCIPAL")
    print("="*70)
    print("1. 🚀 Modo Rápido (criar/atualizar satélites)")
    print("2. 🛠️ Modo Avançado (gerenciamento completo)")
    print("3. ❌ Sair")
    
    modo = input("\nEscolha o modo (1-3): ").strip()
    
    if modo == '3':
        print("👋 Até logo!")
        exit(0)
    
    # Encontra reviews
    reviews = encontrar_reviews()
    
    if not reviews:
        print("\n❌ Nenhum review encontrado na pasta docs/")
        print("🔑 Execute primeiro o gerador.py para criar reviews")
        exit(1)
    
    print(f"\n📈 {len(reviews)} reviews encontrados")
    
    if modo == '2':
        # Modo avançado
        while True:
            escolha = mostrar_menu_avancado()
            continuar_menu = executar_menu_avancado(escolha, reviews)
            if not continuar_menu:
                break  # Sai do menu avançado e vai para criação normal
    
    # Modo normal de criação
    print(f"\n📋 MENU DE REVIEWS DISPONÍVEIS:")
    for i, review in enumerate(reviews, 1):
        print(f"   {i}. {review['nome']} ({review['categoria']})")
    
    print(f"\n🔑 Opções:")
    print(f"   • Digite números separados por vírgula (ex: 1,3,5)")
    print(f"   • Digite 'T' para todos os {len(reviews)} reviews")
    print(f"   • Digite 'N' para cancelar")
    
    escolha_reviews = input("\nQuais reviews processar? ").strip().upper()
    
    if escolha_reviews == 'N':
        print("❌ Processo cancelado")
        exit(0)
    elif escolha_reviews == 'T':
        reviews_selecionados = reviews
    else:
        # Processa seleção por números
        indices = []
        for parte in escolha_reviews.split(','):
            parte = parte.strip()
            if parte.isdigit():
                idx = int(parte) - 1
                if 0 <= idx < len(reviews):
                    indices.append(idx)
        
        if not indices:
            print("❌ Nenhum review válido selecionado")
            exit(1)
        
        reviews_selecionados = [reviews[i] for i in indices]
    
    print(f"\n✅ Processando {len(reviews_selecionados)} reviews selecionados")
    
    # Processa cada review
    total_criados = 0
    total_corrigidos = 0
    
    for i, review in enumerate(reviews_selecionados, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(reviews_selecionados)}] PROCESSANDO REVIEW")
        print(f"Produto: {review['nome']}")
        print(f"Categoria: {review['categoria']}")
        print(f"{'='*70}")
        
        criados = processar_review(review['caminho'])
        if criados:
            total_criados += criados
        
        print(f"   📊 Satélites processados: {criados if criados else 0}")
    
    # Relatório final
    print(f"\n{'='*70}")
    print("🎉 GERADOR DE SATÉLITES CONCLUÍDO - SISTEMA 11/10!")
    print("=" * 70)
    
    print(f"\n📊 RELATÓRIO FINAL:")
    print(f"   Reviews processados: {len(reviews_selecionados)}")
    print(f"   Artigos satélite criados: {total_criados}")
    if len(reviews_selecionados) > 0:
        print(f"   Média: {total_criados/len(reviews_selecionados):.1f} por review")
    
    # Verifica sitemap final
    if SITEMAP_PATH.exists():
        try:
            tree = ET.parse(SITEMAP_PATH)
            root = tree.getroot()
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            total_urls = len(root.findall('.//ns:loc', ns))
            print(f"   URLs no sitemap: {total_urls}")
        except:
            print(f"   ⚠️ Não foi possível verificar sitemap")
    else:
        print(f"   ❌ Sitemap não encontrado após processo")
    
    # Mostra estrutura criada
    print(f"\n📁 ESTRUTURA CRIADA/ATUALIZADA:")
    categorias_com_satelites = []
    
    for categoria in os.listdir(DOCS_DIR):
        cat_path = DOCS_DIR / categoria
        if cat_path.is_dir() and categoria not in ['includes', 'css', 'js', 'img', 'assets']:
            satelites_cat = []
            for item in os.listdir(cat_path):
                item_path = cat_path / item
                if item_path.is_dir() and any(satelite['slug'] in item for satelite in SATELLITE_TYPES):
                    if (item_path / "index.html").exists():
                        satelites_cat.append(item)
            
            if satelites_cat:
                categorias_com_satelites.append(categoria)
                print(f"   📁 {categoria}/")
                for sat in satelites_cat:
                    print(f"      └── {sat}/")
    
    if not categorias_com_satelites:
        print("   ❓ Nenhum artigo satélite foi criado nesta execução.")
    
    print("\n" + "=" * 70)
    print("🏆 POR QUE É SISTEMA 11/10:")
    print("=" * 70)
    print("""
    1. ✅ GESTÃO COMPLETA - Cria, verifica, corrige e remove satélites
    2. ✅ SITEMAP AUTOMÁTICO - Atualiza automaticamente com novas URLs
    3. ✅ QUALIDADE GARANTIDA - Verifica tamanho, links e estrutura
    4. ✅ CORREÇÕES INTELIGENTES - Corrige artigos com problemas
    5. ✅ MENU AVANÇADO - Controle total sobre todos os satélites
    6. ✅ SEO PERFEITO - Artigos com 1800+ palavras otimizados
    7. ✅ LINKS INTERNOS - Múltiplos CTAs para o review principal
    8. ✅ CONTEÚDO ORIGINAL - IA instruída para não copiar do review
    9. ✅ ESTATÍSTICAS - Relatórios detalhados do site completo
    10.✅ CONVERSÃO OTIMIZADA - CTAs claros em múltiplos pontos
    11.✅ INTERFACE AMIGÁVEL - Fácil de usar e gerenciar
    """)
    
    print("\n✅ Processo completo! Sistema pronto para escala.")
    print("👁️ Sitemap atualizado e pronto para indexação no Google!")
    print("🔑 Dica: Use 'python gerador_satelites.py' novamente para")
    print("       verificar qualidade ou corrigir artigos existentes.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Processo interrompido pelo usuário")
        exit(0)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        print("🔑 Verifique se o servidor da IA está acessível")
        exit(1)