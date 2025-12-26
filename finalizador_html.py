#!/usr/bin/env python3
"""
FINALIZADOR HTML SIMPLIFICADO - Versão funcional com prompt completo
"""

import os
import re
import requests
import time
import csv
import json
import unicodedata
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configurações
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ROOT_DIR = Path.cwd() / "docs"
CSV_PRODUTOS = Path.cwd() / "produtos.csv"
HISTORICO_FILE = Path.cwd() / "historico_simples.txt"

# PROMPT EDITORIAL COMPLETO
PROMPT_EDITORIAL = """Você é um editor humano sênior, especialista em SEO, UX editorial e conteúdo de conversão para sites de review que ranqueiam no Google.

Você receberá partes de um HTML já existente (title, meta description e <article>).
Seu trabalho é REFINAR, EXPANDIR E HUMANIZAR, não recriar do zero.

🚫 REGRAS ABSOLUTAS (NÃO QUEBRAR)

NÃO alterar header, footer, sidebar ou layout

NÃO remover nem adicionar tags HTML fora do <article>

NÃO criar CTAs de afiliado

NÃO mencionar afiliados, comissões ou "link especial"

NÃO alterar URLs existentes

NÃO inventar links quebrados

Links internos e externos SOMENTE dentro do <article>

NÃO citar anos (ex: 2024, 2025)

NÃO usar linguagem publicitária exagerada

🎯 OBJETIVO REAL DO CONTEÚDO

Transformar este artigo em um review definitivo, com:

Alta intenção de busca ("vale a pena", "funciona", "é bom")

Leitura natural, como se fosse escrita por alguém experiente

Conteúdo profundo o suficiente para não parecer raso

Clareza para quem está decidindo comprar

Estrutura que favoreça SEO sem parecer forçada

🧠 COMO ESCREVER (MUITO IMPORTANTE)

Escreva como uma pessoa que já usou, analisou ou conviveu com o produto

Inclua micro-histórias reais (uso no dia a dia, situações comuns)

Use exemplos concretos, não frases vagas

Evite termos genéricos como "excelente", "incrível", "imperdível"

Priorize clareza, experiência prática e contexto real

Faça o leitor imaginar o produto sendo usado

🧩 O QUE MELHORAR NO ARTICLE

Dentro do <article>:

Introdução

Deve contextualizar um problema real

Mostrar por que alguém está pesquisando esse produto

Criar identificação imediata com o leitor

Especificações

Explicar o que cada característica significa na prática

Evitar lista seca sem contexto

Testes / Uso Real

Simular uso cotidiano

Falar de pontos positivos e limitações reais

Mostrar experiência prática, mesmo que indireta

Prós e Contras

Prós claros e específicos

Contras honestos (isso aumenta confiança)

Comparações

Comparar com alternativas comuns do mercado

Focar em custo-benefício e perfil de uso

Para Quem Vale a Pena

Definir claramente quem deve comprar

E quem NÃO deve comprar

FAQ

Respostas humanas, não técnicas

Antecipar dúvidas reais de quem está quase decidindo

Links

Inserir naturalmente:

1 link interno relevante

1 link externo confiável e informativo

Sempre contextualizados dentro do texto

🧠 SEO (SEM FORÇAR)

Otimize o conteúdo usando variações naturais da palavra-chave

Use sinônimos e termos relacionados

Nunca repetir palavra-chave de forma mecânica

Priorizar leitura humana, não robô

📌 FORMATO DE SAÍDA (OBRIGATÓRIO):
TITLE:
<título otimizado>

DESCRIPTION:
<meta description otimizada>

ARTICLE:
<article>conteúdo refinado aqui...</article>
"""

def criar_slug(texto):
    """Cria slug igual ao gerador.py"""
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    slug = texto.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'[-]+', '-', slug)
    slug = slug.strip('-')
    return slug[:60]

def carregar_historico():
    """Carrega histórico de processamentos"""
    if HISTORICO_FILE.exists():
        with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def salvar_historico(slug):
    """Salva no histórico"""
    with open(HISTORICO_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{slug}\n")

def carregar_produtos_csv():
    """Carrega produtos do CSV"""
    produtos = {}
    if CSV_PRODUTOS.exists():
        with open(CSV_PRODUTOS, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                produto = row.get('produto', '').strip()
                status = row.get('status', '').lower()
                if produto and status == 'completed':
                    slug = criar_slug(produto)
                    produtos[slug] = {
                        'nome': produto,
                        'slug': slug,
                        'categoria': row.get('categoria', '')
                    }
    return produtos

def encontrar_arquivo(slug):
    """Encontra arquivo pelo slug"""
    for categoria_dir in ROOT_DIR.iterdir():
        if categoria_dir.is_dir() and categoria_dir.name not in ['assets', 'includes']:
            caminho = categoria_dir / slug / "index.html"
            if caminho.exists():
                return caminho
    return None

def extrair_conteudo(html):
    """Extrai title, description e article do HTML"""
    # Título
    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""
    
    # Description
    desc_match = re.search(r'<meta name="description" content="(.*?)"', html, re.IGNORECASE | re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    # Article
    article_match = re.search(r"<article[^>]*>(.*?)</article>", html, re.IGNORECASE | re.DOTALL)
    if not article_match:
        return None, None, None, None
    
    article_content = article_match.group(1).strip()
    article_full = article_match.group(0)
    
    return title, description, article_content, article_full

def chamar_ia_para_refinamento(title, description, article, produto_nome, categoria):
    """Chama a IA com o prompt completo"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt_completo = PROMPT_EDITORIAL + f"""

DADOS DO PRODUTO:
Nome: {produto_nome}
Categoria: {categoria}

CONTEÚDO ATUAL PARA REFINAR:

TITLE:
{title}

DESCRIPTION:
{description}

ARTICLE:
<article>
{article}
</article>

AGORA, REFINE ESTE CONTEÚDO seguindo TODAS as diretrizes acima.
"""
    
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "Você é um editor sênior especialista em melhorar artigos de review. Siga EXATAMENTE o formato solicitado."
            },
            {
                "role": "user", 
                "content": prompt_completo
            }
        ],
        "temperature": 0.7,
        "max_tokens": 6000
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"   ❌ Erro API: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return None

def extrair_resultado(resultado):
    """Extrai título, description e article da resposta da IA"""
    # Procura TITLE
    title_match = re.search(r"TITLE:\s*(.*?)(?=\nDESCRIPTION:|\nARTICLE:|\n\n|$)", resultado, re.IGNORECASE | re.DOTALL)
    novo_title = title_match.group(1).strip() if title_match else None
    
    # Procura DESCRIPTION
    desc_match = re.search(r"DESCRIPTION:\s*(.*?)(?=\nARTICLE:|\n\n|$)", resultado, re.IGNORECASE | re.DOTALL)
    nova_desc = desc_match.group(1).strip() if desc_match else None
    if nova_desc:
        nova_desc = re.sub(r'^["\']|["\']$', '', nova_desc)
    
    # Procura ARTICLE
    article_match = re.search(r"ARTICLE:\s*(<article[\s\S]*?</article>)", resultado, re.IGNORECASE | re.DOTALL)
    if article_match:
        novo_article = article_match.group(1).strip()
    else:
        # Tenta encontrar sem a tag ARTICLE:
        article_match2 = re.search(r"<article[\s\S]*?</article>", resultado, re.IGNORECASE | re.DOTALL)
        novo_article = article_match2.group(0).strip() if article_match2 else None
    
    return novo_title, nova_desc, novo_article

def processar_arquivo(caminho, produto_info):
    """Processa um único arquivo"""
    print(f"\n📝 Processando: {produto_info['nome']}")
    print(f"   📁 {caminho.relative_to(ROOT_DIR)}")
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"   ❌ Erro ao ler arquivo: {e}")
        return False
    
    # Extrai conteúdo
    title, description, article_content, article_full = extrair_conteudo(html)
    if not article_content:
        print("   ❌ Não encontrou <article> no HTML")
        return False
    
    tamanho_original = len(article_content)
    print(f"   📊 Tamanho original: {tamanho_original} caracteres")
    
    # Chama IA
    print("   🤖 Chamando IA para refinamento (pode levar até 2 minutos)...")
    resultado_ia = chamar_ia_para_refinamento(
        title, description, article_content, 
        produto_info['nome'], produto_info['categoria']
    )
    
    if not resultado_ia:
        print("   ❌ Falha na resposta da IA")
        return False
    
    # Extrai resultado
    novo_title, nova_desc, novo_article = extrair_resultado(resultado_ia)
    
    if not novo_article:
        print("   ❌ IA não retornou ARTICLE válido")
        # Salva resposta para debug
        with open(f"debug_{produto_info['slug']}.txt", 'w', encoding='utf-8') as f:
            f.write(resultado_ia)
        print(f"   💾 Resposta salva em debug_{produto_info['slug']}.txt")
        return False
    
    # Aplica modificações
    modificacoes = []
    
    if novo_title:
        html = re.sub(r"<title>.*?</title>", f"<title>{novo_title}</title>", html, flags=re.IGNORECASE | re.DOTALL)
        modificacoes.append("título")
    
    if nova_desc:
        # Remove a descrição existente
        html = re.sub(r'<meta name="description" content=".*?"', 
                     f'<meta name="description" content="{nova_desc}"', 
                     html, flags=re.IGNORECASE)
        modificacoes.append("description")
    
    # Substitui o article
    html = html.replace(article_full, novo_article)
    modificacoes.append("conteúdo")
    
    # Calcula novo tamanho
    tamanho_novo = len(novo_article)
    diferenca = tamanho_novo - tamanho_original
    
    # Salva arquivo
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✅ Salvo! {len(modificacoes)} modificações aplicadas")
        print(f"   📈 Tamanho novo: {tamanho_novo} caracteres")
        print(f"   📊 Diferença: {'+' if diferenca > 0 else ''}{diferenca} caracteres")
        
        # Salva no histórico
        salvar_historico(produto_info['slug'])
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao salvar arquivo: {e}")
        return False

def mostrar_status():
    """Mostra status atual"""
    historico = carregar_historico()
    produtos = carregar_produtos_csv()
    
    print("\n" + "="*60)
    print("📊 STATUS ATUAL")
    print("="*60)
    
    total_produtos = len(produtos)
    finalizados = len([s for s in produtos if s in historico])
    pendentes = total_produtos - finalizados
    
    print(f"Total de produtos no CSV: {total_produtos}")
    print(f"Produtos já finalizados: {finalizados}")
    print(f"Produtos pendentes: {pendentes}")
    
    if pendentes > 0:
        print("\n⏳ PENDENTES:")
        for slug, info in produtos.items():
            if slug not in historico:
                print(f"   • {info['nome']} ({info['categoria']})")
    
    if finalizados > 0:
        print("\n✅ FINALIZADOS:")
        for slug, info in produtos.items():
            if slug in historico:
                print(f"   • {info['nome']}")

def menu_principal():
    """Menu principal simplificado"""
    while True:
        print("\n" + "="*60)
        print("🎯 FINALIZADOR HTML SIMPLIFICADO")
        print("="*60)
        print("1. 🔄 Processar todos os produtos pendentes")
        print("2. 📝 Processar produto específico")
        print("3. 📊 Ver status")
        print("4. 🧹 Limpar histórico")
        print("5. ❌ Sair")
        
        opcao = input("\n🎯 Escolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            processar_todos()
        elif opcao == "2":
            processar_especifico()
        elif opcao == "3":
            mostrar_status()
        elif opcao == "4":
            limpar_historico()
        elif opcao == "5":
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida")

def processar_todos():
    """Processa todos os produtos pendentes"""
    historico = carregar_historico()
    produtos = carregar_produtos_csv()
    
    pendentes = []
    for slug, info in produtos.items():
        if slug not in historico:
            pendentes.append((slug, info))
    
    if not pendentes:
        print("\n✅ Todos os produtos já foram processados!")
        return
    
    print(f"\n🚀 Encontrados {len(pendentes)} produtos pendentes")
    
    sucessos = 0
    falhas = 0
    
    for i, (slug, info) in enumerate(pendentes, 1):
        print(f"\n[{i}/{len(pendentes)}] {'='*40}")
        
        caminho = encontrar_arquivo(slug)
        if not caminho:
            print(f"❌ Arquivo não encontrado: {info['nome']}")
            falhas += 1
            continue
        
        if processar_arquivo(caminho, info):
            sucessos += 1
        else:
            falhas += 1
        
        # Pausa entre processamentos
        if i < len(pendentes):
            print(f"\n⏳ Aguardando 10 segundos...")
            time.sleep(10)
    
    print(f"\n📊 Resultado: {sucessos} sucessos, {falhas} falhas")

def processar_especifico():
    """Processa um produto específico"""
    produtos = carregar_produtos_csv()
    
    if not produtos:
        print("❌ Nenhum produto encontrado no CSV")
        return
    
    print("\n📋 Produtos disponíveis:")
    lista_produtos = list(produtos.items())
    
    for i, (slug, info) in enumerate(lista_produtos, 1):
        print(f"{i:2d}. {info['nome']} ({info['categoria']})")
    
    try:
        escolha = int(input("\nEscolha o número do produto: ").strip())
        if 1 <= escolha <= len(lista_produtos):
            slug, info = lista_produtos[escolha - 1]
            
            caminho = encontrar_arquivo(slug)
            if not caminho:
                print(f"❌ Arquivo não encontrado: {info['nome']}")
                return
            
            if processar_arquivo(caminho, info):
                print(f"\n✅ {info['nome']} processado com sucesso!")
            else:
                print(f"\n❌ Falha ao processar {info['nome']}")
        else:
            print("❌ Escolha inválida")
    except ValueError:
        print("❌ Por favor, digite um número")

def limpar_historico():
    """Limpa o histórico de processamentos"""
    if HISTORICO_FILE.exists():
        confirmacao = input("\n⚠️  Tem certeza que deseja limpar o histórico? (s/n): ").strip().lower()
        if confirmacao == 's':
            try:
                HISTORICO_FILE.unlink()
                print("✅ Histórico limpo com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao limpar histórico: {e}")
    else:
        print("ℹ️ Nenhum histórico encontrado")

def main():
    print("=" * 60)
    print("🎯 FINALIZADOR HTML SIMPLIFICADO")
    print("=" * 60)
    
    if not OPENROUTER_API_KEY:
        print("❌ ERRO: OPENROUTER_API_KEY não encontrada")
        print("💡 Verifique seu arquivo .env")
        return
    
    print("✅ API Key carregada com sucesso")
    
    # Verifica se existe a pasta docs
    if not ROOT_DIR.exists():
        print(f"❌ Pasta docs não encontrada: {ROOT_DIR}")
        return
    
    menu_principal()

if __name__ == "__main__":
    main()