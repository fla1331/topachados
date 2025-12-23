import os
import re
import requests
import time
import csv
import json
import unicodedata

# Configurações
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat"
ROOT_DIR = os.path.join(os.getcwd(), "docs")           # Pasta raiz dos reviews
CSV_PRODUTOS = os.path.join(os.getcwd(), "produtos.csv")
HISTORICO_FILE = os.path.join(os.getcwd(), "reviews_finalizados.json")
EXTENSIONS = ("index.html",)

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# Prompt para a IA
PROMPT_EDITORIAL = """
Você é um editor humano sênior, especialista em SEO, UX editorial e conteúdo de conversão para sites de review que ranqueiam no Google.

Você receberá partes de um HTML já existente (title, meta description e <article>).
Seu trabalho é REFINAR, EXPANDIR E HUMANIZAR, não recriar do zero.

🚫 REGRAS ABSOLUTAS (NÃO QUEBRAR)

NÃO alterar header, footer, sidebar ou layout

NÃO remover nem adicionar tags HTML fora do <article>

NÃO criar CTAs de afiliado

NÃO mencionar afiliados, comissões ou “link especial”

NÃO alterar URLs existentes

NÃO inventar links quebrados

Links internos e externos SOMENTE dentro do <article>

NÃO citar anos (ex: 2024, 2025)

NÃO usar linguagem publicitária exagerada

🎯 OBJETIVO REAL DO CONTEÚDO

Transformar este artigo em um review definitivo, com:

Alta intenção de busca (“vale a pena”, “funciona”, “é bom”)

Leitura natural, como se fosse escrita por alguém experiente

Conteúdo profundo o suficiente para não parecer raso

Clareza para quem está decidindo comprar

Estrutura que favoreça SEO sem parecer forçada

🧠 COMO ESCREVER (MUITO IMPORTANTE)

Escreva como uma pessoa que já usou, analisou ou conviveu com o produto

Inclua micro-histórias reais (uso no dia a dia, situações comuns)

Use exemplos concretos, não frases vagas

Evite termos genéricos como “excelente”, “incrível”, “imperdível”

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

📌 TITLE E META DESCRIPTION

Criar um novo TITLE mais humano, focado em decisão

Criar uma META DESCRIPTION clara, objetiva e atrativa

Ambos devem refletir exatamente o conteúdo do artigo

TITLE:
<título otimizado>

DESCRIPTION:
<meta description otimizada>

ARTICLE:
<article>...</article>

"""


# Função para criar slugs consistentes
def slugify(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9\s-]", "", texto).lower()
    return re.sub(r"\s+", "-", texto).strip("-")

# Carrega produtos válidos do CSV
def carregar_produtos_csv():
    produtos_validos = set()
    if not os.path.exists(CSV_PRODUTOS):
        print(f"⚠️ CSV de produtos não encontrado: {CSV_PRODUTOS}")
        return produtos_validos
    with open(CSV_PRODUTOS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Considera apenas produtos com status 'completed'
            if row.get("produto") and row.get("status","").lower() == "completed":
                slug = slugify(row["produto"].strip())
                produtos_validos.add(slug)
    return produtos_validos

# Carrega histórico de reviews finalizados
def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# Salva histórico
def salvar_historico(historico):
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(list(historico), f, ensure_ascii=False, indent=2)

# Chama a IA para editar o review
def chamar_ia(title, description, article):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT_EDITORIAL},
            {"role": "user", "content": f"TITLE ATUAL:\n{title}\n\nDESCRIPTION ATUAL:\n{description}\n\nARTICLE ATUAL:\n{article}"}
        ],
        "temperature": 0.7
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=180
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Processa cada arquivo HTML de review
def processar_html(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        html = f.read()

    title_match = re.search(r"<title>(.*?)</title>", html, re.S)
    article_match = re.search(r"<article.*?>.*?</article>", html, re.S)
    if not title_match or not article_match:
        return False

    title = title_match.group(1).strip()
    desc_match = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
    description = desc_match.group(1).strip() if desc_match else ""
    article = article_match.group(0)

    print(f"🔧 Revisando review: {caminho}")
    try:
        resultado = chamar_ia(title, description, article)
    except Exception as e:
        print(f"❌ Erro ao processar {caminho}: {e}")
        return False

    novo_title = re.search(r"TITLE:\s*(.*)", resultado)
    nova_desc = re.search(r"DESCRIPTION:\s*(.*)", resultado)
    novo_article = re.search(r"ARTICLE:\s*(<article.*?</article>)", resultado, re.S)

    if novo_title:
        html = re.sub(r"<title>.*?</title>", f"<title>{novo_title.group(1).strip()}</title>", html, flags=re.S)
    if nova_desc:
        if desc_match:
            html = re.sub(r'<meta name="description" content=".*?"',
                          f'<meta name="description" content="{nova_desc.group(1).strip()}"', html)
        else:
            html = html.replace("</head>", f'<meta name="description" content="{nova_desc.group(1).strip()}">\n</head>')
    if novo_article:
        html = html.replace(article, novo_article.group(1).strip())

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)

    time.sleep(2)
    print(f"✅ Review finalizado: {caminho}")
    return True

# Percorre a pasta docs e processa apenas produtos do CSV
def percorrer_docs():
    produtos_validos = carregar_produtos_csv()
    historico = carregar_historico()
    reviews_finalizados = []

    if not produtos_validos:
        print("⚠️ Nenhum produto válido encontrado no CSV. Abortando.")
        return reviews_finalizados

    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file in EXTENSIONS:
                caminho = os.path.join(root, file)
                partes = os.path.relpath(caminho, ROOT_DIR).split(os.sep)
                if len(partes) == 3:  # categoria/produto/index.html
                    produto_slug = partes[1]
                    if produto_slug not in produtos_validos:
                        print(f"ℹ️ Produto não listado no CSV ou status não 'completed', pulando: {produto_slug}")
                        continue
                    if caminho in historico:
                        print(f"ℹ️ Review já finalizado anteriormente, pulando: {produto_slug}")
                        continue
                    sucesso = processar_html(caminho)
                    if sucesso:
                        reviews_finalizados.append(caminho)
                        historico.add(caminho)
                else:
                    print(f"ℹ️ Ignorando arquivo não-review: {caminho}")

    salvar_historico(historico)
    return reviews_finalizados

# Execução principal
if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("❌ Defina a variável OPENROUTER_API_KEY")
        exit(1)

    print("🚀 Iniciando revisão editorial dos reviews...")
    reviews = percorrer_docs()
    print(f"✅ Finalizado. Reviews processados: {len(reviews)}")
    for r in reviews:
        print(f" - {r}")
