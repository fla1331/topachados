import os
import re
import requests
import time
import unicodedata

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat"

DOCS_DIR = os.path.join(os.getcwd(), "docs")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

SATELLITE_TYPES = [
    {"slug": "vale-a-pena", "intent": "avaliar se o produto realmente compensa a compra",
     "title_hint": "Vale a pena comprar {PRODUTO}? O que analisar antes"},
    {"slug": "e-bom", "intent": "resolver dúvida e curiosidade sobre o produto",
     "title_hint": "{PRODUTO} é bom? Pontos positivos e negativos"},
    {"slug": "como-escolher", "intent": "educar o leitor e preparar para a decisão de compra",
     "title_hint": "Como escolher {CATEGORIA} ideal para sua necessidade"}
]

PROMPT_SATELITE = """
Você é um redator humano especialista em SEO e conteúdo informativo.

Crie UM artigo satélite com foco em tráfego orgânico.
Ele NÃO é um review direto e NÃO deve vender explicitamente.

REGRAS:
- Linguagem natural, humana e envolvente
- Texto original, profundo e útil
- Não mencionar afiliados
- Não criar CTA de compra
- Inserir 1 link interno natural apontando para o review
- Inserir 1 link externo confiável e informativo
- Não repetir parágrafos do review
- Texto rico, com exemplos e storytelling, aplicável para o usuário

FORMATO DE RETORNO (OBRIGATÓRIO):
TITLE:
<apenas o título>

DESCRIPTION:
<apenas a meta description>

ARTICLE:
<article>...</article>
"""

def slugify(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9\s-]", "", texto).lower()
    return re.sub(r"\s+", "-", texto).strip("-")

def chamar_ia(review_title, review_article, produto, categoria, review_url, satelite, link_externo):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT_SATELITE},
            {"role": "user", "content": f"""
PRODUTO:
{produto}

CATEGORIA:
{categoria}

TIPO DE SATÉLITE:
{satelite['intent']}

SUGESTÃO DE TÍTULO:
{satelite['title_hint'].replace('{PRODUTO}', produto).replace('{CATEGORIA}', categoria)}

LINK DO REVIEW (usar como link interno):
{review_url}

LINK EXTERNO CONFIÁVEL (usar naturalmente no artigo):
{link_externo}

TÍTULO DO REVIEW:
{review_title}

CONTEÚDO DO REVIEW:
{review_article}
"""}
        ],
        "temperature": 0.75
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def criar_html_com_template(review_html, article_satelite, title="", description=""):
    artigo_match = re.search(r"(<article[\s\S]*?</article>)", review_html, re.S)
    if not artigo_match:
        return None
    artigo_review = artigo_match.group(1)

    partes = review_html.split(artigo_review)
    header = partes[0]
    footer = partes[1] if len(partes) > 1 else ""

    if title:
        header = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", header, flags=re.S)
    if description:
        if "<meta name=\"description\"" in header:
            header = re.sub(r"<meta name=\"description\" content=\".*?\">",
                            f"<meta name=\"description\" content=\"{description}\">", header, flags=re.S)
        else:
            header = header.replace("</head>", f'<meta name="description" content="{description}">\n</head>')

    return f"{header}{article_satelite}{footer}"

def link_externo_por_categoria(categoria):
    links = {
        "smartphones": "https://pt.wikipedia.org/wiki/Smartphone",
        "eletrodomesticos": "https://pt.wikipedia.org/wiki/Eletrodoméstico",
        "computadores": "https://pt.wikipedia.org/wiki/Computador",
        "games": "https://pt.wikipedia.org/wiki/Video_game",
        "healthcare": "https://pt.wikipedia.org/wiki/Health_care",
        "ton-maquininhas-modelos": "https://pt.wikipedia.org/wiki/Máquina_de_cartão"
    }
    return links.get(categoria, "https://pt.wikipedia.org")

def processar_review(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        review_html = f.read()

    title_match = re.search(r"<title>(.*?)</title>", review_html, re.S)
    article_match = re.search(r"<article[\s\S]*?</article>", review_html, re.S)
    if not title_match or not article_match:
        print(f"⚠️ Index.html inválido ou sem <article>: {caminho}")
        return

    review_title = title_match.group(1).strip()
    review_article = article_match.group(0)

    partes = os.path.relpath(caminho, DOCS_DIR).split(os.sep)
    if len(partes) != 2:
        print(f"⚠️ Estrutura inválida, pulando: {caminho}")
        return

    categoria, produto_slug = partes
    produto = produto_slug.replace("-", " ").title()
    review_url = f"/{categoria}/{produto_slug}/"
    link_externo = link_externo_por_categoria(categoria)

    for satelite in SATELLITE_TYPES:
        slug = f"{produto_slug}-{satelite['slug']}"
        pasta_destino = os.path.join(DOCS_DIR, categoria, slug)
        arquivo_final = os.path.join(pasta_destino, "index.html")

        if os.path.exists(arquivo_final):
            print(f"⚠️ Satélite já existe, pulando: {slug}")
            continue

        os.makedirs(pasta_destino, exist_ok=True)
        print(f"🛰️ Criando satélite: {slug}")

        resultado = None
        for tentativa in range(3):
            try:
                resultado = chamar_ia(review_title, review_article, produto, categoria, review_url, satelite, link_externo)
            except Exception as e:
                print(f"❌ Erro IA {slug}, tentativa {tentativa+1}: {e}")
                time.sleep(2)
                continue

            a = re.search(r"ARTICLE:\s*(<article[\s\S]*?</article>)", resultado, re.S)
            if a:
                break
            print(f"⚠️ Resultado incompleto, retry {tentativa+1}")
            time.sleep(2)

        if not resultado or not a:
            print(f"❌ Satélite {slug} não gerado após retries")
            continue

        t = re.search(r"TITLE:\s*(.*)", resultado)
        d = re.search(r"DESCRIPTION:\s*(.*)", resultado)

        html_final = criar_html_com_template(
            review_html,
            a.group(1).strip(),
            title=t.group(1).strip() if t else "",
            description=d.group(1).strip() if d else ""
        )

        with open(arquivo_final, "w", encoding="utf-8") as f:
            f.write(html_final)
        time.sleep(3)

def percorrer_reviews():
    print(f"📂 Verificando pasta docs: {DOCS_DIR}")
    for root, _, files in os.walk(DOCS_DIR):
        if "index.html" not in files:
            continue
        rel_path = os.path.relpath(root, DOCS_DIR)
        partes = rel_path.split(os.sep)
        if len(partes) < 2:
            continue
        caminho_index = os.path.join(root, "index.html")
        print(f"➡️ Processando review: {caminho_index}")
        processar_review(caminho_index)

if __name__ == "__main__":
    percorrer_reviews()
    print("✅ Todos os satélites finalizados.")
