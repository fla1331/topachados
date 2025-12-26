#!/usr/bin/env python3
"""
GERADOR DE ARTIGOS SATÉLITE - Sistema de Conteúdo Secundário
Cria artigos de nicho focados em dor/solução para cada produto
"""

import os
import re
import requests
import time
import unicodedata
import json
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configurações
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat"
DOCS_DIR = Path.cwd() / "docs"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Gerador Satélites v1.0"
}

# Tipos de artigos satélite
SATELLITE_TYPES = [
    {
        "slug": "vale-a-pena",
        "nome": "Vale a Pena?",
        "intent": "Avaliar se o produto realmente compensa a compra",
        "title_hint": "{PRODUTO} Vale a Pena? Análise Honesta e Detalhada",
        "focus": "custo-benefício, retorno sobre investimento, comparativo com alternativas"
    },
    {
        "slug": "e-bom",
        "nome": "É Bom?",
        "intent": "Resolver dúvida sobre qualidade e performance do produto",
        "title_hint": "{PRODUTO} é Bom? Prós, Contras e Opinião Real",
        "focus": "qualidade, durabilidade, experiência do usuário, pontos fortes e fracos"
    },
    {
        "slug": "como-escolher",
        "nome": "Como Escolher",
        "intent": "Educar o leitor para tomar a melhor decisão de compra",
        "title_hint": "Como Escolher {CATEGORIA} Ideal em {ANO_ATUAL}",
        "focus": "critérios de escolha, fatores importantes, o que observar, dicas práticas"
    },
    {
        "slug": "funciona-mesmo",
        "nome": "Funciona Mesmo?",
        "intent": "Responder ceticismo e dúvidas sobre eficácia do produto",
        "title_hint": "{PRODUTO} Funciona Mesmo? Verdade Revelada",
        "focus": "efetividade, resultados reais, ciência por trás, depoimentos"
    },
    {
        "slug": "melhor-marca",
        "nome": "Melhor Marca",
        "intent": "Comparar marcas e modelos dentro da categoria",
        "title_hint": "Qual a Melhor Marca de {CATEGORIA}? Comparativo {ANO_ATUAL}",
        "focus": "comparação entre marcas, diferenciais, mercado, recomendações"
    }
]

PROMPT_SATELITE = """Você é um redator especialista em criar conteúdo informativo e educativo para blogs.

Crie UM artigo satélite completo e aprofundado.

🎯 OBJETIVO DO ARTIGO SATÉLITE:
- Gerar tráfego orgânico de busca
- Responder dúvidas específicas do usuário
- Educar e informar, não vender diretamente
- Conduzir naturalmente para o review principal

📋 REGRAS:
- Linguagem natural, humana e envolvente
- Texto ORIGINAL, não copie do review
- Profundidade: mínimo 1200 palavras
- Estrutura clara com subtítulos
- Não mencionar afiliados, comissões ou vendas
- Não criar CTAs de compra explícitos
- Foco em informação e educação

🔗 LINKS (INSERIR NATURALMENTE):
- 1-2 links internos para o review principal (contextualizados)
- 1 link externo para fonte confiável (Wikipedia, site oficial, estudo)
- Links devem fazer sentido no contexto

📝 ESTRUTURA SUGERIDA:
1. Introdução (contextualiza a dúvida/dor)
2. Importância do tema (por que isso importa)
3. Análise detalhada (respondendo a pergunta central)
4. Fatores a considerar (itens importantes)
5. Comparações (se aplicável)
6. Conclusão (resumo e próximo passo)
7. FAQ (3-5 perguntas frequentes)

📌 FORMATO DE SAÍDA:
TITLE:
<título otimizado>

DESCRIPTION:
<meta description atrativa>

ARTICLE:
<article>
  <h2>Introdução</h2>
  <p>...</p>
  
  <h2>Análise Detalhada</h2>
  <p>...</p>
  
  <h2>Fatores Importantes</h2>
  <p>...</p>
  
  <h2>Conclusão</h2>
  <p>...</p>
  
  <h2>FAQ</h2>
  <p><strong>Pergunta 1?</strong> Resposta...</p>
</article>
"""

def slugify(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9\s-]", "", texto).lower()
    return re.sub(r"\s+", "-", texto).strip("-")

def link_externo_por_categoria(categoria):
    """Retorna link externo apropriado para a categoria"""
    links = {
        "smartphones": "https://pt.wikipedia.org/wiki/Smartphone",
        "eletrodomesticos": "https://pt.wikipedia.org/wiki/Eletrodoméstico",
        "computadores": "https://pt.wikipedia.org/wiki/Computador",
        "games": "https://pt.wikipedia.org/wiki/Videojogo",
        "healthcare": "https://pt.wikipedia.org/wiki/Saúde",
        "beleza": "https://pt.wikipedia.org/wiki/Cosmético",
        "fitness": "https://pt.wikipedia.org/wiki/Exercício_físico",
        "cozinha": "https://pt.wikipedia.org/wiki/Utensílio_de_cozinha",
        "pets": "https://pt.wikipedia.org/wiki/Animal_de_estimação",
        "tecnologia": "https://pt.wikipedia.org/wiki/Tecnologia"
    }
    return links.get(categoria.lower(), "https://pt.wikipedia.org")

def criar_html_completo(titulo, descricao, artigo_html, review_html):
    """Cria HTML completo para o artigo satélite"""
    
    # Extrai header e footer do review
    header_match = re.search(r"(.*?)<article", review_html, re.IGNORECASE | re.DOTALL)
    footer_match = re.search(r"</article>(.*)", review_html, re.IGNORECASE | re.DOTALL)
    
    header = header_match.group(1) if header_match else ""
    footer = footer_match.group(1) if footer_match else ""
    
    # Atualiza título
    if titulo:
        header = re.sub(r"<title>.*?</title>", f"<title>{titulo}</title>", header, flags=re.IGNORECASE | re.DOTALL)
    
    # Atualiza meta description
    if descricao:
        desc_pattern = r'<meta name="description" content=".*?"'
        if re.search(desc_pattern, header, re.IGNORECASE):
            header = re.sub(desc_pattern, f'<meta name="description" content="{descricao}"', header, flags=re.IGNORECASE)
        else:
            # Insere se não existir
            head_end = header.find("</head>")
            if head_end != -1:
                header = header[:head_end] + f'\n<meta name="description" content="{descricao}">' + header[head_end:]
    
    # Adiciona breadcrumb
    breadcrumb = '''
    <div class="breadcrumb">
        <a href="../index.html">Home</a> &gt; 
        <a href="../{categoria}/index.html">{categoria_title}</a> &gt; 
        <a href="../{categoria}/{produto_slug}/index.html">{produto}</a> &gt; 
        <span>{satelite_nome}</span>
    </div>
    '''
    
    # HTML completo
    html_completo = f"""
{header}
<body>
    <div class="container">
        {breadcrumb}
        <main class="content">
            {artigo_html}
        </main>
    </div>
{footer}
"""
    
    return html_completo

def processar_review(caminho_review):
    """Processa um review e cria artigos satélite"""
    
    try:
        with open(caminho_review, "r", encoding="utf-8") as f:
            review_html = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler review: {e}")
        return
    
    # Extrai informações do review
    title_match = re.search(r"<title>(.*?)</title>", review_html, re.IGNORECASE | re.DOTALL)
    article_match = re.search(r"<article.*?>(.*?)</article>", review_html, re.IGNORECASE | re.DOTALL)
    
    if not title_match or not article_match:
        print(f"⚠️ Review inválido: {caminho_review}")
        return
    
    review_title = title_match.group(1).strip()
    review_article_content = article_match.group(1)
    
    # Obtém categoria e produto do caminho
    caminho_rel = Path(caminho_review).relative_to(DOCS_DIR)
    partes = caminho_rel.parts
    
    if len(partes) != 2:  # categoria/produto/index.html
        print(f"⚠️ Estrutura inválida: {caminho_review}")
        return
    
    categoria = partes[0]
    produto_slug = partes[1].replace("/index.html", "")
    produto_nome = produto_slug.replace("-", " ").title()
    
    # URL do review principal
    review_url = f"/{categoria}/{produto_slug}/"
    link_externo = link_externo_por_categoria(categoria)
    ano_atual = time.strftime("%Y")
    
    print(f"\n🎯 PROCESSANDO: {produto_nome} ({categoria})")
    print(f"   📁 Review: {categoria}/{produto_slug}/")
    
    # Cria cada tipo de artigo satélite
    for satelite in SATELLITE_TYPES:
        slug_satelite = f"{produto_slug}-{satelite['slug']}"
        pasta_destino = DOCS_DIR / categoria / slug_satelite
        arquivo_final = pasta_destino / "index.html"
        
        # Pula se já existir
        if arquivo_final.exists():
            print(f"   ⏭️  Satélite já existe: {satelite['slug']}")
            continue
        
        print(f"   🛰️  Criando: {satelite['nome']}")
        
        # Prepara prompt específico
        prompt_personalizado = PROMPT_SATELITE + f"""

INFORMAÇÕES ESPECÍFICAS:
PRODUTO: {produto_nome}
CATEGORIA: {categoria}
TIPO DE CONTEÚDO: {satelite['intent']}
FOCO PRINCIPAL: {satelite['focus']}
ANO ATUAL: {ano_atual}

LINK DO REVIEW PRINCIPAL (usar 1-2x naturalmente):
{review_url}

LINK EXTERNO DE REFERÊNCIA:
{link_externo}

TÍTULO DO REVIEW (para contexto):
{review_title}

Crie um artigo ORIGINAL e COMPLETO sobre {satelite['intent'].lower()} para {produto_nome}.
"""
        
        # Chama a IA
        try:
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "Você é um redator especialista em conteúdo informativo para blogs."},
                    {"role": "user", "content": prompt_personalizado}
                ],
                "temperature": 0.7,
                "max_tokens": 3000
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=HEADERS,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            resultado = response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"   ❌ Erro na IA ({satelite['slug']}): {e}")
            continue
        
        # Extrai resultado
        titulo_match = re.search(r"TITLE:\s*(.*?)(?:\n|$)", resultado, re.IGNORECASE)
        desc_match = re.search(r"DESCRIPTION:\s*(.*?)(?:\n|$)", resultado, re.IGNORECASE)
        article_match = re.search(r"ARTICLE:\s*(<article.*?</article>)", resultado, re.IGNORECASE | re.DOTALL)
        
        if not article_match:
            print(f"   ❌ IA não retornou ARTICLE válido para {satelite['slug']}")
            continue
        
        titulo = titulo_match.group(1).strip() if titulo_match else satelite['title_hint'].replace("{PRODUTO}", produto_nome).replace("{CATEGORIA}", categoria).replace("{ANO_ATUAL}", ano_atual)
        descricao = desc_match.group(1).strip() if desc_match else f"Análise completa sobre {satelite['intent'].lower()} do {produto_nome}. Descubra tudo o que precisa saber."
        artigo_html = article_match.group(1).strip()
        
        # Cria HTML completo
        html_final = criar_html_completo(titulo, descricao, artigo_html, review_html)
        
        # Cria diretório e salva
        pasta_destino.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(arquivo_final, "w", encoding="utf-8") as f:
                f.write(html_final)
            print(f"   ✅ Criado: {slug_satelite}/")
        except Exception as e:
            print(f"   ❌ Erro ao salvar satélite: {e}")
            continue
        
        # Pausa para não sobrecarregar API
        time.sleep(4)

def encontrar_reviews():
    """Encontra todos os reviews na estrutura docs/"""
    reviews = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        if "index.html" in files:
            caminho = Path(root) / "index.html"
            rel_path = caminho.relative_to(DOCS_DIR)
            partes = rel_path.parts
            
            # Verifica se é um review (categoria/produto/index.html)
            if len(partes) == 2 and not any(x in partes[1] for x in ["-vale-a-pena", "-e-bom", "-como-escolher", "-funciona-mesmo", "-melhor-marca"]):
                reviews.append(str(caminho))
    
    return reviews

def main():
    print("=" * 70)
    print("🛰️  GERADOR DE ARTIGOS SATÉLITE")
    print("=" * 70)
    
    if not OPENROUTER_API_KEY:
        print("❌ ERRO: OPENROUTER_API_KEY não encontrada")
        print("💡 Crie um arquivo .env com: OPENROUTER_API_KEY=sua_chave_aqui")
        exit(1)
    
    print("✅ API Key carregada do .env")
    print(f"📁 Diretório base: {DOCS_DIR}")
    
    # Encontra reviews
    reviews = encontrar_reviews()
    
    if not reviews:
        print("❌ Nenhum review encontrado na pasta docs/")
        print("💡 Execute primeiro o gerador.py para criar reviews")
        exit(1)
    
    print(f"\n📊 {len(reviews)} reviews encontrados")
    
    # Processa cada review
    for i, review in enumerate(reviews, 1):
        print(f"\n[{i}/{len(reviews)}] {'='*40}")
        processar_review(review)
    
    print("\n" + "=" * 70)
    print("🎉 GERADOR DE SATÉLITES CONCLUÍDO!")
    print("=" * 70)
    
    # Relatório final
    satelites_criados = 0
    for root, dirs, files in os.walk(DOCS_DIR):
        for dir_name in dirs:
            if any(x in dir_name for x in ["-vale-a-pena", "-e-bom", "-como-escolher", "-funciona-mesmo", "-melhor-marca"]):
                satelites_criados += 1
    
    print(f"📊 Total de artigos satélite criados: {satelites_criados}")
    print(f"🎯 Média: {satelites_criados / len(reviews):.1f} satélites por review")
    print("\n✅ Processo completo!")

if __name__ == "__main__":
    main()