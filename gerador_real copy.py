#!/usr/bin/env python3
"""
GERADOR REAL v5.0 - SISTEMA PROFISSIONAL COMPLETO
SEO Avançado + Sitemap Automático + Performance + Monetização
"""

import os
import sys
import json
import csv
import re
import random
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from urllib.parse import urljoin, quote
from xml.dom import minidom

# Tenta importar requests para IA
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  'requests' não instalado. IA desativada.")
    print("💡 Para IA: pip install requests")

class GeradorReal:
    def __init__(self, site_url="https://topofertas.reviewnexus.blog"):
        self.base_dir = Path(__file__).parent
        self.docs_dir = self.base_dir / "docs"
        self.includes_dir = self.docs_dir / "includes"
        self.templates_dir = self.base_dir / "templates"  # Nova pasta para prompts
        self.ia_api_key = None
        self.ia_provider = None
        self.has_requests = HAS_REQUESTS
        self.site_url = site_url.rstrip('/')
        self.site_name = "Top Ofertas"
        
        print("=" * 70)
        print("🤖 GERADOR REAL v5.0 - SISTEMA PROFISSIONAL COMPLETO")
        print("=" * 70)
        print(f"🌐 Site: {self.site_url}")
        print(f"📁 Docs: {self.docs_dir}")
        
        if not self.has_requests:
            print("⚠️  MODO SEM IA: 'requests' não instalado")
            print("💡 Para IA: pip install requests")
        
        # Criar estrutura de pastas
        self.criar_estrutura_pastas()
        
        # Configurações padrão
        self.config = self.carregar_config()
        
        # Carregar configurações de IA se existirem
        self.carregar_config_ia()
        
        # Criar templates básicos se não existirem
        self.criar_templates_prompt_se_necessario()
    
    def criar_estrutura_pastas(self):
        """Cria pastas necessárias"""
        pastas = [
            self.docs_dir / "assets" / "css",
            self.docs_dir / "assets" / "js",
            self.docs_dir / "assets" / "img",
            self.docs_dir / "assets" / "img" / "eletrodomesticos",
            self.docs_dir / "assets" / "img" / "smartphones",
            self.docs_dir / "assets" / "img" / "computadores",
            self.docs_dir / "assets" / "img" / "games",
            self.docs_dir / "includes",
            self.templates_dir,  # Pasta para prompts
            self.base_dir / "backups",
            self.base_dir / "logs"
        ]
        
        for pasta in pastas:
            pasta.mkdir(parents=True, exist_ok=True)
    
    def carregar_config(self):
        """Carrega configurações do site"""
        config_path = self.base_dir / "config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Erro ao carregar config: {e}")
        
        # Configuração padrão
        config = {
            "site": {
                "name": "Top Ofertas",
                "url": self.site_url,
                "description": "Reviews honestos de produtos de tecnologia",
                "language": "pt-BR",
                "author": "Equipe Top Ofertas",
                "twitter": "@TopOfertas",
                "fb_app_id": "",
                "google_analytics": "",
                "default_image": "/assets/img/og-default.jpg"
            },
            "seo": {
                "default_priority": 0.8,
                "change_freq": "weekly",
                "enable_amp": False,
                "enable_jsonld": True
            },
            "content": {
                "word_count": 2000,
                "enable_faq": True,
                "enable_toc": True,
                "image_source": "unsplash",
                "use_ia_by_default": True,
                "default_ia_provider": "deepseek"
            }
        }
        
        # Salvar config padrão
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuração criada: {config_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar config: {e}")
        
        return config
    
    def carregar_config_ia(self):
        """Carrega configurações de IA se existirem"""
        config_path = self.base_dir / "config_ia.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.ia_api_key = config.get('api_key')
                    self.ia_provider = config.get('provider')
                    if self.ia_api_key:
                        print(f"✅ API Key carregada: {self.ia_provider}")
                        return True
            except Exception as e:
                print(f"⚠️  Erro ao carregar config IA: {e}")
        
        return False
    
    def criar_templates_prompt_se_necessario(self):
        """Cria templates de prompt se não existirem"""
        templates = {
            'review.txt': self.criar_template_review(),
            'comparativo.txt': self.criar_template_comparativo(),
            'guia.txt': self.criar_template_guia(),
            'analise.txt': self.criar_template_analise()
        }
        
        for nome, conteudo in templates.items():
            caminho = self.templates_dir / nome
            if not caminho.exists():
                try:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✅ Template criado: templates/{nome}")
                except Exception as e:
                    print(f"❌ Erro ao criar template {nome}: {e}")
    
    # ==================== CORE FUNCTIONS ====================
    
    def carregar_template(self, nome_arquivo):
        """Carrega um arquivo HTML do includes"""
        caminho = self.includes_dir / nome_arquivo
        
        if caminho.exists():
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️  Erro ao ler template {caminho}: {e}")
                return None
        else:
            return None
    
    def carregar_prompt_template(self, tipo_artigo):
        """Carrega template de prompt do arquivo .txt"""
        arquivo_prompt = self.templates_dir / f"{tipo_artigo}.txt"
        
        if arquivo_prompt.exists():
            try:
                with open(arquivo_prompt, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️  Erro ao ler prompt template: {e}")
        
        return None
    
    def criar_slug(self, texto):
        """Cria slug amigável para URL"""
        import unicodedata
        
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = texto.encode('ASCII', 'ignore').decode('ASCII')
        
        # Para minúsculas
        slug = texto.lower()
        
        # Remove caracteres especiais
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        
        # Substitui espaços por hífens
        slug = re.sub(r'[\s]+', '-', slug)
        
        # Remove hífens duplicados e nas extremidades
        slug = re.sub(r'[-]+', '-', slug)
        slug = slug.strip('-')
        
        # Limita tamanho (ótimo para SEO)
        return slug[:60]
    
    def criar_titulo_seo(self, produto, tipo_artigo):
        """Cria título otimizado para SEO"""
        
        ano_atual = datetime.now().year
        
        titulos_por_tipo = {
            'review': [
                f"{produto} - Review Completo e Análise {ano_atual}",
                f"Vale a pena comprar {produto}? Análise Detalhada",
                f"{produto}: Review Completo, Prós e Contras | Teste Real"
            ],
            'comparativo': [
                f"Comparativo: {produto} vs Concorrentes {ano_atual}",
                f"{produto}: Melhor Custo-Benefício? Análise Comparativa",
                f"Análise Comparativa do {produto} - Qual Vale Mais?"
            ],
            'guia': [
                f"Guia Completo: Como escolher {produto} {ano_atual}",
                f"Guida Definitivo do {produto} - Tudo o que Precisa Saber",
                f"Guia de Compra: {produto} - Dicas Especialistas"
            ],
            'analise': [
                f"Análise Técnica do {produto} - Especificações e Performance",
                f"{produto}: Teste Completo e Análise Detalhada",
                f"Review Técnico do {produto} - Vale o Investimento?"
            ]
        }
        
        opcoes = titulos_por_tipo.get(tipo_artigo.lower(), titulos_por_tipo['review'])
        return random.choice(opcoes)
    
    # ==================== SEO AVANÇADO ====================
    
    def criar_meta_tags_seo(self, titulo, descricao, keywords, url_relativa, imagem=None):
        """Cria todas as meta tags SEO avançadas"""
        
        url_completa = f"{self.site_url}/{url_relativa}"
        
        if not imagem:
            imagem = f"{self.site_url}{self.config['site']['default_image']}"
        
        # Criar descrição otimizada
        descricao_og = descricao[:155] + "..." if len(descricao) > 155 else descricao
        
        meta_tags = f'''    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <meta name="description" content="{descricao_og}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{self.config['site']['author']}">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{titulo}">
    <meta property="og:description" content="{descricao_og}">
    <meta property="og:image" content="{imagem}">
    <meta property="og:url" content="{url_completa}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{self.config['site']['name']}">
    <meta property="og:locale" content="pt_BR">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{titulo}">
    <meta name="twitter:description" content="{descricao_og}">
    <meta name="twitter:image" content="{imagem}">
    <meta name="twitter:creator" content="{self.config['site']['twitter']}">
    
    <!-- Canonical -->
    <link rel="canonical" href="{url_completa}">
    
    <!-- Schema.org -->
    {self.criar_jsonld_avancado(titulo, descricao_og, url_completa, imagem)}
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- CSS -->
    <link rel="stylesheet" href="{self.calcular_caminho_relativo(url_relativa, 'assets/css/style.css')}">
    
    <!-- Google Analytics -->
    {self.criar_google_analytics()}'''
        
        return meta_tags
    
    def criar_jsonld_avancado(self, titulo, descricao, url, imagem=None):
        """Cria JSON-LD Schema.org avançado"""
        
        if not imagem:
            imagem = f"{self.site_url}{self.config['site']['default_image']}"
        
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": titulo,
            "description": descricao,
            "image": imagem,
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat(),
            "author": {
                "@type": "Person",
                "name": self.config['site']['author']
            },
            "publisher": {
                "@type": "Organization",
                "name": self.config['site']['name'],
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.site_url}/assets/img/logo.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": url
            }
        }
        
        if self.config['seo']['enable_jsonld']:
            return f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>'
        return ""
    
    def criar_google_analytics(self):
        """Cria código do Google Analytics"""
        ga_id = self.config['site']['google_analytics']
        if ga_id:
            return f'''    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>'''
        return ""
    
    def calcular_caminho_relativo(self, url_origem, url_destino):
        """Calcula caminho relativo entre URLs"""
        niveis = url_origem.count('/')
        if niveis == 0:
            return url_destino
        else:
            return "../" * niveis + url_destino
    
    # ==================== SISTEMA DE IMAGENS ====================
    
    def obter_url_imagem(self, produto, categoria):
        """Obtém URL da imagem para o produto"""
        
        # Imagens por categoria (Unsplash - livre uso)
        imagens_por_categoria = {
            'games': [
                'https://images.unsplash.com/photo-1534423861386-85a16f5d13fd?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=1200&h=630&fit=crop'
            ],
            'eletrodomesticos': [
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=630&fit=crop'
            ],
            'smartphones': [
                'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200&h=630&fit=crop'
            ],
            'computadores': [
                'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=1200&h=630&fit=crop'
            ]
        }
        
        # Usar imagem padrão da categoria
        if categoria.lower() in imagens_por_categoria:
            return random.choice(imagens_por_categoria[categoria.lower()])
        
        # Imagem padrão do site
        return f"{self.site_url}{self.config['site']['default_image']}"
    
    def criar_alt_imagem(self, produto):
        """Cria texto alt para imagem"""
        return f"Imagem ilustrativa do produto {produto}"
    
    # ==================== GERAÇÃO DE CONTEÚDO ====================
    
    def configurar_ia(self):
        """Configura a API de IA"""
        if not self.has_requests:
            print("❌ IA não disponível: biblioteca 'requests' não instalada")
            print("💡 Execute: pip install requests")
            return False
        
        print("\n" + "="*50)
        print("🌐 CONFIGURAÇÃO DA IA")
        print("="*50)
        
        if self.ia_api_key:
            print(f"⚠️  API já configurada: {self.ia_provider}")
            reconfigurar = input("Reconfigurar? (s/n): ").strip().lower()
            if reconfigurar != 's':
                return True
        
        print("Escolha a API de IA:")
        print("1. DeepSeek (recomendada - gratuita)")
        print("2. Gemini (Google AI Studio)")
        print("3. Não usar IA agora")
        
        opcao = input("\nEscolha (1-3): ").strip()
        
        config_path = self.base_dir / "config_ia.json"
        
        if opcao == "1":
            print("\n🔑 Para DeepSeek:")
            print("1. Acesse: https://platform.deepseek.com/api_keys")
            print("2. Crie conta gratuita")
            print("3. Gere API Key")
            api_key = input("\nCole sua DeepSeek API Key: ").strip()
            
            if api_key:
                self.ia_api_key = api_key
                self.ia_provider = 'deepseek'
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({'api_key': api_key, 'provider': 'deepseek'}, f, indent=2)
                print("✅ DeepSeek configurada!")
                return True
        
        elif opcao == "2":
            print("\n🔑 Para Gemini (Google AI Studio):")
            print("1. Acesse: https://aistudio.google.com/app/apikey")
            print("2. Crie projeto e gere API Key")
            api_key = input("\nCole sua Gemini API Key: ").strip()
            
            if api_key:
                self.ia_api_key = api_key
                self.ia_provider = 'gemini'
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({'api_key': api_key, 'provider': 'gemini'}, f, indent=2)
                print("✅ Gemini configurada!")
                return True
        
        print("⚠️  IA não configurada. Usando conteúdo básico.")
        return False
    
    def gerar_conteudo_com_ia(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado):
        """Gera conteúdo usando IA"""
        
        if not self.ia_api_key or not self.has_requests:
            print("   ⚠️  IA não disponível, usando conteúdo básico")
            return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado)
        
        print(f"   🤖 Gerando conteúdo com IA ({self.ia_provider})...")
        
        prompt = self.criar_prompt_ia(produto, categoria, tipo_artigo, site_oficial, link_afiliado)
        
        try:
            if self.ia_provider == 'deepseek':
                return self.chamar_deepseek_api(prompt)
            elif self.ia_provider == 'gemini':
                return self.chamar_gemini_api(prompt)
            else:
                print(f"   ❌ Provedor {self.ia_provider} não suportado")
                return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado)
                
        except Exception as e:
            print(f"   ⚠️  Erro na IA: {e}")
            return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado)
    
    def chamar_deepseek_api(self, prompt):
        """Chama API da DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.ia_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Você é um especialista em SEO e criação de conteúdo para reviews de produtos."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                conteudo = result["choices"][0]["message"]["content"]
                conteudo = self.limpar_resposta_ia(conteudo)
                print(f"   ✅ DeepSeek gerou {len(conteudo)} caracteres")
                return conteudo
            else:
                print(f"   ❌ Erro DeepSeek ({response.status_code}): {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
            return None
    
    def chamar_gemini_api(self, prompt):
        """Chama API do Gemini (versão atualizada)"""
        
        # Endpoints mais recentes do Gemini
        endpoints = [
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        ]
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4000,
            }
        }
        
        for endpoint in endpoints:
            try:
                response = requests.post(
                    f"{endpoint}?key={self.ia_api_key}",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    conteudo = result['candidates'][0]['content']['parts'][0]['text']
                    conteudo = self.limpar_resposta_ia(conteudo)
                    print(f"   ✅ Gemini gerou {len(conteudo)} caracteres")
                    return conteudo
                    
            except Exception:
                continue
        
        print("   ❌ Todos os endpoints Gemini falharam")
        return None


        
    
    def criar_prompt_ia(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado):
        """Cria prompt usando templates ou padrão"""
        
        # Tentar carregar do template .txt
        template = self.carregar_prompt_template(tipo_artigo)
        
        if template:
            # Substituir placeholders
            prompt = template
            prompt = prompt.replace("{PRODUTO}", produto)
            prompt = prompt.replace("{CATEGORIA}", categoria)
            prompt = prompt.replace("{TIPO_ARTIGO}", tipo_artigo)
            prompt = prompt.replace("{SITE_OFICIAL}", site_oficial)
            prompt = prompt.replace("{LINK_AFILIADO}", link_afiliado)
            prompt = prompt.replace("{SITE_URL}", self.site_url)
            prompt = prompt.replace("{SITE_NAME}", self.config['site']['name'])
            prompt = prompt.replace("{AUTHOR}", self.config['site']['author'])
            prompt = prompt.replace("{ANO_ATUAL}", str(datetime.now().year))
            return prompt
        
        # Se não tiver template, usar padrão
        return self.criar_prompt_padrao(produto, categoria, tipo_artigo, site_oficial, link_afiliado)
    
    def criar_prompt_padrao(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado):
        """Cria prompt padrão se não tiver template"""
        
        estruturas = {
            'review': """## ESTRUTURA PARA REVIEW:
1. INTRODUÇÃO (contextualizar o produto)
2. ESPECIFICAÇÕES TÉCNICAS DETALHADAS
3. DESIGN E QUALIDADE DE CONSTRUÇÃO
4. PERFORMANCE NO USO PRÁTICO
5. PRÓS E CONTRAS HONESTOS
6. COMPARAÇÃO COM 2-3 CONCORRENTES DIRETOS
7. ANÁLISE DE CUSTO-BENEFÍCIO
8. CONCLUSÃO (RECOMENDAÇÃO FINAL)
9. FAQ COM 5 PERGUNTAS RELEVANTES
10. ONDE COMPRAR COM MELHOR PREÇO""",
            
            'comparativo': """## ESTRUTURA PARA COMPARATIVO:
1. INTRODUÇÃO SOBRE A CATEGORIA
2. TABELA COMPARATIVA DE ESPECIFICAÇÕES
3. ANÁLISE INDIVIDUAL DE CADA PRODUTO
4. COMPARAÇÃO LADO A LADO (VANTAGENS/DESVANTAGENS)
5. VENCEDOR POR CATEGORIA (DESEMPENHO, CUSTO-BENEFÍCIO, ETC.)
6. RECOMENDAÇÃO POR PERFIL DE USUÁRIO""",
            
            'guia': """## ESTRUTURA PARA GUIA:
1. INTRODUÇÃO EDUCATIVA SOBRE A CATEGORIA
2. FATORES IMPORTANTES AO ESCOLHER
3. TERMINOLOGIA BÁSICA EXPLICADA
4. MARCAS E MODELOS RECOMENDADOS
5. DICAS DE MANUTENÇÃO E CUIDADOS
6. PERGUNTAS PARA FAZER ANTES DE COMPRAR
7. LINKS PARA REVIEWS ESPECÍFICOS""",
            
            'analise': """## ESTRUTURA PARA ANÁLISE TÉCNICA:
1. INTRODUÇÃO TÉCNICA
2. ESPECIFICAÇÕES DETALHADAS
3. RESULTADOS DE TESTES/BENCHMARKS
4. ANÁLISE DE ARQUITETURA/TECNOLOGIA
5. POTENCIAIS DE UPGRADE/EXPANSÃO
6. COMPARAÇÃO TÉCNICA COM CONCORRENTES
7. CONCLUSÃO PARA USUÁRIOS TÉCNICOS"""
        }
        
        estrutura = estruturas.get(tipo_artigo.lower(), estruturas['review'])
        
        prompt = f"""# CRIAÇÃO DE ARTIGO SEO PROFISSIONAL

## INFORMAÇÕES BÁSICAS:
- PRODUTO: {produto}
- CATEGORIA: {categoria}
- TIPO DE ARTIGO: {tipo_artigo.upper()}

{estrutura}

## INSTRUÇÕES:
- PÚBLICO: Brasileiros pesquisando antes de comprar
- TOM: Profissional, autoritativo, acessível
- COMPRIMENTO: 1500-2000 palavras
- NÍVEL DE DETALHE: Alto, com informações práticas

## FORMATAÇÃO HTML:
- Use APENAS: h2, h3, p, ul, li, strong, a, table, tr, td, th
- Para links: target="_blank" rel="nofollow" ou "nofollow sponsored"
- NUNCA use: div, span, style, class, emojis no HTML

## LINKS PARA INCLUIR:
1. Site oficial: {site_oficial} (rel="nofollow")
2. Link afiliado: {link_afiliado} (rel="nofollow sponsored")
3. Inclua 2-3 links internos para artigos relacionados
4. Inclua 1-2 links externos para fontes confiáveis

## QUALIDADE:
- Seja ESPECÍFICO com dados e exemplos
- Seja IMPARCIAL (mostre pontos fortes e fracos)
- Seja PRÁTICO (informações úteis para decisão de compra)
- Seja COMPLETO (responda todas dúvidas possíveis)

## RETORNO:
Retorne APENAS o HTML completo, sem comentários extras.
O HTML deve estar 100% pronto para publicação.

Comece agora o artigo sobre "{produto}":"""
        
        return prompt
    
    def criar_template_review(self):
        """Cria template para review.txt"""
        return """# TEMPLATE PARA REVIEW - {PRODUTO}

Você é um especialista em {CATEGORIA} com 10 anos de experiência. Escreva um review completo sobre o produto.

## INFORMAÇÕES:
- PRODUTO: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- SITE OFICIAL: {SITE_OFICIAL}
- LINK AFILIADO: {LINK_AFILIADO}

## ESTRUTURA OBRIGATÓRIA:
1. TÍTULO ATRAENTE (incluir {PRODUTO} e ano)
2. INTRODUÇÃO (2-3 parágrafos, contextualizar)
3. ESPECIFICAÇÕES TÉCNICAS (tabela ou lista detalhada)
4. TESTES PRÁTICOS (como funciona no dia a dia)
5. VANTAGENS (lista com explicações)
6. DESVANTAGENS (lista honesta)
7. COMPARAÇÃO COM CONCORRENTES (2-3 produtos similares)
8. CUSTO-BENEFÍCIO (vale o preço?)
9. CONCLUSÃO (para quem recomendamos)
10. FAQ (5 perguntas frequentes com <details> e <summary>)

## FORMATAÇÃO HTML:
- Use H2 para títulos principais
- Use H3 para subtítulos
- Use <ul> e <li> para listas
- Use <table> para comparações
- Use <a href="" target="_blank" rel="nofollow"> para links
- Para FAQ: <details><summary>Pergunta</summary><p>Resposta</p></details>

## TOM:
- Profissional mas acessível
- Imparcial (mostre prós e contras)
- Focado no usuário brasileiro
- Informativo e útil

## SEO:
- Inclua palavras-chave naturalmente
- Use parágrafos curtos
- Inclua pelo menos 1500 palavras

## LINKS:
- Link oficial: {SITE_OFICIAL} (rel="nofollow")
- Link afiliado: {LINK_AFILIADO} (rel="nofollow sponsored")
- 2-3 links internos para outros artigos do site
- 1-2 links externos para fontes confiáveis

Retorne APENAS HTML válido pronto para publicação."""
    
    def criar_template_comparativo(self):
        """Cria template para comparativo.txt"""
        return """# TEMPLATE PARA COMPARATIVO - {PRODUTO}

## OBJETIVO:
Comparar {PRODUTO} com seus principais concorrentes para ajudar na decisão de compra.

## ESTRUTURA:
1. INTRODUÇÃO sobre a categoria {CATEGORIA}
2. TABELA COMPARATIVA completa (especificações, preços, recursos)
3. ANÁLISE INDIVIDUAL de cada produto
4. COMPARAÇÃO DETALHADA ponto a ponto
5. VENCEDOR POR CATEGORIA (melhor custo-benefício, melhor performance, etc.)
6. RECOMENDAÇÃO FINAL baseada em diferentes perfis de usuário

## PRODUTOS A COMPARAR:
1. {PRODUTO} (principal)
2. Concorrente A (principal concorrente)
3. Concorrente B (alternativa popular)

## TABELA COMPARATIVA OBRIGATÓRIA:
| Característica | {PRODUTO} | Concorrente A | Concorrente B |
|----------------|-----------|---------------|---------------|
| Preço | [Preço] | [Preço] | [Preço] |
| [Característica 1] | [Info] | [Info] | [Info] |
| [Característica 2] | [Info] | [Info] | [Info] |
| [Característica 3] | [Info] | [Info] | [Info] |
| Garantia | [Info] | [Info] | [Info] |

## CONCLUSÃO:
- Para quem vale mais o {PRODUTO}
- Para quem recomendar os concorrentes
- Qual oferece melhor custo-benefício

Retorne HTML completo com tabela comparativa."""
    
    def criar_template_guia(self):
        """Cria template para guia.txt"""
        return """# TEMPLATE PARA GUIA - Como escolher {PRODUTO}

## OBJETIVO:
Educar o leitor sobre {CATEGORIA} e ajudá-lo a tomar a melhor decisão de compra.

## ESTRUTURA:
1. INTRODUÇÃO: O que é {PRODUTO} e por que é importante
2. FATORES CRÍTICOS ao escolher (lista detalhada)
3. TERMINOLOGIA EXPLICADA (termos técnicos em português simples)
4. MARCAS E MODELOS RECOMENDADOS (com prós e contras de cada)
5. DICAS DE MANUTENÇÃO e cuidados importantes
6. PERGUNTAS PARA FAZER ANTES DE COMPRAR
7. RECOMENDAÇÕES POR ORÇAMENTO (baixo, médio, alto)

## FOCO NO CONSUMIDOR BRASILEIRO:
- Preços em Reais
- Disponibilidade no Brasil
- Garantia e suporte técnico local
- Compatibilidade com rede elétrica brasileira

## DICAS PRÁTICAS:
- Como testar antes de comprar
- Onde encontrar promoções
- Como negociar garantia estendida
- O que verificar na nota fiscal

## FORMATAÇÃO:
- Listas explicativas
- Destaques para informações importantes
- Links para reviews específicos
- Exemplos reais de uso

Retorne um guia completo e educativo em HTML."""
    
    def criar_template_analise(self):
        """Cria template para analise.txt"""
        return """# TEMPLATE PARA ANÁLISE TÉCNICA - {PRODUTO}

## PÚBLICO-ALVO:
Usuários avançados, entusiastas e profissionais que precisam de detalhes técnicos.

## ESTRUTURA TÉCNICA:
1. ARQUITETURA E COMPONENTES (diagrama conceitual em texto)
2. ESPECIFICAÇÕES DETALHADAS (todos os componentes e suas specs)
3. RESULTADOS DE BENCHMARKS (dados quantitativos de performance)
4. ANÁLISE DE EFICIÊNCIA (consumo, calor, ruído)
5. POTENCIAL DE OVERCLOCK/UPGRADE
6. COMPARAÇÃO TÉCNICA com especificações de referência
7. CONCLUSÃO TÉCNICA (para que tipo de uso é ideal)

## DADOS TÉCNICOS OBRIGATÓRIOS:
- Processador/CPU: especificações completas
- Memória: tipo, velocidade, latência
- Armazenamento: tipo, velocidade, capacidade
- Conectividade: todas as portas e protocolos
- Alimentação: consumo, eficiência
- Resfriamento: sistema, temperaturas em carga

## TESTES A RELATAR:
- Performance em diferentes cenários de uso
- Estabilidade sob carga prolongada
- Compatibilidade com periféricos
- Temperaturas em ambientes controlados

## LINGUAGEM:
- Técnica mas compreensível
- Dados precisos e verificáveis
- Referências a padrões da indústria
- Comparações com benchmarks conhecidos

Retorne uma análise técnica profunda em HTML com dados específicos."""
    
    def gerar_conteudo_basico(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado):
        """Gera conteúdo básico SEM IA com qualidade"""
        
        # Templates específicos por tipo de artigo
        if tipo_artigo.lower() == 'review':
            return self.gerar_review_basico(produto, categoria, site_oficial, link_afiliado)
        elif tipo_artigo.lower() == 'comparativo':
            return self.gerar_comparativo_basico(produto, categoria, site_oficial, link_afiliado)
        elif tipo_artigo.lower() == 'guia':
            return self.gerar_guia_basico(produto, categoria, site_oficial, link_afiliado)
        else:
            return self.gerar_analise_basica(produto, categoria, site_oficial, link_afiliado)
    
    def gerar_review_basico(self, produto, categoria, site_oficial, link_afiliado):
        """Gera review básico com conteúdo realista"""
        
        # Conteúdo específico por categoria
        categorias_conteudo = {
            'games': """
            <h2>🎮 Análise do {produto}</h2>
            <p>O {produto} representa a nova geração de consoles, trazendo avanços significativos em performance gráfica, carregamento de jogos e experiência do usuário.</p>
            
            <h3>🚀 Performance e Gráficos</h3>
            <ul>
                <li><strong>Resolução 4K:</strong> Suporte nativo a 4K com HDR</li>
                <li><strong>Altas Taxas de Quadro:</strong> Até 120fps em jogos otimizados</li>
                <li><strong>Carregamento Rápido:</strong> SSD de alta velocidade reduz tempos de loading</li>
                <li><strong>Ray Tracing:</strong> Iluminação realista em tempo real</li>
            </ul>
            
            <h3>🎮 Experiência do Jogador</h3>
            <p>Com controles aprimorados e recursos exclusivos, a imersão atinge novos patamares. A biblioteca de jogos inclui títulos que demonstram todo o potencial do hardware.</p>
            
            <h3>💰 Custo-Benefício</h3>
            <p>Considerando a tecnologia avançada e longevidade, o {produto} oferece excelente relação custo-benefício para quem busca a melhor experiência em jogos.</p>""",
            
            'smartphones': """
            <h2>📱 Análise do {produto}</h2>
            <p>O {produto} combina design premium com performance de ponta, atendendo tanto usuários comuns quanto exigentes.</p>
            
            <h3>📸 Sistema de Câmeras</h3>
            <ul>
                <li><strong>Câmera Principal:</strong> Alta resolução com estabilização óptica</li>
                <li><strong>Sensor Ultra-wide:</strong> Para fotos panorâmicas impressionantes</li>
                <li><strong>Zoom Óptico:</strong> Captura detalhes à distância</li>
                <li><strong>Gravação em 4K:</strong> Vídeos com qualidade cinematográfica</li>
            </ul>
            
            <h3>⚡ Performance</h3>
            <p>Com processador de última geração e RAM generosa, o dispositivo executa qualquer aplicação com fluidez.</p>
            
            <h3>🔋 Bateria e Autonomia</h3>
            <p>Bateria de longa duração com carregamento rápido, ideal para uso intensivo durante todo o dia.</p>""",
            
            'eletrodomesticos': """
            <h2>🏠 Análise do {produto}</h2>
            <p>O {produto} traz inovação e eficiência para o lar, combinando tecnologia avançada com praticidade no dia a dia.</p>
            
            <h3>⚡ Eficiência Energética</h3>
            <ul>
                <li><strong>Consumo Otimizado:</strong> Economia na conta de energia</li>
                <li><strong>Selo Procel A:</strong> Máxima eficiência energética</li>
                <li><strong>Modo Econômico:</strong> Redução inteligente do consumo</li>
            </ul>
            
            <h3>🧼 Facilidade de Uso e Limpeza</h3>
            <p>Design intuitivo com controles simplificados e superfícies de fácil limpeza.</p>
            
            <h3>🔊 Operação Silenciosa</h3>
            <p>Tecnologia de redução de ruído para operação discreta em qualquer ambiente.</p>""",
            
            'computadores': """
            <h2>💻 Análise do {produto}</h2>
            <p>O {produto} oferece performance profissional para trabalho criativo, jogos e multitarefa intensiva.</p>
            
            <h3>⚙️ Especificações Técnicas</h3>
            <ul>
                <li><strong>Processador:</strong> CPU de última geração para máxima performance</li>
                <li><strong>Placa de Vídeo:</strong> GPU dedicada para gráficos e renderização</li>
                <li><strong>Armazenamento:</strong> SSD rápido combinado com HDD de alta capacidade</li>
                <li><strong>Memória RAM:</strong> Ampla para multitarefa intensiva</li>
            </ul>
            
            <h3>🎮 Performance em Jogos e Aplicações</h3>
            <p>Capacidade de executar os jogos mais exigentes e aplicativos profissionais com fluidez.</p>
            
            <h3>🔧 Conectividade e Expansibilidade</h3>
            <p>Portas modernas e possibilidade de upgrades para acompanhar a evolução tecnológica.</p>"""
        }
        
        # Conteúdo padrão se categoria não especificada
        conteudo_categoria = categorias_conteudo.get(categoria.lower(), """
        <h2>📦 Análise do {produto}</h2>
        <p>O {produto} é um produto da categoria {categoria} que combina qualidade, desempenho e inovação.</p>
        
        <h3>✨ Principais Características</h3>
        <ul>
            <li><strong>Alta Performance:</strong> Desempenho consistente em todas as situações</li>
            <li><strong>Design Moderno:</strong> Estética contemporânea e funcional</li>
            <li><strong>Facilidade de Uso:</strong> Interface intuitiva para todos os usuários</li>
            <li><strong>Durabilidade:</strong> Construção robusta para longa vida útil</li>
        </ul>
        
        <h3>🎯 Para Quem é Indicado</h3>
        <p>Ideal para quem busca um produto confiável com bom custo-benefício na categoria {categoria}.</p>
        """)
        
        conteudo = conteudo_categoria.format(produto=produto, categoria=categoria)
        
        # Adicionar seção de onde comprar
        conteudo += f"""
        <div class="onde-comprar">
            <h3>🛒 Onde Comprar {produto}</h3>
            <p>Para garantir o melhor preço e condições, recomendamos:</p>
            <ul>
                <li><a href="{site_oficial}" target="_blank" rel="nofollow">Site Oficial</a> - Garantia direta do fabricante</li>
                <li><a href="{link_afiliado}" target="_blank" rel="nofollow sponsored">Loja Parceira</a> - Preço especial com entrega garantida</li>
            </ul>
            <p class="aviso-afiliado"><small>💡 Link afiliado: você não paga nada a mais, mas recebemos uma pequena comissão que ajuda a manter o site. Obrigado!</small></p>
        </div>
        
        {self.gerar_faq_generico(produto, categoria)}"""
        
        return conteudo
    
    def gerar_comparativo_basico(self, produto, categoria, site_oficial, link_afiliado):
        """Gera comparativo básico"""
        
        return f"""
        <h2>📊 Comparativo: {produto} vs Concorrentes</h2>
        
        <p>Nesta análise comparativa, avaliamos o {produto} contra seus principais concorrentes na categoria {categoria}.</p>
        
        <h3>📈 Tabela Comparativa</h3>
        <table class="tabela-comparativa">
            <tr>
                <th>Característica</th>
                <th>{produto}</th>
                <th>Concorrente A</th>
                <th>Concorrente B</th>
            </tr>
            <tr>
                <td>Preço Médio</td>
                <td>💰💎</td>
                <td>💰💰</td>
                <td>💰</td>
            </tr>
            <tr>
                <td>Performance</td>
                <td>⭐⭐⭐⭐⭐</td>
                <td>⭐⭐⭐⭐</td>
                <td>⭐⭐⭐</td>
            </tr>
            <tr>
                <td>Recursos</td>
                <td>✅ Completo</td>
                <td>✅ Básico+</td>
                <td>✅ Básico</td>
            </tr>
            <tr>
                <td>Garantia</td>
                <td>12 meses</td>
                <td>12 meses</td>
                <td>6 meses</td>
            </tr>
        </table>
        
        <h3>🏆 Vencedor por Categoria</h3>
        <ul>
            <li><strong>Melhor Custo-Benefício:</strong> Avalie conforme seu orçamento</li>
            <li><strong>Melhor Performance:</strong> {produto} se destaca</li>
            <li><strong>Mais Recursos:</strong> {produto} oferece mais funcionalidades</li>
        </ul>
        
        <h3>🎯 Recomendação</h3>
        <p>Se você busca o melhor desempenho e está disposto a investir, o {produto} é a escolha ideal.</p>
        """
    
    def gerar_guia_basico(self, produto, categoria, site_oficial, link_afiliado):
        """Gera guia básico"""
        
        return f"""
        <h2>📚 Guia Completo: Como Escolher {produto}</h2>
        
        <p>Este guia vai ajudá-lo a entender tudo o que precisa saber antes de comprar um {produto}.</p>
        
        <h3>🎯 O Que é {produto}?</h3>
        <p>{produto} é um produto da categoria {categoria} projetado para [função principal].</p>
        
        <h3>📝 Fatores Importantes ao Escolher</h3>
        <ol>
            <li><strong>Orçamento:</strong> Defina quanto pode gastar</li>
            <li><strong>Necessidades:</strong> Liste o que realmente precisa</li>
            <li><strong>Uso:</strong> Considere frequência e intensidade de uso</li>
            <li><strong>Marca:</strong> Pesquise reputação e suporte</li>
            <li><strong>Garantia:</strong> Verifique tempo e cobertura</li>
        </ol>
        
        <h3>🔧 Termos Técnicos Explicados</h3>
        <ul>
            <li><strong>[Termo 1]:</strong> Significado em português simples</li>
            <li><strong>[Termo 2]:</strong> Por que é importante</li>
            <li><strong>[Termo 3]:</strong> Como afeta o uso</li>
        </ul>
        
        <h3>🏷️ Marcas Recomendadas</h3>
        <p>Para {categoria}, algumas marcas se destacam:</p>
        <ul>
            <li>Marca Premium - Para quem busca o melhor</li>
            <li>Marca Intermediária - Excelente custo-benefício</li>
            <li>Marca Econômica - Boa opção com orçamento limitado</li>
        </ul>
        
        <h3>🔍 Dicas Finais</h3>
        <ul>
            <li>Leia reviews antes de comprar</li>
            <li>Teste o produto se possível</li>
            <li>Compare preços em diferentes lojas</li>
            <li>Verifique políticas de troca e devolução</li>
        </ul>
        """
    
    def gerar_analise_basica(self, produto, categoria, site_oficial, link_afiliado):
        """Gera análise técnica básica"""
        
        return f"""
        <h2>🔬 Análise Técnica do {produto}</h2>
        
        <p>Esta análise técnica examina as especificações e capacidades do {produto}.</p>
        
        <h3>⚙️ Especificações Principais</h3>
        <table>
            <tr>
                <th>Componente</th>
                <th>Especificação</th>
                <th>Impacto</th>
            </tr>
            <tr>
                <td>Componente Principal</td>
                <td>[Especificação técnica]</td>
                <td>Determina performance geral</td>
            </tr>
            <tr>
                <td>Memória/Armazenamento</td>
                <td>[Capacidade e tipo]</td>
                <td>Velocidade e capacidade de trabalho</td>
            </tr>
            <tr>
                <td>Conectividade</td>
                <td>[Tipos e padrões]</td>
                <td>Compatibilidade e velocidade</td>
            </tr>
        </table>
        
        <h3>📊 Performance Técnica</h3>
        <ul>
            <li><strong>Em carga leve:</strong> [Desempenho]</li>
            <li><strong>Em carga média:</strong> [Desempenho]</li>
            <li><strong>Em carga máxima:</strong> [Desempenho]</li>
            <li><strong>Estabilidade:</strong> [Avaliação]</li>
        </ul>
        
        <h3>🔧 Conclusão Técnica</h3>
        <p>O {produto} oferece [características técnicas] adequadas para [tipo de uso]. Para necessidades de [uso específico], apresenta bom desempenho.</p>
        """
    
    def gerar_faq_generico(self, produto, categoria):
        """Gera FAQ genérico"""
        
        return f"""
        <div class="faq-section">
            <h3>❓ Perguntas Frequentes sobre {produto}</h3>
            
            <details>
                <summary><strong>Qual o tempo de garantia?</strong></summary>
                <p>O {produto} geralmente possui garantia de 12 meses contra defeitos de fabricação. Consulte o manual ou site do fabricante para detalhes específicos.</p>
            </details>
            
            <details>
                <summary><strong>É compatível com outros dispositivos?</strong></summary>
                <p>Sim, o {produto} segue padrões de compatibilidade comuns da categoria {categoria}. Verifique especificações técnicas para conexões específicas.</p>
            </details>
            
            <details>
                <summary><strong>Quais cuidados de manutenção?</strong></summary>
                <p>Para manter em bom estado: limpe regularmente, evite umidade excessiva, guarde adequadamente e siga instruções do manual.</p>
            </details>
            
            <details>
                <summary><strong>Qual a vida útil esperada?</strong></summary>
                <p>Com uso normal, expectativa de [X] anos. Marcas consolidadas geralmente oferecem maior durabilidade.</p>
            </details>
            
            <details>
                <summary><strong>Vale a pena comprar agora?</strong></summary>
                <p>Se precisa do produto, o {produto} oferece boa relação custo-benefício. Novas versões geralmente levam [tempo] para serem lançadas.</p>
            </details>
        </div>
        """
    
    def limpar_resposta_ia(self, texto):
        """Limpa a resposta da IA"""
        # Remove blocos de código markdown
        texto = re.sub(r'```(?:html)?\s*', '', texto)
        texto = re.sub(r'\s*```', '', texto)
        
        # Remove explicações iniciais
        padroes = [
            r'^.*?(?=<h2|<div|<p>)',
            r'^Aqui está.*?(?=<)',
            r'^Segue.*?(?=<)',
            r'^Vamos.*?(?=<)'
        ]
        
        for padrao in padroes:
            texto = re.sub(padrao, '', texto, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove comentários HTML
        texto = re.sub(r'<!--.*?-->', '', texto, flags=re.DOTALL)
        
        # Remove espaços em excesso
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        texto = texto.strip()
        
        # Garante que começa com tag HTML
        if not texto.startswith('<'):
            match = re.search(r'<[^>]+>', texto)
            if match:
                texto = texto[match.start():]
            else:
                texto = f'<p>{texto}</p>'
        
        return texto
    
    # ==================== CRIAÇÃO DE ARTIGOS ====================
    
    def criar_artigo_completo(self, titulo, conteudo_html, categoria, produto_slug, tipo_artigo, nome_original, site_oficial, link_afiliado):
        """Cria artigo HTML completo"""
        
        print(f"   📝 Criando artigo: {titulo[:50]}...")
        
        # Criar pastas
        categoria_dir = self.docs_dir / categoria
        categoria_dir.mkdir(exist_ok=True)
        
        produto_dir = categoria_dir / produto_slug
        produto_dir.mkdir(exist_ok=True)
        
        # Caminho do arquivo
        caminho_arquivo = produto_dir / "index.html"
        url_relativa = f"{categoria}/{produto_slug}/"
        
        # Carregar templates com fallback
        header = self.carregar_template("header.html")
        if not header:
            header = self.criar_header_basico()
        
        footer = self.carregar_template("footer.html")
        if not footer:
            footer = self.criar_footer_basico()
        
        # Criar descrição SEO
        descricao_seo = f"{tipo_artigo.title()} completo do {nome_original}. Análise detalhada, especificações, onde comprar e se vale a pena. Confira nosso review!"
        keywords_seo = f"{nome_original}, {categoria}, review, análise, comprar, preço, especificações"
        
        # Obter imagem
        imagem_principal = self.obter_url_imagem(nome_original, categoria)
        alt_imagem = self.criar_alt_imagem(nome_original)
        
        # HTML do artigo
        html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    {self.criar_meta_tags_seo(titulo, descricao_seo, keywords_seo, url_relativa, imagem_principal)}
    <script src="https://topofertas.reviewnexus.blog/assets/js/script.js" defer></script>
</head>
<body>
    {header}
    
    <main class="container main-container">
        <article class="content">
            <div class="article-meta">
                <span><i class="far fa-calendar-alt"></i> {datetime.now().strftime('%d/%m/%Y')}</span>
                <span><i class="far fa-user"></i> {self.config['site']['author']}</span>
                <span><i class="far fa-clock"></i> {random.randint(5, 10)} min</span>
                <span><i class="fas fa-tag"></i> {categoria.title()}</span>
            </div>

            <h1>{titulo}</h1>

            <img src="{imagem_principal}" alt="{alt_imagem}" class="featured-image">

            <div class="article-body">
                {conteudo_html if conteudo_html else '<p>Conteúdo do artigo...</p>'}
            </div>

            <div class="rating-section">
                <h3>Avaliação dos Leitores</h3>
                <div class="stars">★★★★★</div>
                <p>{random.uniform(4.3, 4.9):.1f} de 5 ({random.randint(50, 200)} avaliações)</p>
            </div>

            <div class="cta">
                <h3>Pronto para Experimentar?</h3>
                <p>Garanta o melhor preço e condições através do nosso link especial:</p>
                <a href="{link_afiliado}" class="btn-cta" target="_blank" rel="nofollow sponsored">
                    <i class="fas fa-shopping-cart"></i> Ver Oferta Especial
                </a>
                <p class="affiliate-notice"><small>💡 Links afiliados: você não paga nada a mais, mas ganhamos uma pequena comissão. Obrigado pelo apoio!</small></p>
            </div>
        </article>

        <aside class="sidebar">
            <div class="widget">
                <h3><i class="fas fa-bolt"></i> Oferta Limitada</h3>
                <p><strong>{nome_original} com {random.randint(10, 25)}% OFF</strong></p>
                <p>Frete grátis + {random.randint(12, 24)} meses de garantia</p>
                <a href="{link_afiliado}" class="btn-sidebar" target="_blank" rel="nofollow sponsored">Aproveitar Agora</a>
            </div>

            <div class="widget">
                <h3><i class="fas fa-link"></i> Mais {categoria.title()}</h3>
                <p><a href="{self.calcular_caminho_relativo(url_relativa, f'{categoria}/index.html')}">Ver todos os produtos</a></p>
            </div>

            <div class="widget">
                <h3><i class="fas fa-info-circle"></i> Informações</h3>
                <ul class="site-links">
                    <li><a href="{self.calcular_caminho_relativo(url_relativa, 'sobre-nos.html')}">Sobre Nós</a></li>
                    <li><a href="{self.calcular_caminho_relativo(url_relativa, 'politica-de-privacidade.html')}">Privacidade</a></li>
                    <li><a href="{self.calcular_caminho_relativo(url_relativa, 'contato.html')}">Contato</a></li>
                </ul>
            </div>
        </aside>
    </main>
    
    {footer}
</body>
</html>'''
        
        # Salvar arquivo
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"   ✅ Artigo salvo: {categoria}/{produto_slug}/index.html")
            
            # Atualizar índice da categoria
            self.atualizar_index_categoria(categoria)
            
            # Atualizar sitemap
            self.atualizar_sitemap(url_relativa, datetime.now())
            
            return caminho_arquivo
        except Exception as e:
            print(f"   ❌ Erro ao salvar artigo: {e}")
            return None
    
    def criar_header_basico(self):
        """Cria header básico"""
        return '''<header class="site-header">
    <div class="container">
        <div class="logo">
            <a href="../index.html">🔥 Top Ofertas</a>
        </div>
        <nav class="main-nav">
            <a href="../index.html">Home</a>
            <a href="../eletrodomesticos/index.html">Eletrodomésticos</a>
            <a href="../smartphones/index.html">Smartphones</a>
            <a href="../computadores/index.html">Computadores</a>
            <a href="../games/index.html">Games</a>
        </nav>
    </div>
</header>'''
    
    def criar_footer_basico(self):
        """Cria footer básico"""
        return '''<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h3>Top Ofertas</h3>
                <p>Reviews honestos e análises detalhadas.</p>
            </div>
            <div class="footer-section">
                <h4>Links</h4>
                <a href="../sobre-nos.html">Sobre</a>
                <a href="../contato.html">Contato</a>
                <a href="../politica-de-privacidade.html">Privacidade</a>
            </div>
        </div>
        <p class="copyright">&copy; 2024 Top Ofertas. Todos os direitos reservados.</p>
    </div>
</footer>'''
    
    def atualizar_index_categoria(self, categoria):
        """Atualiza/cria index.html da categoria"""
        categoria_dir = self.docs_dir / categoria
        index_path = categoria_dir / "index.html"
        
        # Listar produtos na categoria
        produtos = []
        for item in categoria_dir.iterdir():
            if item.is_dir() and (item / "index.html").exists():
                produtos.append({
                    'slug': item.name,
                    'nome': item.name.replace('-', ' ').title(),
                    'data': datetime.fromtimestamp((item / "index.html").stat().st_mtime)
                })
        
        if not produtos:
            return
        
        # Ordenar por data
        produtos.sort(key=lambda x: x['data'], reverse=True)
        
        html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{categoria.title()} - {self.config['site']['name']}</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script src="https://topofertas.reviewnexus.blog/assets/js/script.js" defer></script>
</head>
<body>
    <div id="header-placeholder"></div>
    
    <main class="container">
        <h1>{categoria.title()}</h1>
        <p>Confira nossos reviews e análises de {categoria}:</p>
        
        <div class="products-grid">
'''
        
        for produto in produtos:
            html += f'''
            <div class="product-card">
                <h3><a href="{produto['slug']}/index.html">{produto['nome']}</a></h3>
                <p>Review completo e análise detalhada.</p>
                <a href="{produto['slug']}/index.html" class="btn-read">Ver Review →</a>
            </div>
'''
        
        html += f'''
        </div>
        <a href="../index.html" class="btn-home">← Voltar para Home</a>
    </main>
    
    <div id="footer-placeholder"></div>
    
    <script>
        fetch('../includes/header.html')
            .then(r => r.text())
            .then(h => document.getElementById('header-placeholder').innerHTML = h);
        
        fetch('../includes/footer.html')
            .then(r => r.text())
            .then(f => document.getElementById('footer-placeholder').innerHTML = f);
    </script>
</body>
</html>'''
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   📁 Index criado: {categoria}/index.html")
        except Exception as e:
            print(f"   ❌ Erro ao criar index: {e}")
    
    # ==================== SITEMAP ====================
    
    def criar_sitemap(self):
        """Cria/atualiza sitemap.xml"""
        print("\n🗺️  Criando sitemap.xml...")
        
        sitemap_path = self.docs_dir / "sitemap.xml"
        
        # Criar elemento raiz
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Adicionar URLs
        self.adicionar_url_sitemap(urlset, '', 1.0, 'daily')
        
        # Adicionar páginas estáticas
        paginas = ['sobre-nos.html', 'politica-de-privacidade.html', 'contato.html']
        for pagina in paginas:
            if (self.docs_dir / pagina).exists():
                self.adicionar_url_sitemap(urlset, pagina, 0.5, 'monthly')
        
        # Adicionar categorias e artigos
        for categoria_dir in self.docs_dir.iterdir():
            if categoria_dir.is_dir() and categoria_dir.name not in ['assets', 'includes']:
                categoria = categoria_dir.name
                self.adicionar_url_sitemap(urlset, f"{categoria}/", 0.8, 'weekly')
                
                # Artigos da categoria
                for artigo_dir in categoria_dir.iterdir():
                    if artigo_dir.is_dir() and (artigo_dir / "index.html").exists():
                        url = f"{categoria}/{artigo_dir.name}/"
                        lastmod = datetime.fromtimestamp((artigo_dir / "index.html").stat().st_mtime)
                        self.adicionar_url_sitemap(urlset, url, 0.6, 'monthly', lastmod)
        
        # Salvar sitemap
        try:
            xml_str = ET.tostring(urlset, encoding='unicode')
            xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
            
            with open(sitemap_path, 'w', encoding='utf-8') as f:
                f.write(xml_pretty)
            
            print(f"✅ Sitemap criado com {len(urlset.findall('url'))} URLs")
            
            # Criar robots.txt
            self.criar_robots_txt()
            
        except Exception as e:
            print(f"❌ Erro ao criar sitemap: {e}")
    
    def adicionar_url_sitemap(self, urlset, url_relativa, priority, changefreq, lastmod=None):
        """Adiciona uma URL ao sitemap"""
        if not lastmod:
            lastmod = datetime.now()
        
        url_elem = ET.SubElement(urlset, 'url')
        
        loc = ET.SubElement(url_elem, 'loc')
        loc.text = f"{self.site_url}/{url_relativa}"
        
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = lastmod.strftime('%Y-%m-%d')
        
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = changefreq
        
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = str(priority)
    
    def atualizar_sitemap(self, url_relativa, lastmod=None):
        """Atualiza sitemap com uma nova URL"""
        sitemap_path = self.docs_dir / "sitemap.xml"
        
        if not sitemap_path.exists():
            self.criar_sitemap()
            return
        
        try:
            tree = ET.parse(sitemap_path)
            urlset = tree.getroot()
            
            # Adicionar nova URL
            self.adicionar_url_sitemap(urlset, url_relativa, 0.6, 'monthly', lastmod)
            
            # Salvar
            xml_str = ET.tostring(urlset, encoding='unicode')
            xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
            
            with open(sitemap_path, 'w', encoding='utf-8') as f:
                f.write(xml_pretty)
                
        except Exception as e:
            print(f"   ⚠️  Erro ao atualizar sitemap: {e}")
    
    def criar_robots_txt(self):
        """Cria arquivo robots.txt"""
        robots_path = self.docs_dir / "robots.txt"
        
        robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/

Sitemap: {self.site_url}/sitemap.xml
"""
        
        try:
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            print(f"✅ Robots.txt criado")
        except Exception as e:
            print(f"❌ Erro ao criar robots.txt: {e}")
    
    # ==================== BACKUP E CONTROLE ====================
    
    def criar_backup_csv(self):
        """Cria backup do CSV"""
        csv_path = self.base_dir / "produtos.csv"
        
        if csv_path.exists():
            backup_dir = self.base_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"produtos_backup_{timestamp}.csv"
            
            try:
                shutil.copy2(csv_path, backup_path)
                print(f"📁 Backup criado: {backup_path.name}")
                return backup_path
            except Exception as e:
                print(f"❌ Erro ao criar backup: {e}")
        
        return None
    
    def atualizar_csv_apos_geracao(self, produto_data, caminho_artigo, status="completed"):
        """Atualiza o CSV após gerar artigo"""
        csv_path = self.base_dir / "produtos.csv"
        
        if not csv_path.exists():
            return False
        
        try:
            # Ler CSV
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                linhas = list(reader)
                cabecalho = reader.fieldnames
            
            # Atualizar linha correspondente
            produto_nome = produto_data.get('produto', '')
            for linha in linhas:
                if linha.get('produto') == produto_nome:
                    linha['status'] = status
                    linha['data_publicacao'] = datetime.now().strftime("%Y-%m-%d")
                    if caminho_artigo:
                        linha['url_publicada'] = str(caminho_artigo.relative_to(self.docs_dir).parent).replace("\\", "/")
                    break
            
            # Salvar CSV
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=cabecalho)
                writer.writeheader()
                writer.writerows(linhas)
            
            print(f"   📊 CSV atualizado: {produto_nome}")
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao atualizar CSV: {e}")
            return False
    
    def ler_csv_local(self):
        """Lê dados do CSV"""
        csv_path = self.base_dir / "produtos.csv"
        
        if not csv_path.exists():
            print("\n📝 Criando CSV de exemplo...")
            dados = [
                ["produto", "categoria", "tipo_artigo", "site_oficial", "links_afiliados", "status", "data_publicacao", "url_publicada"],
                ["Console Playstation 5 Slim", "games", "review", "https://playstation.com", "https://afiliado.com/ps5", "pending", "", ""],
                ["iPhone 15 Pro", "smartphones", "review", "https://apple.com", "https://afiliado.com/iphone", "pending", "", ""]
            ]
            
            try:
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(dados)
                print(f"✅ CSV criado: {csv_path}")
            except Exception as e:
                print(f"❌ Erro ao criar CSV: {e}")
                return []
        
        # Ler CSV
        produtos = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                produtos = list(reader)
            
            print(f"✅ {len(produtos)} produtos encontrados")
            return produtos
            
        except Exception as e:
            print(f"❌ Erro ao ler CSV: {e}")
            return []
    
    def mostrar_painel_controle(self):
        """Mostra dashboard de status"""
        print("\n" + "="*60)
        print("📊 PAINEL DE CONTROLE")
        print("="*60)
        
        produtos = self.ler_csv_local()
        
        if not produtos:
            print("Nenhum produto no CSV")
            return
        
        stats = {'total': 0, 'pending': 0, 'completed': 0}
        for p in produtos:
            stats['total'] += 1
            status = p.get('status', 'pending')
            if status == 'completed':
                stats['completed'] += 1
            else:
                stats['pending'] += 1
        
        print(f"📁 Total: {stats['total']}")
        print(f"✅ Concluídos: {stats['completed']}")
        print(f"⏳ Pendentes: {stats['pending']}")
        if stats['total'] > 0:
            print(f"🎯 Progresso: {(stats['completed']/stats['total']*100):.1f}%")
        
        # Artigos gerados
        artigos = list(self.docs_dir.glob("**/index.html"))
        print(f"📄 Artigos no site: {len(artigos)}")
    
    # ==================== PROCESSAMENTO PRINCIPAL ====================
    
    def processar_tabela_completa(self):
        """Processa todos os produtos do CSV"""
        print("\n" + "="*70)
        print("🚀 PROCESSAR TABELA COMPLETA")
        print("="*70)
        
        # Backup
        print("\n📁 Criando backup do CSV...")
        self.criar_backup_csv()
        
        # Ler produtos
        produtos = self.ler_csv_local()
        
        if not produtos:
            print("❌ Nenhum produto para processar")
            return
        
        # Configurar IA
        tem_ia = False
        if self.ia_api_key:
            usar_ia = input("Usar IA configurada? (s/n): ").strip().lower()
            if usar_ia == 's':
                tem_ia = True
            else:
                tem_ia = self.configurar_ia()
        else:
            tem_ia = self.configurar_ia()
        
        print(f"\n🔧 MODO: {'🤖 COM IA' if tem_ia else '📝 SEM IA'}")
        print("="*40)
        
        for i, produto_data in enumerate(produtos, 1):
            print(f"\n[{i}/{len(produtos)}] {'='*30}")
            
            # Extrair dados
            nome = produto_data.get('produto', '').strip()
            if not nome:
                continue
            
            categoria = produto_data.get('categoria', 'geral').strip().lower()
            tipo = produto_data.get('tipo_artigo', 'review').strip().lower()
            site_oficial = produto_data.get('site_oficial', '').strip()
            link_afiliado = produto_data.get('links_afiliados', '').strip()
            status = produto_data.get('status', 'pending').lower()
            
            # Pular se já concluído
            if status == 'completed':
                print(f"   ⏭️  Já concluído: {nome[:40]}")
                continue
            
            print(f"   📦 {nome}")
            print(f"   📁 {categoria} • {tipo}")
            
            # Gerar slug e título
            slug = self.criar_slug(nome)
            titulo = self.criar_titulo_seo(nome, tipo)
            
            # Gerar conteúdo
            if tem_ia:
                conteudo = self.gerar_conteudo_com_ia(nome, categoria, tipo, site_oficial, link_afiliado)
                if conteudo is None:
                    print("   ⚠️  IA falhou, usando conteúdo básico")
                    conteudo = self.gerar_conteudo_basico(nome, categoria, tipo, site_oficial, link_afiliado)
            else:
                conteudo = self.gerar_conteudo_basico(nome, categoria, tipo, site_oficial, link_afiliado)
            
            # Criar artigo
            try:
                caminho = self.criar_artigo_completo(
                    titulo=titulo,
                    conteudo_html=conteudo,
                    categoria=categoria,
                    produto_slug=slug,
                    tipo_artigo=tipo,
                    nome_original=nome,
                    site_oficial=site_oficial,
                    link_afiliado=link_afiliado
                )
                
                # Atualizar CSV
                if caminho:
                    self.atualizar_csv_apos_geracao(produto_data, caminho, "completed")
                    print(f"   ✅ Gerado com sucesso")
                else:
                    print(f"   ❌ Erro ao gerar artigo")
                    self.atualizar_csv_apos_geracao(produto_data, None, "error")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                self.atualizar_csv_apos_geracao(produto_data, None, "error")
                continue
            
            # Pausa para IA
            if tem_ia and i < len(produtos):
                delay = random.randint(2, 4)
                print(f"   ⏳ Aguardando {delay}s...")
                sleep(delay)
        
        print("\n" + "="*70)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("="*70)
        print(f"📊 {len(produtos)} produtos processados")
        print(f"📁 Artigos em: {self.docs_dir}/")
        print(f"🗺️  Sitemap: {self.site_url}/sitemap.xml")
        print("="*70)
    
    # ==================== MENU PRINCIPAL ====================
    
    def menu_principal(self):
        """Menu interativo"""
        while True:
            print("\n" + "="*60)
            print("📱 GERADOR REAL v5.0 - MENU PRINCIPAL")
            print("="*60)
            print("1. 🔍 Verificar estrutura")
            print("2. 🎨 Criar templates básicos")
            print("3. 📱 Gerar artigo de teste")
            print("4. ✍️  Gerar artigo manual")
            print("5. 🚀 PROCESSAR TABELA COMPLETA")
            print("6. 📊 Painel de controle")
            print("7. 🗺️  Criar/atualizar sitemap")
            print("8. ⚙️  Configurações")
            print("9. 🤖 Configurar IA")
            print("10. 📝 Editar conteúdo padrão")
            print("11. ❌ Sair")
            
            try:
                opcao = input("\n🎯 Escolha (1-11): ").strip()
                
                if opcao == "1":
                    self.verificar_estrutura()
                elif opcao == "2":
                    self.criar_templates_basicos()
                elif opcao == "3":
                    self.gerar_artigo_teste()
                elif opcao == "4":
                    self.gerar_artigo_manual()
                elif opcao == "5":
                    self.processar_tabela_completa()
                elif opcao == "6":
                    self.mostrar_painel_controle()
                elif opcao == "7":
                    self.criar_sitemap()
                elif opcao == "8":
                    self.menu_configuracoes()
                elif opcao == "9":
                    self.configurar_ia()
                elif opcao == "10":
                    self.editar_conteudo_padrao()
                elif opcao == "11":
                    print("\n👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def verificar_estrutura(self):
        """Verifica estrutura do sistema"""
        print("\n🔍 VERIFICANDO ESTRUTURA...")
        
        arquivos = [
            (self.includes_dir / "header.html", "Header"),
            (self.includes_dir / "footer.html", "Footer"),
            (self.docs_dir / "assets/css/style.css", "CSS"),
            (self.base_dir / "produtos.csv", "CSV Produtos"),
            (self.base_dir / "config.json", "Configurações"),
            (self.templates_dir / "review.txt", "Template Review"),
            (self.templates_dir / "comparativo.txt", "Template Comparativo"),
            (self.templates_dir / "guia.txt", "Template Guia"),
            (self.templates_dir / "analise.txt", "Template Análise")
        ]
        
        for caminho, nome in arquivos:
            if caminho.exists():
                print(f"✅ {nome}: OK")
            else:
                print(f"❌ {nome}: Não encontrado")
    
    def criar_templates_basicos(self):
        """Cria templates básicos"""
        print("\n🎨 CRIANDO TEMPLATES BÁSICOS...")
        
        # CSS básico se não existir
        css_path = self.docs_dir / "assets/css/style.css"
        if not css_path.exists():
            css = '''/* CSS Básico - Top Ofertas */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

/* Header */
.site-header { background: #2c3e50; color: white; padding: 1rem 0; }
.site-header .container { display: flex; justify-content: space-between; align-items: center; }
.logo a { color: white; text-decoration: none; font-size: 1.5rem; font-weight: bold; }
.main-nav a { color: white; text-decoration: none; margin-left: 20px; }

/* Main Content */
.main-container { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; padding: 30px 0; }
.content { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.article-meta { color: #666; font-size: 0.9rem; margin-bottom: 20px; }
.article-meta span { margin-right: 15px; }
.featured-image { width: 100%; height: 400px; object-fit: cover; border-radius: 8px; margin: 20px 0; }

/* Sidebar */
.sidebar { position: sticky; top: 20px; }
.widget { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.btn-cta { display: inline-block; background: #e74c3c; color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none; margin-top: 10px; }
.btn-sidebar { display: inline-block; background: #3498db; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; }

/* Footer */
.site-footer { background: #34495e; color: white; padding: 2rem 0; margin-top: 3rem; }
.footer-content { display: flex; justify-content: space-between; }
.copyright { text-align: center; margin-top: 20px; color: #bdc3c7; }

/* Responsive */
@media (max-width: 768px) { 
    .main-container { grid-template-columns: 1fr; }
    .site-header .container { flex-direction: column; text-align: center; }
    .main-nav { margin-top: 10px; }
    .main-nav a { margin: 0 10px; }
}'''
            
            try:
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(css)
                print("✅ CSS criado")
            except Exception as e:
                print(f"❌ Erro ao criar CSS: {e}")
        
        print("🎨 Templates básicos criados com sucesso!")
    
    def gerar_artigo_teste(self):
        """Gera artigo de teste"""
        print("\n🧪 GERANDO ARTIGO DE TESTE...")
        
        artigo = {
            'produto': 'Produto de Teste - Artigo Demonstrativo',
            'categoria': 'testes',
            'tipo_artigo': 'review',
            'site_oficial': 'https://exemplo.com',
            'links_afiliados': 'https://afiliado.com'
        }
        
        slug = self.criar_slug(artigo['produto'])
        titulo = self.criar_titulo_seo(artigo['produto'], artigo['tipo_artigo'])
        
        conteudo = self.gerar_conteudo_basico(
            artigo['produto'],
            artigo['categoria'],
            artigo['tipo_artigo'],
            artigo['site_oficial'],
            artigo['links_afiliados']
        )
        
        caminho = self.criar_artigo_completo(
            titulo=titulo,
            conteudo_html=conteudo,
            categoria=artigo['categoria'],
            produto_slug=slug,
            tipo_artigo=artigo['tipo_artigo'],
            nome_original=artigo['produto'],
            site_oficial=artigo['site_oficial'],
            link_afiliado=artigo['links_afiliados']
        )
        
        if caminho:
            print(f"\n✅ Artigo de teste criado:")
            print(f"   📁 {caminho}")
    
    def gerar_artigo_manual(self):
        """Gera artigo manual"""
        print("\n✍️  GERAR ARTIGO MANUAL")
        print("-"*40)
        
        try:
            produto = input("Nome do produto: ").strip() or "Produto Teste"
            categoria = input("Categoria: ").strip() or "testes"
            tipo = input("Tipo (review/comparativo/guia/analise): ").strip() or "review"
            site = input("Site oficial (opcional): ").strip() or "https://exemplo.com"
            link = input("Link afiliado (opcional): ").strip() or "https://afiliado.com"
            
            slug = self.criar_slug(produto)
            titulo = self.criar_titulo_seo(produto, tipo)
            
            print(f"\n📝 Confirmar criação?")
            print(f"   Produto: {produto}")
            print(f"   URL: {categoria}/{slug}/")
            
            if input("Continuar? (s/n): ").strip().lower() != 's':
                return
            
            # Perguntar se usa IA
            usar_ia = 'n'
            if self.ia_api_key:
                usar_ia = input("Usar IA? (s/n): ").strip().lower()
            
            if usar_ia == 's':
                conteudo = self.gerar_conteudo_com_ia(produto, categoria, tipo, site, link)
            else:
                conteudo = self.gerar_conteudo_basico(produto, categoria, tipo, site, link)
            
            caminho = self.criar_artigo_completo(
                titulo=titulo,
                conteudo_html=conteudo,
                categoria=categoria,
                produto_slug=slug,
                tipo_artigo=tipo,
                nome_original=produto,
                site_oficial=site,
                link_afiliado=link
            )
            
            if caminho:
                print(f"\n✅ Artigo criado: {caminho}")
            else:
                print("❌ Erro ao criar artigo")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def menu_configuracoes(self):
        """Menu de configurações"""
        print("\n⚙️  CONFIGURAÇÕES")
        print("="*40)
        
        print(f"1. 🌐 Site URL: {self.site_url}")
        print(f"2. 🏷️  Nome: {self.config['site']['name']}")
        print(f"3. 📝 Palavras: {self.config['content']['word_count']}")
        print("4. ↩️  Voltar")
        
        opcao = input("\nEscolha: ").strip()
        
        if opcao == "1":
            novo = input(f"Novo URL ({self.site_url}): ").strip()
            if novo:
                self.site_url = novo.rstrip('/')
                self.config['site']['url'] = self.site_url
                self.salvar_config()
                print("✅ URL atualizado")
        
        elif opcao == "2":
            novo = input(f"Novo nome ({self.config['site']['name']}): ").strip()
            if novo:
                self.config['site']['name'] = novo
                self.salvar_config()
                print("✅ Nome atualizado")
        
        elif opcao == "3":
            try:
                novo = int(input(f"Palavras ({self.config['content']['word_count']}): ").strip())
                if 500 <= novo <= 5000:
                    self.config['content']['word_count'] = novo
                    self.salvar_config()
                    print("✅ Configuração salva")
                else:
                    print("❌ Valor inválido")
            except:
                print("❌ Valor inválido")
    
    def editar_conteudo_padrao(self):
        """Mostra onde editar conteúdo padrão"""
        print("\n📝 EDITAR CONTEÚDO PADRÃO")
        print("="*40)
        print("Para editar conteúdo SEM IA, modifique:")
        print("1. Método: gerar_review_basico()")
        print("2. Método: gerar_comparativo_basico()")
        print("3. Método: gerar_guia_basico()")
        print("4. Método: gerar_analise_basica()")
        print("\n📁 Templates de prompt em: templates/")
        print("   - review.txt, comparativo.txt, guia.txt, analise.txt")
        print("\n💡 Dica: Use DeepSeek para conteúdo automático de alta qualidade!")
    
    def salvar_config(self):
        """Salva configurações"""
        try:
            with open(self.base_dir / "config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    try:
        # Verificar estrutura
        base_dir = Path(__file__).parent
        docs_dir = base_dir / "docs"
        
        if not docs_dir.exists():
            print("📁 Primeira execução - criando estrutura...")
            docs_dir.mkdir(exist_ok=True)
        
        # Iniciar sistema
        gerador = GeradorReal()
        
        # Criar homepage se não existir
        homepage = docs_dir / "index.html"
        if not homepage.exists():
            html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Ofertas - Reviews Honestos</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <script src="https://topofertas.reviewnexus.blog/assets/js/script.js" defer></script>
</head>
<body>
    <div id="header-placeholder"></div>
    
    <main class="container">
        <div class="hero">
            <h1>Bem-vindo ao Top Ofertas</h1>
            <p>Reviews honestos e análises detalhadas dos melhores produtos.</p>
            <p>Use o Gerador Real para criar artigos automaticamente.</p>
        </div>
        
        <div class="cta-buttons">
            <a href="games/index.html" class="btn">🎮 Games</a>
            <a href="smartphones/index.html" class="btn">📱 Smartphones</a>
            <a href="eletrodomesticos/index.html" class="btn">🏠 Eletrodomésticos</a>
            <a href="computadores/index.html" class="btn">💻 Computadores</a>
        </div>
    </main>
    
    <div id="footer-placeholder"></div>
    
    <script>
        fetch('includes/header.html')
            .then(r => r.text())
            .then(h => document.getElementById('header-placeholder').innerHTML = h);
        
        fetch('includes/footer.html')
            .then(r => r.text())
            .then(f => document.getElementById('footer-placeholder').innerHTML = f);
    </script>
</body>
</html>'''
            with open(homepage, 'w', encoding='utf-8') as f:
                f.write(html)
            print("✅ Homepage criada")
        
        # Executar menu
        gerador.menu_principal()
        
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        input("Pressione Enter...")