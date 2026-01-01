#!/usr/bin/env python3
"""
GERADOR REAL v6.0 - SISTEMA PROFISSIONAL AVANÇADO
SEO Avançado + Artigos Humanos + Funnel Completo + Multi-idioma
"""

from dotenv import load_dotenv
import os

# Carrega variáveis do .env ANTES de qualquer coisa
load_dotenv()

import json
import csv
import re
import random
import shutil
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from time import sleep
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
        self.templates_dir = self.base_dir / "templates"
        
        # Configurações de IA - AGORA SÓ DO .env
        self.ia_api_key = os.getenv("OPENROUTER_API_KEY")
        self.ia_provider = 'openrouter'
        self.has_requests = HAS_REQUESTS
        
        self.site_url = site_url.rstrip('/')
        
        print("=" * 70)
        print("🤖 GERADOR REAL v6.0 - SISTEMA PROFISSIONAL AVANÇADO")
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
        
        # Verificar IA
        self.verificar_ia()
        
        # Criar templates básicos se não existirem
        self.criar_templates_prompt_se_necessario()
        
        # Criar templates HTML básicos se não existirem
        self.criar_templates_basicos()
    
    def criar_estrutura_pastas(self):
        """Cria pastas necessárias"""
        pastas = [
            self.docs_dir / "assets" / "css",
            self.docs_dir / "assets" / "js",
            self.docs_dir / "assets" / "img",
            self.includes_dir,
            self.templates_dir,
            self.base_dir / "backups"
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
                "description": "Reviews honestos e análises detalhadas dos melhores produtos",
                "language": "pt-BR",
                "author": "Equipe Top Ofertas",
                "twitter": "@TopOfertas",
                "google_analytics": "",
                "default_image": "/assets/img/og-default.jpg"
            },
            "seo": {
                "default_priority": 0.8,
                "change_freq": "weekly",
                "enable_jsonld": True
            },
            "content": {
                "word_count": 2500,
                "enable_faq": True,
                "image_source": "unsplash",
                "use_ia_by_default": True,
                "default_ia_provider": "openrouter"
            },
            "funnel": {
                "enable_preland": True,
                "preland_suffix": "-guia-completo"
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
    
    def verificar_ia(self):
        """Verifica configuração da IA"""
        if self.ia_api_key:
            print(f"✅ API Key carregada do .env: Open Router")
            return True
        else:
            print("⚠️  OPENROUTER_API_KEY não encontrada no .env")
            print("💡 Crie um arquivo .env com: OPENROUTER_API_KEY=sua_chave_aqui")
            return False
    
    def criar_templates_prompt_se_necessario(self):
        """Cria templates de prompt se não existirem"""
        templates = {
            'review.txt': self.criar_template_review(),
            'guia.txt': self.criar_template_guia(),
            'preland.txt': self.criar_template_preland(),
            'comparativo.txt': self.criar_template_comparativo()
        }
        
        for nome, conteudo in templates.items():
            caminho = self.templates_dir / nome
            if not caminho.exists():
                try:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✅ Template criado: {nome}")
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
    
    def carregar_prompt_template(self, tipo_artigo, idioma='pt-BR'):
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
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = texto.encode('ASCII', 'ignore').decode('ASCII')
        
        # Para minúsculas e remove caracteres especiais
        slug = texto.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'[-]+', '-', slug)
        slug = slug.strip('-')
        
        return slug[:60]
    
    def criar_titulo_seo(self, produto, tipo_artigo, idioma='pt-BR'):
        """Cria título otimizado para SEO"""
        ano_atual = datetime.now().year
        
        # Títulos em diferentes idiomas
        titulos = {
            'pt-BR': {
                'review': [
                    f"{produto} - Análise Completa e Review {ano_atual}",
                    f"Vale a pena comprar {produto}? Review Honesto e Detalhado"
                ],
                'comparativo': [
                    f"Comparativo: {produto} vs Concorrentes {ano_atual}"
                ],
                'guia': [
                    f"Guia Completo: Como escolher {produto} {ano_atual}"
                ],
                'preland': [
                    f"{produto} Funciona Mesmo? Verdade Revelada {ano_atual}"
                ]
            },
            'en': {
                'review': [
                    f"{produto} - Complete Review and Honest Analysis {ano_atual}"
                ],
                'comparativo': [
                    f"Comparison: {produto} vs Competitors {ano_atual}"
                ],
                'guia': [
                    f"Complete Guide: How to Choose {produto} {ano_atual}"
                ],
                'preland': [
                    f"Does {produto} Really Work? The Truth Revealed"
                ]
            },
            'es': {
                'review': [
                    f"{produto} - Reseña Completa y Análisis Honesto {ano_atual}"
                ]
            }
        }
        
        # Normalizar idioma
        idioma_base = self.normalizar_idioma_base(idioma)
        
        # Buscar títulos no idioma ou usar português como fallback
        if idioma_base in titulos and tipo_artigo.lower() in titulos[idioma_base]:
            opcoes = titulos[idioma_base][tipo_artigo.lower()]
        else:
            opcoes = titulos['pt-BR'][tipo_artigo.lower()] if tipo_artigo.lower() in titulos['pt-BR'] else [f"{produto} - {tipo_artigo.title()}"]
        
        return random.choice(opcoes)
    
    def normalizar_idioma_base(self, idioma):
        """Normaliza código de idioma para base"""
        idioma = idioma.lower()
        
        if idioma.startswith('pt'):
            return 'pt-BR'
        elif idioma.startswith('en'):
            return 'en'
        elif idioma.startswith('es'):
            return 'es'
        else:
            return 'pt-BR'
    
    def normalizar_idioma_html(self, idioma):
        """Normaliza código de idioma para tag HTML lang"""
        idioma = idioma.lower()
        
        if idioma.startswith('pt'):
            return 'pt-BR'
        elif idioma.startswith('en'):
            return 'en'
        elif idioma.startswith('es'):
            return 'es'
        else:
            return 'pt-BR'
    
    # ==================== SEO AVANÇADO ====================
    
    def criar_meta_tags_seo(self, titulo, descricao, keywords, url_relativa, imagem=None, idioma='pt-BR'):
        """Cria todas as meta tags SEO avançadas"""
        url_completa = f"{self.site_url}/{url_relativa}"
        
        if not imagem:
            imagem = f"{self.site_url}{self.config['site']['default_image']}"
        
        # Criar descrição otimizada
        descricao_og = descricao[:155] + "..." if len(descricao) > 155 else descricao
        
        # Mapear locale para Open Graph
        locale_map = {
            'pt-br': 'pt_BR',
            'en': 'en_US',
            'es': 'es_ES'
        }
        
        idioma_lower = idioma.lower()
        og_locale = locale_map.get(idioma_lower, 'pt_BR')
        
        meta_tags = f'''    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <meta name="description" content="{descricao_og}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{self.config['site']['author']}">
    <meta name="robots" content="index, follow">
    <meta name="language" content="{self.normalizar_idioma_html(idioma)}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{titulo}">
    <meta property="og:description" content="{descricao_og}">
    <meta property="og:image" content="{imagem}">
    <meta property="og:url" content="{url_completa}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{self.config['site']['name']}">
    <meta property="og:locale" content="{og_locale}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{titulo}">
    <meta name="twitter:description" content="{descricao_og}">
    <meta name="twitter:image" content="{imagem}">
    
    <!-- Canonical -->
    <link rel="canonical" href="{url_completa}">
    
    <!-- Schema.org -->
    {self.criar_jsonld_avancado(titulo, descricao_og, url_completa, imagem, idioma)}
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- CSS -->
    <link rel="stylesheet" href="{self.calcular_caminho_relativo(url_relativa, 'assets/css/style.css')}">
    
    <!-- Google Analytics -->
    {self.criar_google_analytics()}'''
        
        return meta_tags
    
    def criar_jsonld_avancado(self, titulo, descricao, url, imagem=None, idioma='pt-BR'):
        """Cria JSON-LD Schema.org avançado"""
        if not imagem:
            imagem = f"{self.site_url}{self.config['site']['default_image']}"
        
        # Determinar linguagem para Schema.org
        in_language_map = {
            'pt-br': 'Portuguese',
            'en': 'English',
            'es': 'Spanish'
        }
        
        idioma_lower = idioma.lower()
        in_language = in_language_map.get(idioma_lower, 'Portuguese')
        
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
                "name": self.config['site']['author'],
                "url": self.site_url
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
            },
            "inLanguage": in_language
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
                'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200&h=630&fit=crop'
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
            ],
            'healthcare': [
                'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&h=630&fit=crop'
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
        """Configura a API de IA - SIMPLIFICADO PARA .env"""
        if not self.has_requests:
            print("❌ IA não disponível: biblioteca 'requests' não instalada")
            print("💡 Execute: pip install requests")
            return False
        
        print("\n" + "="*50)
        print("🌐 CONFIGURAÇÃO DA IA")
        print("="*50)
        
        if self.ia_api_key:
            print(f"✅ API já configurada via .env: Open Router")
            usar_ia = input("Usar IA? (s/n): ").strip().lower()
            if usar_ia == 's':
                return True
        else:
            print("⚠️  OPENROUTER_API_KEY não encontrada no .env")
            print("💡 Crie um arquivo .env com: OPENROUTER_API_KEY=sua_chave_aqui")
        
        print("⚠️  IA não configurada. Usando conteúdo básico.")
        return False
    
    def gerar_conteudo_com_ia(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Gera conteúdo usando IA com Open Router"""
        
        if not self.ia_api_key or not self.has_requests:
            print("   ⚠️  IA não disponível, usando conteúdo básico")
            return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
        
        print(f"   🤖 Gerando conteúdo com IA (Open Router) em {idioma.upper()}...")
        
        # Criar prompt considerando o idioma
        prompt = self.criar_prompt_ia_completo(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma, palavras_chave)
        
        try:
            conteudo = self.chamar_openrouter_api(prompt, idioma)
            
            if conteudo:
                return conteudo
            else:
                print("   ⚠️  IA falhou, usando conteúdo básico")
                return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
                
        except Exception as e:
            print(f"   ⚠️  Erro na IA: {e}")
            return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
    
    def chamar_openrouter_api(self, prompt, idioma='pt-BR'):
        """Chama API do Open Router usando .env"""
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        
        if not OPENROUTER_API_KEY:
            print("❌ ERRO: OPENROUTER_API_KEY não encontrada")
            return None
        
        OPENROUTER_MODEL = "deepseek/deepseek-chat"
        
        # Mensagem do sistema baseada no idioma
        system_messages = {
            'pt-BR': "Você é um especialista brasileiro em SEO e criação de conteúdo para reviews de produtos. Crie conteúdo 100% em português do Brasil, natural e humano.",
            'en': "You are an English SEO and product review content creation expert. Create content 100% in English, natural and human-like.",
            'es': "Eres un experto español en SEO y creación de contenido para reseñas de productos. Crea conteúdo 100% en español, natural y humano."
        }
        
        idioma_base = self.normalizar_idioma_base(idioma)
        system_message = system_messages.get(idioma_base, system_messages['pt-BR'])
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Gerador Real v6.0"
        }
        
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                conteudo = result["choices"][0]["message"]["content"]
                conteudo = self.limpar_resposta_ia(conteudo)
                print(f"   ✅ Open Router gerou {len(conteudo)} caracteres em {idioma.upper()}")
                return conteudo
            else:
                print(f"   ❌ Erro Open Router ({response.status_code}): {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro na requisição ao Open Router: {e}")
            return None
    
    def criar_prompt_ia_completo(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Cria prompt completo baseado no tipo de artigo e idioma"""
        template = self.carregar_prompt_template(tipo_artigo, idioma)
        
        if template:
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
            prompt = prompt.replace("{IDIOMA}", idioma.upper())
            
            if palavras_chave:
                prompt = prompt.replace("{PALAVRAS_CHAVE}", palavras_chave)
            
            return prompt
        
        # Fallback para prompt padrão
        return self.criar_prompt_padrao(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
    
    def criar_prompt_padrao(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR'):
        """Cria prompt padrão para IA"""
        if tipo_artigo.lower() == 'review':
            return f"""Crie um review detalhado sobre {produto} em {idioma}.

Produto: {produto}
Categoria: {categoria}
Idioma: {idioma}

Requisitos:
1. Título atrativo
2. Introdução envolvente
3. Especificações técnicas em tabela HTML
4. Prós e contras
5. Análise de custo-benefício
6. Recomendação final
7. Links relevantes

Site oficial: {site_oficial}
Link afiliado: {link_afiliado}

Retorne apenas HTML válido pronto para publicação."""
        else:
            return f"""Crie um artigo sobre {produto} em {idioma}.

Tipo: {tipo_artigo}
Produto: {produto}
Categoria: {categoria}

Inclua:
- Título SEO
- Conteúdo informativo
- Formatação HTML básica
- Links relevantes

Idioma: {idioma}"""
    
    def criar_template_review(self):
        """Cria template para review.txt"""
        return """# TEMPLATE PARA REVIEW - {PRODUTO}

## INFORMAÇÕES BÁSICAS:
- PRODUTO: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}
- SITE OFICIAL: {SITE_OFICIAL}
- LINK AFILIADO: {LINK_AFILIADO}

## ESTRUTURA DO REVIEW:
1. INTRODUÇÃO ATRAENTE
2. ESPECIFICAÇÕES TÉCNICAS (tabela HTML)
3. ANÁLISE DE DESIGN E QUALIDADE
4. TESTES E PERFORMANCE PRÁTICA
5. PRÓS E CONTRAS HONESTOS
6. COMPARAÇÃO COM CONCORRENTES
7. ANÁLISE DE CUSTO-BENEFÍCIO
8. PARA QUEM É RECOMENDADO
9. FAQ COMPLETO (6-8 perguntas)
10. ONDE COMPRAR

## TOM E ESTILO:
- Profissional mas acessível
- Imparcial (mostre prós e contras)
- Informativo e prático
- Confiável e honesto

## REQUISITOS TÉCNICOS:
- HTML válido pronto para publicação
- Use tags semânticas (h2, h3, p, ul, li, table, etc.)
- Links com atributos rel="nofollow" ou "nofollow sponsored"
- Otimizado para SEO
- Conteúdo 100% em {IDIOMA}

Retorne APENAS o HTML completo do artigo, sem comentários extras."""
    
    def criar_template_guia(self):
        """Cria template para guia.txt"""
        return """# TEMPLATE PARA GUIA - Como escolher {PRODUTO}

## INFORMAÇÕES BÁSICAS:
- PRODUTO: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}

## ESTRUTURA DO GUIA:
1. INTRODUÇÃO EDUCATIVA
2. FATORES CRÍTICOS DE ESCOLHA
3. TERMINOLOGIA TÉCNICA EXPLICADA
4. MARCAS E MODELOS RECOMENDADOS
5. FAIXAS DE PREÇO E O QUE ESPERAR
6. DICAS DE MANUTENÇÃO
7. CHECKLIST ANTES DE COMPRAR
8. ONDE COMPRAR COM SEGURANÇA
9. RECOMENDAÇÃO FINAL

## TOM E ESTILO:
- Educativo e detalhado
- Imparcial e objetivo
- Prático e aplicável
- Acessível para todos os níveis

Retorne APENAS o HTML completo do guia, sem comentários extras."""
    
    def criar_template_preland(self):
        """Cria template para preland.txt"""
        return """# TEMPLATE PARA PRE-LANDING PAGE - {PRODUTO}

## INFORMAÇÕES BÁSICAS:
- PRODUTO: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}
- LINK PRINCIPAL: {LINK_AFILIADO}

## ESTRUTURA DA PRE-LANDING:
1. TÍTULO IMPACTANTE (focado na dor)
2. AMPLIFICAÇÃO DO PROBLEMA
3. APRESENTAÇÃO DA SOLUÇÃO ({PRODUTO})
4. BENEFÍCIOS EMOCIONAIS E RACIONAIS
5. PROVA SOCIAL (depoimentos)
6. DIFERENCIAIS COMPETITIVOS
7. OFERTA IRRECUSÁVEL (desconto + bônus)
8. CHAMADA PARA AÇÃO
9. GARANTIA E SEGURANÇA
10. FAQ ANTIOBJEÇÕES

## TÉCNICAS DE PERSUASÃO:
- Gatilhos mentais (urgência, escassez, prova social)
- Copywriting emocional
- Storytelling persuasivo
- Foco na transformação

## TOM E ESTILO:
- Persuasivo e urgente
- Empático e compreensivo
- Confiante e autoritário
- Claro e direto

Retorne APENAS o HTML completo da pre-landing, sem comentários extras."""
    
    def criar_template_comparativo(self):
        """Cria template para comparativo.txt"""
        return """# TEMPLATE PARA COMPARATIVO - {PRODUTO} vs Concorrentes

## INFORMAÇÕES BÁSICAS:
- PRODUTO PRINCIPAL: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}

## ESTRUTURA DO COMPARATIVO:
1. INTRODUÇÃO À CATEGORIA
2. TABELA COMPARATIVA COMPLETA
3. ANÁLISE INDIVIDUAL DETALHADA
4. COMPARAÇÃO PONTO A PONTO
5. TESTES PRÁTICOS COMPARATIVOS
6. ANÁLISE DE CUSTO-BENEFÍCIO
7. RECOMENDAÇÕES POR PERFIL
8. CONCLUSÃO E VENCEDORES

## TOM E ESTILO:
- Objetivo e imparcial
- Detalhado e completo
- Prático e útil
- Baseado em fatos

Retorne APENAS o HTML completo do comparativo, sem comentários extras."""
    
    def limpar_resposta_ia(self, texto):
        """Limpa a resposta da IA"""
        # Remove blocos de código markdown
        texto = re.sub(r'```(?:html)?\s*', '', texto)
        texto = re.sub(r'\s*```', '', texto)
        
        # Remove explicações iniciais
        padroes = [
            r'^.*?(?=<h2|<div|<p|<h1|<h3|<table|<ul|<ol)',
            r'^Aqui está.*?(?=<)',
            r'^Segue.*?(?=<)',
            r'^Here is.*?(?=<)',
            r'^Following.*?(?=<)'
        ]
        
        for padrao in padroes:
            texto = re.sub(padrao, '', texto, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove comentários HTML
        texto = re.sub(r'<!--.*?-->', '', texto, flags=re.DOTALL)
        
        # Remove espaços em excesso
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        texto = texto.strip()
        
        return texto
    
    # ==================== GERAÇÃO BÁSICA (SEM IA) ====================
    
    def gerar_conteudo_basico(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera conteúdo básico SEM IA com qualidade"""
        if tipo_artigo.lower() == 'review':
            return self.gerar_review_basico(produto, categoria, site_oficial, link_afiliado, idioma)
        elif tipo_artigo.lower() == 'guia':
            return self.gerar_guia_basico(produto, categoria, site_oficial, link_afiliado, idioma)
        elif tipo_artigo.lower() == 'preland':
            return self.gerar_preland_basica(produto, categoria, site_oficial, link_afiliado, idioma)
        else:
            return self.gerar_review_basico(produto, categoria, site_oficial, link_afiliado, idioma)
    
    def gerar_review_basico(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera review básico com conteúdo realista"""
        
        if idioma.lower().startswith('en'):
            return f"""
<h2>Complete Review: {produto}</h2>

<p>In today's competitive market, {produto} stands out as a notable option in the {categoria} category. This comprehensive review examines every aspect to help you make an informed decision.</p>

<h3>Technical Specifications</h3>
<table>
    <tr>
        <th>Specification</th>
        <th>Details</th>
    </tr>
    <tr>
        <td>Main Feature</td>
        <td>High performance and reliability</td>
    </tr>
    <tr>
        <td>Build Quality</td>
        <td>Premium materials and solid construction</td>
    </tr>
    <tr>
        <td>Performance</td>
        <td>Consistent and efficient operation</td>
    </tr>
    <tr>
        <td>Warranty</td>
        <td>Standard manufacturer warranty</td>
    </tr>
</table>

<h3>Advantages</h3>
<ul>
    <li><strong>Reliable Performance:</strong> Consistent results under different conditions</li>
    <li><strong>Good Build Quality:</strong> Durable construction that lasts</li>
    <li><strong>User-Friendly:</strong> Easy to set up and use</li>
    <li><strong>Good Value:</strong> Competitive pricing for features offered</li>
</ul>

<h3>Disadvantages</h3>
<ul>
    <li><strong>Learning Curve:</strong> Some features require time to master</li>
    <li><strong>Availability:</strong> May be out of stock during high demand</li>
    <li><strong>Accessories:</strong> Some accessories sold separately</li>
</ul>

<div class="buy-recommendation">
    <h3>Where to Buy {produto}</h3>
    <p>For the best price and guaranteed authenticity, we recommend purchasing through our trusted partner:</p>
    <a href="{link_afiliado}" class="buy-button" target="_blank" rel="nofollow sponsored">Check Current Price →</a>
    <p class="affiliate-disclosure"><small>Disclosure: We may earn a commission at no extra cost to you.</small></p>
</div>
"""
        else:
            return f"""
<h2>Review Completo: {produto}</h2>

<p>No mercado competitivo atual, {produto} se destaca como uma opção notável na categoria {categoria}. Este review completo examina todos os aspectos para ajudá-lo a tomar uma decisão informada.</p>

<h3>Especificações Técnicas</h3>
<table>
    <tr>
        <th>Especificação</th>
        <th>Detalhes</th>
    </tr>
    <tr>
        <td>Característica Principal</td>
        <td>Alta performance e confiabilidade</td>
    </tr>
    <tr>
        <td>Qualidade de Construção</td>
        <td>Materiais premium e construção sólida</td>
    </tr>
    <tr>
        <td>Performance</td>
        <td>Operação consistente e eficiente</td>
    </tr>
    <tr>
        <td>Garantia</td>
        <td>Garantia padrão do fabricante</td>
    </tr>
</table>

<h3>Vantagens</h3>
<ul>
    <li><strong>Performance Confiável:</strong> Resultados consistentes em diferentes condições</li>
    <li><strong>Boa Qualidade de Construção:</strong> Construção durável que perdura</li>
    <li><strong>Fácil de Usar:</strong> Simples de configurar e operar</li>
    <li><strong>Bom Custo-Benefício:</strong> Preço competitivo pelas funcionalidades oferecidas</li>
</ul>

<h3>Desvantagens</h3>
<ul>
    <li><strong>Curva de Aprendizado:</strong> Algumas funcionalidades exigem tempo para dominar</li>
    <li><strong>Disponibilidade:</strong> Pode estar esgotado em períodos de alta demanda</li>
    <li><strong>Acessórios:</strong> Alguns acessórios vendidos separadamente</li>
</ul>

<div class="onde-comprar">
    <h3>Onde Comprar {produto}</h3>
    <p>Para o melhor preço e autenticidade garantida, recomendamos comprar através do nosso parceiro confiável:</p>
    <a href="{link_afiliado}" class="btn-comprar" target="_blank" rel="nofollow sponsored">Ver Preço Atual →</a>
    <p class="aviso-afiliado"><small>Aviso: Podemos receber uma comissão sem custo adicional para você.</small></p>
</div>
"""
    
    def gerar_guia_basico(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera guia básico"""
        if idioma.lower().startswith('en'):
            return f"""
<h2>Complete Guide: How to Choose {produto}</h2>

<p>Choosing the right {produto} can be challenging. This comprehensive guide will help you make an informed decision.</p>

<h3>Key Factors to Consider</h3>
<ul>
    <li><strong>Performance:</strong> Check the specifications and user reviews</li>
    <li><strong>Compatibility:</strong> Ensure it works with your existing setup</li>
    <li><strong>Budget:</strong> Set a realistic budget range</li>
    <li><strong>Brand Reputation:</strong> Research the manufacturer's track record</li>
</ul>

<h3>Recommended Models</h3>
<p>Based on current market analysis, here are the top recommendations:</p>
<ul>
    <li><strong>Entry Level:</strong> Basic features, affordable price</li>
    <li><strong>Mid Range:</strong> Best value for money</li>
    <li><strong>Premium:</strong> Top performance with advanced features</li>
</ul>

<h3>Where to Buy Safely</h3>
<p>For guaranteed authenticity and best prices, purchase from authorized sellers:</p>
<a href="{link_afiliado}" class="btn-comprar" target="_blank" rel="nofollow sponsored">View Current Deals →</a>
"""
        else:
            return f"""
<h2>Guia Completo: Como Escolher {produto}</h2>

<p>Escolher o {produto} ideal pode ser desafiador. Este guia completo vai ajudá-lo a tomar uma decisão informada.</p>

<h3>Fatores Importantes</h3>
<ul>
    <li><strong>Performance:</strong> Verifique especificações e avaliações de usuários</li>
    <li><strong>Compatibilidade:</strong> Certifique-se que funciona com seu setup atual</li>
    <li><strong>Orçamento:</strong> Defina uma faixa de preço realista</li>
    <li><strong>Reputação da Marca:</strong> Pesquise o histórico do fabricante</li>
</ul>

<h3>Modelos Recomendados</h3>
<p>Baseado na análise atual do mercado, aqui estão as principais recomendações:</p>
<ul>
    <li><strong>Básico:</strong> Funcionalidades essenciais, preço acessível</li>
    <li><strong>Intermediário:</strong> Melhor custo-benefício</li>
    <li><strong>Premium:</strong> Performance superior com recursos avançados</li>
</ul>

<h3>Onde Comprar com Segurança</h3>
<p>Para autenticidade garantida e melhores preços, compre em vendedores autorizados:</p>
<a href="{link_afiliado}" class="btn-comprar" target="_blank" rel="nofollow sponsored">Ver Ofertas Atuais →</a>
"""
    
    def gerar_preland_basica(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera pre-landing page básica"""
        
        if idioma.lower().startswith('en'):
            return f"""
<div class="preland-hero">
    <h1>Discover {produto} - The Ultimate Solution!</h1>
    <p class="subtitle">Transform your experience with this innovative product.</p>
</div>

<div class="benefits-grid">
    <div class="benefit">
        <h3>✅ Proven Results</h3>
        <p>Thousands of satisfied customers worldwide</p>
    </div>
    <div class="benefit">
        <h3>✅ Easy to Use</h3>
        <p>Simple setup and intuitive operation</p>
    </div>
    <div class="benefit">
        <h3>✅ Great Value</h3>
        <p>Premium quality at an affordable price</p>
    </div>
</div>

<div class="offer-section">
    <h2>Special Limited Time Offer</h2>
    
    <div class="offer-details">
        <div class="current-price">Today Only: Special Price</div>
        <div class="savings">Save up to 30% + Free Shipping</div>
    </div>
    
    <div class="cta-main">
        <a href="{link_afiliado}" class="cta-button" target="_blank" rel="nofollow sponsored">
            <span class="cta-text">Get {produto} Now</span>
            <span class="cta-subtext">Limited Stock Available</span>
        </a>
        <p class="guarantee">✅ 30-Day Money Back Guarantee</p>
    </div>
</div>
"""
        else:
            return f"""
<div class="preland-hero">
    <h1>Descubra {produto} - A Solução Definitiva!</h1>
    <p class="subtitle">Transforme sua experiência com este produto inovador.</p>
</div>

<div class="benefits-grid">
    <div class="benefit">
        <h3>✅ Resultados Comprovados</h3>
        <p>Milhares de clientes satisfeitos mundialmente</p>
    </div>
    <div class="benefit">
        <h3>✅ Fácil de Usar</h3>
        <p>Configuração simples e operação intuitiva</p>
    </div>
    <div class="benefit">
        <h3>✅ Ótimo Custo-Benefício</h3>
        <p>Qualidade premium a um preço acessível</p>
    </div>
</div>

<div class="oferta-section">
    <h2>Oferta Especial por Tempo Limitado</h2>
    
    <div class="oferta-detalhes">
        <div class="preco-atual">Apenas Hoje: Preço Especial</div>
        <div class="economia">Economize até 30% + Frete Grátis</div>
    </div>
    
    <div class="cta-principal">
        <a href="{link_afiliado}" class="cta-button" target="_blank" rel="nofollow sponsored">
            <span class="cta-text">Adquira {produto} Agora</span>
            <span class="cta-subtext">Estoque Limitado</span>
        </a>
        <p class="garantia">✅ Garantia de 30 Dias</p>
    </div>
</div>
"""
    
    # ==================== TEMPLATES HTML BÁSICOS ====================
    
    def criar_templates_basicos(self):
        """Cria templates básicos"""
        print("\n🎨 CRIANDO TEMPLATES BÁSICOS...")
        
        # CSS básico se não existir
        css_path = self.docs_dir / "assets/css/style.css"
        if not css_path.exists():
            css = '''/* CSS Básico - Top Ofertas v6.0 */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

/* Header */
.site-header { background: linear-gradient(135deg, #1a3a8f 0%, #2c3e50 100%); color: white; padding: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.site-header .container { display: flex; justify-content: space-between; align-items: center; }
.logo a { color: white; text-decoration: none; font-size: 1.5rem; font-weight: bold; }
.main-nav { display: flex; gap: 20px; }
.main-nav a { color: white; text-decoration: none; padding: 5px 10px; border-radius: 4px; transition: background 0.3s; }
.main-nav a:hover { background: rgba(255,255,255,0.1); }

/* Main Content */
.main-container { display: grid; grid-template-columns: 2fr 1fr; gap: 40px; padding: 40px 0; }
@media (max-width: 992px) { .main-container { grid-template-columns: 1fr; } }
.content { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.article-meta { display: flex; flex-wrap: wrap; gap: 15px; color: #666; font-size: 0.9rem; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
.article-meta span { display: flex; align-items: center; gap: 5px; }
.featured-image { width: 100%; height: 400px; object-fit: cover; border-radius: 10px; margin: 25px 0; }

/* Sidebar */
.sidebar { position: sticky; top: 20px; align-self: start; }
.widget { background: white; padding: 25px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 3px 15px rgba(0,0,0,0.05); }
.widget h3 { color: #1a3a8f; margin-bottom: 15px; }
.btn-sidebar { display: inline-block; background: #3498db; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; margin-top: 10px; }

/* CTA */
.cta { background: linear-gradient(135deg, #1a3a8f 0%, #2c3e50 100%); color: white; padding: 30px; border-radius: 12px; margin: 40px 0; text-align: center; }
.btn-cta { display: inline-block; background: #ff6b6b; color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; margin: 15px 0; }

/* Footer */
.site-footer { background: #2c3e50; color: white; padding: 3rem 0; margin-top: 4rem; }
.footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 40px; }
.copyright { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #34495e; }

@media (max-width: 768px) { 
    .site-header .container { flex-direction: column; text-align: center; }
    .main-nav { margin-top: 15px; flex-wrap: wrap; justify-content: center; }
    .content, .widget { padding: 20px; }
}'''
            
            try:
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(css)
                print("✅ CSS criado")
            except Exception as e:
                print(f"❌ Erro ao criar CSS: {e}")
        
        # Criar sidebar.html template se não existir
        sidebar_path = self.includes_dir / "sidebar.html"
        if not sidebar_path.exists():
            sidebar_content = '''<!-- Sidebar Template -->
<div class="widget">
    <h3><i class="fas fa-bolt"></i> Oferta Especial</h3>
    <p><strong>Produto em Destaque</strong></p>
    <p>Aproveite nossa oferta por tempo limitado!</p>
    <a href="#" class="btn-sidebar">Saiba Mais</a>
</div>

<div class="widget">
    <h3><i class="fas fa-link"></i> Mais Produtos</h3>
    <p>Confira outros produtos relacionados:</p>
    <ul>
        <li><a href="#">Produto Relacionado 1</a></li>
        <li><a href="#">Produto Relacionado 2</a></li>
        <li><a href="#">Produto Relacionado 3</a></li>
    </ul>
</div>

<div class="widget">
    <h3><i class="fas fa-info-circle"></i> Informações</h3>
    <ul>
        <li><a href="../sobre-nos.html">Sobre Nós</a></li>
        <li><a href="../contato.html">Contato</a></li>
        <li><a href="../politica-de-privacidade.html">Privacidade</a></li>
    </ul>
</div>'''
            
            try:
                with open(sidebar_path, 'w', encoding='utf-8') as f:
                    f.write(sidebar_content)
                print("✅ Sidebar template criado")
            except Exception as e:
                print(f"❌ Erro ao criar sidebar template: {e}")
        
        # Criar header.html se não existir
        header_path = self.includes_dir / "header.html"
        if not header_path.exists():
            header_content = '''<header class="site-header">
    <div class="container">
        <div class="logo">
            <a href="../index.html">🔥 Top Ofertas</a>
        </div>
        <nav class="main-nav">
            <a href="../index.html">Home</a>
            <a href="../games/index.html">Games</a>
            <a href="../smartphones/index.html">Smartphones</a>
            <a href="../eletrodomesticos/index.html">Eletrodomésticos</a>
            <a href="../computadores/index.html">Computadores</a>
            <a href="../healthcare/index.html">Healthcare</a>
        </nav>
    </div>
</header>'''
            
            try:
                with open(header_path, 'w', encoding='utf-8') as f:
                    f.write(header_content)
                print("✅ Header template criado")
            except Exception as e:
                print(f"❌ Erro ao criar header template: {e}")
        
        # Criar footer.html se não existir
        footer_path = self.includes_dir / "footer.html"
        if not footer_path.exists():
            footer_content = f'''<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h3>Top Ofertas</h3>
                <p>Reviews honestos e análises detalhadas.</p>
            </div>
            <div class="footer-section">
                <h4>Links</h4>
                <a href="../sobre-nos.html">Sobre Nós</a>
                <a href="../contato.html">Contato</a>
                <a href="../politica-de-privacidade.html">Política de Privacidade</a>
            </div>
        </div>
        <p class="copyright">&copy; {datetime.now().year} Top Ofertas. Todos os direitos reservados.</p>
    </div>
</footer>'''
            
            try:
                with open(footer_path, 'w', encoding='utf-8') as f:
                    f.write(footer_content)
                print("✅ Footer template criado")
            except Exception as e:
                print(f"❌ Erro ao criar footer template: {e}")
        
        print("🎨 Templates básicos criados com sucesso!")

    # ==================== CRIAÇÃO DE ARTIGOS ====================
    
    def criar_artigo_completo(self, titulo, conteudo_html, categoria, produto_slug, tipo_artigo, nome_original, site_oficial, link_afiliado, idioma='pt-BR', is_preland=False):
        """Cria artigo HTML completo"""
        
        print(f"   📝 Criando artigo ({tipo_artigo}) em {idioma.upper()}: {titulo[:60]}...")
        
        # Criar pastas
        categoria_dir = self.docs_dir / categoria
        categoria_dir.mkdir(exist_ok=True)
        
        # Para pre-landing pages, usar sufixo diferente
        if is_preland:
            produto_slug = f"{produto_slug}-guia-completo"
        
        produto_dir = categoria_dir / produto_slug
        produto_dir.mkdir(exist_ok=True)
        
        # Caminho do arquivo
        caminho_arquivo = produto_dir / "index.html"
        url_relativa = f"{categoria}/{produto_slug}/"
        
        # Carregar templates do header e footer
        header = self.carregar_template("header.html") or self.criar_header_basico(idioma)
        footer = self.carregar_template("footer.html") or self.criar_footer_basico(idioma)
        
        # Criar sidebar dinâmica SEM PREÇOS
        sidebar_content = self.criar_sidebar_conteudo(categoria, produto_slug, nome_original, link_afiliado, idioma, is_preland)
        
        # Se estiver usando IA, podemos pedir para a IA criar uma sidebar mais personalizada
        if self.ia_api_key and self.has_requests and tipo_artigo.lower() != 'preland':
            # Tentar criar sidebar mais sofisticada com IA
            sidebar_ia = self.criar_sidebar_com_ia(nome_original, categoria, link_afiliado, idioma)
            if sidebar_ia:
                sidebar_content = sidebar_ia
        
        # Criar descrição SEO
        if idioma.lower().startswith('en'):
            descricao_seo = f"Complete {tipo_artigo} of {nome_original}. Detailed analysis, specifications, where to buy and if it's worth it."
        else:
            descricao_seo = f"{tipo_artigo.title()} completo do {nome_original}. Análise detalhada, especificações, onde comprar e se vale a pena."
        
        # Palavras-chave SEO
        keywords_seo = f"{nome_original}, {categoria}, {tipo_artigo}, comprar, preço, análise, review"
        
        # Obter imagem
        imagem_principal = self.obter_url_imagem(nome_original, categoria)
        alt_imagem = self.criar_alt_imagem(nome_original)
        
        # Normalizar código de idioma para HTML
        idioma_html = self.normalizar_idioma_html(idioma)
        
        # HTML do artigo
        html = f'''<!DOCTYPE html>
<html lang="{idioma_html}">
<head>
    {self.criar_meta_tags_seo(titulo, descricao_seo, keywords_seo, url_relativa, imagem_principal, idioma)}
    <script src="https://topofertas.reviewnexus.blog/assets/js/script.js" defer></script>
</head>
<body>
    {header}
    
    <main class="container main-container">
        <article class="content">
            <div class="article-meta">
                <span><i class="far fa-calendar-alt"></i> {datetime.now().strftime('%d/%m/%Y')}</span>
                <span><i class="far fa-user"></i> {self.config['site']['author']}</span>
                <span><i class="far fa-clock"></i> {random.randint(5, 12)} min</span>
                <span><i class="fas fa-tag"></i> {categoria.title()}</span>
            </div>

            <h1>{titulo}</h1>

            <img src="{imagem_principal}" alt="{alt_imagem}" class="featured-image">

            <div class="article-content">
                {conteudo_html if conteudo_html else '<p>Conteúdo do artigo...</p>'}
            </div>

            {self.criar_secao_cta(nome_original, link_afiliado, idioma, is_preland)}
        </article>

        <aside class="sidebar">
            {sidebar_content}
        </aside>
    </main>
    
    {footer}
</body>
</html>'''
        
        # Salvar arquivo
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"   ✅ Artigo salvo em {idioma.upper()}: {categoria}/{produto_slug}/index.html")
            
            # Atualizar índice da categoria
            self.atualizar_index_categoria(categoria, idioma)
            
            # Atualizar sitemap
            self.atualizar_sitemap(url_relativa, datetime.now())
            
            return caminho_arquivo
        except Exception as e:
            print(f"   ❌ Erro ao salvar artigo: {e}")
            return None
    
    def criar_sidebar_com_ia(self, produto, categoria, link_afiliado, idioma='pt-BR'):
        """Cria sidebar personalizada com IA SEM PREÇOS"""
        if not self.ia_api_key or not self.has_requests:
            return None
        
        try:
            # Preparar prompt para criar sidebar personalizada SEM PREÇOS
            prompt = self.criar_prompt_sidebar(produto, categoria, link_afiliado, idioma)
            
            # Chamar IA
            headers = {
                "Authorization": f"Bearer {self.ia_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "Gerador Real v6.0"
            }
            
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Você é um especialista em criação de conteúdo para sidebars de sites de reviews. Crie conteúdo HTML válido e otimizado, SEM MENCIONAR PREÇOS OU VALORES."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                sidebar = result["choices"][0]["message"]["content"]
                sidebar = self.limpar_resposta_ia(sidebar)
                print(f"   ✅ Sidebar personalizada criada com IA")
                return sidebar
            else:
                return None
                
        except Exception as e:
            print(f"   ⚠️  Erro ao criar sidebar com IA: {e}")
            return None
    
    def criar_prompt_sidebar(self, produto, categoria, link_afiliado, idioma='pt-BR'):
        """Cria prompt para gerar sidebar personalizada SEM PREÇOS"""
        if idioma.lower().startswith('en'):
            return f"""Create a personalized sidebar for a review article about {produto} in the {categoria} category.

The sidebar should include:
1. A special offer widget WITHOUT PRICES - just mention it's a limited time offer
2. A "Related Products" section with 3-4 products from the same category
3. An "Information" section with links (About Us, Contact, Privacy Policy)

IMPORTANT: DO NOT mention any prices, values, discounts percentages, or specific monetary amounts.

Make it HTML valid, with CSS classes that match: widget, btn-sidebar, etc.
Create realistic product names related to {categoria}.

Return ONLY the HTML code, no explanations."""
        else:
            return f"""Crie uma sidebar personalizada para um artigo de review sobre {produto} na categoria {categoria}.

A sidebar deve incluir:
1. Um widget de oferta especial SEM PREÇOS - apenas mencione que é uma oferta por tempo limitado
2. Uma seção "Produtos Relacionados" com 3-4 produtos da mesma categoria
3. Uma seção "Informações" com links (Sobre Nós, Contato, Política de Privacidade)

IMPORTANTE: NÃO mencione preços, valores, porcentagens de desconto ou quantias monetárias específicas.

Faça HTML válido, com classes CSS que combinem: widget, btn-sidebar, etc.
Crie nomes de produtos realistas relacionados a {categoria}.

Retorne APENAS o código HTML, sem explicações."""
    
    def criar_sidebar_conteudo(self, categoria, produto_slug, nome_original, link_afiliado, idioma='pt-BR', is_preland=False):
        """Cria conteúdo da sidebar automaticamente SEM PREÇOS"""
        
        # Produtos relacionados por categoria
        produtos_relacionados = self.obter_produtos_relacionados(categoria, nome_original)
        
        if idioma.lower().startswith('en'):
            html = f'''
        <div class="widget">
            <h3><i class="fas fa-star"></i> Featured Product</h3>
            <p><strong>{nome_original}</strong></p>
            <p>Special limited time offer available</p>
            <a href="{link_afiliado}" class="btn-sidebar" target="_blank" rel="nofollow sponsored">Learn More</a>
        </div>

        <div class="widget">
            <h3><i class="fas fa-link"></i> More {categoria.title()}</h3>
            <ul>
        '''
        
            for produto in produtos_relacionados:
                html += f'                <li><a href="#">{produto}</a></li>\n'
        
            html += f'''            </ul>
            <p><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', f'{categoria}/index.html')}">View all products →</a></p>
        </div>

        <div class="widget">
            <h3><i class="fas fa-info-circle"></i> Information</h3>
            <ul>
                <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'sobre-nos.html')}">About Us</a></li>
                <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'contato.html')}">Contact</a></li>
                <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'politica-de-privacidade.html')}">Privacy Policy</a></li>
            </ul>
        </div>
        '''
        else:
            html = f'''
        <div class="widget">
            <h3><i class="fas fa-star"></i> Destaque</h3>
            <p><strong>{nome_original}</strong></p>
            <p>Oferta especial por tempo limitado disponível</p>
            <a href="{link_afiliado}" class="btn-sidebar" target="_blank" rel="nofollow sponsored">Saiba Mais</a>
        </div>

        <div class="widget">
            <h3><i class="fas fa-link"></i> Mais {categoria.title()}</h3>
            <ul>
        '''
        
            for produto in produtos_relacionados:
                html += f'                <li><a href="#">{produto}</a></li>\n'
        
            html += f'''            </ul>
            <p><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', f'{categoria}/index.html')}">Ver todos os produtos →</a></p>
        </div>

        <div class="widget">
            <h3><i class="fas fa-info-circle"></i> Informações</h3>
            <ul>
                <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'sobre-nos.html')}">Sobre Nós</a></li>
                <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'contato.html')}">Contato</a></li>
                <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'politica-de-privacidade.html')}">Política de Privacidade</a></li>
            </ul>
        </div>
        '''
        
        return html
    
    def obter_produtos_relacionados(self, categoria, produto_atual):
        """Retorna lista de produtos relacionados por categoria"""
        # Produtos por categoria (pode ser expandido)
        catalogo = {
            'games': ['Xbox Series X', 'Nintendo Switch OLED', 'PlayStation 5 Pro', 'PC Gamer Ryzen 7', 'Headset Gamer 7.1'],
            'smartphones': ['Samsung Galaxy S24', 'iPhone 16 Pro', 'Xiaomi 14 Pro', 'Google Pixel 8', 'OnePlus 12'],
            'eletrodomesticos': ['Air Fryer Digital', 'Liquidificador Profissional', 'Forno Elétrico', 'Cafeteira Expresso', 'Aspirador Robô'],
            'computadores': ['Notebook Gamer RTX 4060', 'MacBook Pro M3', 'Ultrabook Dell XPS', 'All-in-One Intel i7', 'Workstation AMD Threadripper'],
            'healthcare': ['Escova Elétrica Oral-B', 'Aparelho Pressão Digital', 'Oxímetro de Dedo', 'Massageador Cervical', 'Cadeira de Massagem'],
            'testes': ['Produto Teste 1', 'Produto Teste 2', 'Produto Teste 3', 'Produto Teste 4']
        }
        
        # Se categoria não existe, usar genérico
        if categoria.lower() in catalogo:
            produtos = catalogo[categoria.lower()]
            # Remover o produto atual da lista se estiver presente
            produtos = [p for p in produtos if p.lower() != produto_atual.lower()]
            # Retornar até 4 produtos
            return produtos[:4]
        
        # Fallback
        return ['Produto Relacionado 1', 'Produto Relacionado 2', 'Produto Relacionado 3']
    
    def criar_secao_cta(self, produto, link_afiliado, idioma, is_preland=False):
        """Cria seção de call-to-action"""
        if is_preland:
            if idioma.lower().startswith('en'):
                return f'''
                <div class="cta-premium">
                    <h3>🚀 Special Launch Offer!</h3>
                    <p>Limited time opportunity</p>
                    
                    <div class="cta-button-container">
                        <a href="{link_afiliado}" class="cta-button-premium" target="_blank" rel="nofollow sponsored">
                            GET {produto.upper()} NOW
                        </a>
                    </div>
                    
                    <p><i class="fas fa-lock"></i> Secure Checkout</p>
                </div>
                '''
            else:
                return f'''
                <div class="cta-premium">
                    <h3>🚀 Oferta de Lançamento!</h3>
                    <p>Oportunidade por tempo limitado</p>
                    
                    <div class="cta-button-container">
                        <a href="{link_afiliado}" class="cta-button-premium" target="_blank" rel="nofollow sponsored">
                            ADQUIRA {produto.upper()} AGORA
                        </a>
                    </div>
                    
                    <p><i class="fas fa-lock"></i> Compra Segura</p>
                </div>
                '''
        else:
            if idioma.lower().startswith('en'):
                return f'''
                <div class="cta">
                    <h3>Ready to Experience {produto}?</h3>
                    <p>Get the best offer through our special link:</p>
                    <a href="{link_afiliado}" class="btn-cta" target="_blank" rel="nofollow sponsored">
                        <i class="fas fa-shopping-cart"></i> View Special Offer
                    </a>
                </div>
                '''
            else:
                return f'''
                <div class="cta">
                    <h3>Pronto para Experimentar {produto}?</h3>
                    <p>Garanta a melhor oferta através do nosso link especial:</p>
                    <a href="{link_afiliado}" class="btn-cta" target="_blank" rel="nofollow sponsored">
                        <i class="fas fa-shopping-cart"></i> Ver Oferta Especial
                    </a>
                </div>
                '''
    
    def criar_header_basico(self, idioma='pt-BR'):
        """Cria header básico"""
        if idioma.lower().startswith('en'):
            return '''<header class="site-header">
    <div class="container">
        <div class="logo">
            <a href="../index.html">🔥 Top Offers</a>
        </div>
        <nav class="main-nav">
            <a href="../index.html">Home</a>
            <a href="../eletrodomesticos/index.html">Appliances</a>
            <a href="../smartphones/index.html">Smartphones</a>
            <a href="../computadores/index.html">Computers</a>
            <a href="../games/index.html">Games</a>
            <a href="../healthcare/index.html">Healthcare</a>
        </nav>
    </div>
</header>'''
        else:
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
            <a href="../healthcare/index.html">Healthcare</a>
        </nav>
    </div>
</header>'''
    
    def criar_footer_basico(self, idioma='pt-BR'):
        """Cria footer básico"""
        ano_atual = datetime.now().year
        
        if idioma.lower().startswith('en'):
            return f'''<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h3>Top Offers</h3>
                <p>Honest reviews and detailed analysis.</p>
            </div>
            <div class="footer-section">
                <h4>Links</h4>
                <a href="../sobre-nos.html">About</a>
                <a href="../contato.html">Contact</a>
                <a href="../politica-de-privacidade.html">Privacy</a>
            </div>
        </div>
        <p class="copyright">&copy; {ano_atual} Top Offers. All rights reserved.</p>
    </div>
</footer>'''
        else:
            return f'''<footer class="site-footer">
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
        <p class="copyright">&copy; {ano_atual} Top Ofertas. Todos os direitos reservados.</p>
    </div>
</footer>'''
    
    def atualizar_index_categoria(self, categoria, idioma='pt-BR'):
        """Atualiza/cria index.html da categoria"""
        categoria_dir = self.docs_dir / categoria
        index_path = categoria_dir / "index.html"
        
        # Listar produtos na categoria
        produtos = []
        for item in categoria_dir.iterdir():
            if item.is_dir() and (item / "index.html").exists():
                if '-guia-completo' not in item.name:
                    produtos.append({
                        'slug': item.name,
                        'nome': item.name.replace('-', ' ').title()
                    })
        
        if not produtos:
            return
        
        # Determinar título baseado no idioma
        if idioma.lower().startswith('en'):
            titulo = f"{categoria.title()} - Reviews and Analysis"
            descricao = f"Check out our reviews and analysis of {categoria}:"
        else:
            titulo = f"{categoria.title()} - Reviews e Análises"
            descricao = f"Confira nossos reviews e análises de {categoria}:"
        
        html = f'''<!DOCTYPE html>
<html lang="{self.normalizar_idioma_html(idioma)}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://topofertas.reviewnexus.blog/assets/js/script.js" defer></script>
</head>
<body>
    {self.criar_header_basico(idioma)}
    
    <main class="container">
        <h1>{categoria.title()}</h1>
        <p>{descricao}</p>
        
        <div class="products-grid">
'''
        
        for produto in produtos:
            html += f'''
            <div class="product-card">
                <h3><a href="{produto['slug']}/index.html">{produto['nome']}</a></h3>
                <p>Complete review and detailed analysis.</p>
                <a href="{produto['slug']}/index.html" class="btn-read">Read Review →</a>
            </div>
'''
        
        html += f'''
        </div>
    </main>
    
    {self.criar_footer_basico(idioma)}
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
                        self.adicionar_url_sitemap(urlset, url, 0.6, 'monthly')
        
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
    
    def adicionar_url_sitemap(self, urlset, url_relativa, priority, changefreq):
        """Adiciona uma URL ao sitemap"""
        url_elem = ET.SubElement(urlset, 'url')
        
        loc = ET.SubElement(url_elem, 'loc')
        loc.text = f"{self.site_url}/{url_relativa}"
        
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = datetime.now().strftime('%Y-%m-%d')
        
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
            
            # Verificar se URL já existe
            urls_existentes = [loc.text for loc in urlset.findall('url/loc')]
            url_completa = f"{self.site_url}/{url_relativa}"
            
            if url_completa not in urls_existentes:
                # Adicionar nova URL
                self.adicionar_url_sitemap(urlset, url_relativa, 0.6, 'monthly')
                
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
                ["produto", "idioma", "categoria", "tipo_artigo", "site_oficial", "links_afiliados", "status", "data_publicacao", "url_publicada"],
                ["Playstation 5", "pt-BR", "games", "review", "https://playstation.com", "https://afiliado.com/ps5", "pending", "", ""],
                ["iPhone 15 Pro", "en-US", "smartphones", "review", "https://apple.com", "https://afiliado.com/iphone", "pending", "", ""],
                ["Prodentim", "en-US", "healthcare", "preland", "https://prodentim.com", "https://afiliado.com/prodentim", "pending", "", ""]
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
        print(f"📄 Artigos gerados: {len(artigos)}")
    
    # ==================== PROCESSAMENTO PRINCIPAL ====================
    
    def gerar_funnel_completo(self, produto_data):
        """Gera funnel completo: review + pre-landing page"""
        nome = produto_data.get('produto', '').strip()
        if not nome:
            return False
        
        categoria = produto_data.get('categoria', 'geral').strip().lower()
        idioma = produto_data.get('idioma', 'pt-BR').strip()
        site_oficial = produto_data.get('site_oficial', '').strip()
        link_afiliado = produto_data.get('links_afiliados', '').strip()
        
        print(f"\n   🔄 Gerando funnel para: {nome}")
        print(f"   📁 Categoria: {categoria} | 🌐 Idioma: {idioma}")
        
        # 1. Gerar REVIEW
        print(f"   📝 1. Gerando REVIEW...")
        slug_review = self.criar_slug(nome)
        titulo_review = self.criar_titulo_seo(nome, 'review', idioma)
        
        conteudo_review = self.gerar_conteudo_com_ia(
            nome, categoria, 'review', site_oficial, link_afiliado, idioma
        )
        
        caminho_review = self.criar_artigo_completo(
            titulo=titulo_review,
            conteudo_html=conteudo_review,
            categoria=categoria,
            produto_slug=slug_review,
            tipo_artigo='review',
            nome_original=nome,
            site_oficial=site_oficial,
            link_afiliado=link_afiliado,
            idioma=idioma,
            is_preland=False
        )
        
        if not caminho_review:
            return False
        
        print(f"   ✅ Review criado: {categoria}/{slug_review}/")
        
        # 2. Gerar PRE-LANDING (guia)
        print(f"   📝 2. Gerando PRE-LANDING...")
        titulo_preland = self.criar_titulo_seo(nome, 'preland', idioma)
        
        conteudo_preland = self.gerar_conteudo_com_ia(
            nome, categoria, 'preland', site_oficial, link_afiliado, idioma
        )
        
        if not conteudo_preland:
            conteudo_preland = self.gerar_preland_basica(nome, categoria, site_oficial, link_afiliado, idioma)
        
        caminho_preland = self.criar_artigo_completo(
            titulo=titulo_preland,
            conteudo_html=conteudo_preland,
            categoria=categoria,
            produto_slug=slug_review,
            tipo_artigo='preland',
            nome_original=nome,
            site_oficial=site_oficial,
            link_afiliado=link_afiliado,
            idioma=idioma,
            is_preland=True
        )
        
        if caminho_preland:
            print(f"   ✅ Pre-landing criada: {categoria}/{slug_review}-guia-completo/")
        
        return True
    
    def processar_tabela_completa(self):
        """Processa todos os produtos do CSV"""
        print("\n" + "="*70)
        print("🚀 PROCESSAR TABELA COMPLETA COM FUNNEL")
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
        
        print(f"\n🔧 MODO: {'🤖 COM IA' if tem_ia else '📝 SEM IA'}")
        print("="*40)
        
        for i, produto_data in enumerate(produtos, 1):
            print(f"\n[{i}/{len(produtos)}] {'='*30}")
            
            nome = produto_data.get('produto', '').strip()
            if not nome:
                continue
            
            categoria = produto_data.get('categoria', 'geral').strip().lower()
            tipo = produto_data.get('tipo_artigo', 'review').strip().lower()
            site_oficial = produto_data.get('site_oficial', '').strip()
            link_afiliado = produto_data.get('links_afiliados', '').strip()
            status = produto_data.get('status', 'pending').lower()
            idioma = produto_data.get('idioma', 'pt-BR').strip()
            
            # Pular se já concluído
            if status == 'completed':
                print(f"   ⏭️  Já concluído: {nome[:40]}")
                continue
            
            print(f"   📦 {nome}")
            print(f"   📁 {categoria} • {tipo} • 🌐 {idioma}")
            
            if tipo == 'preland' and self.config['funnel']['enable_preland']:
                # Gerar funnel completo
                sucesso = self.gerar_funnel_completo(produto_data)
                status_final = "completed" if sucesso else "error"
                self.atualizar_csv_apos_geracao(produto_data, None, status_final)
                
            else:
                # Gerar artigo único
                slug = self.criar_slug(nome)
                titulo = self.criar_titulo_seo(nome, tipo, idioma)
                
                # Gerar conteúdo
                if tem_ia:
                    conteudo = self.gerar_conteudo_com_ia(nome, categoria, tipo, site_oficial, link_afiliado, idioma)
                    if conteudo is None:
                        print("   ⚠️  IA falhou, usando conteúdo básico")
                        conteudo = self.gerar_conteudo_basico(nome, categoria, tipo, site_oficial, link_afiliado, idioma)
                else:
                    conteudo = self.gerar_conteudo_basico(nome, categoria, tipo, site_oficial, link_afiliado, idioma)
                
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
                        link_afiliado=link_afiliado,
                        idioma=idioma,
                        is_preland=(tipo == 'preland')
                    )
                    
                    # Atualizar CSV
                    if caminho:
                        self.atualizar_csv_apos_geracao(produto_data, caminho, "completed")
                        print(f"   ✅ Gerado com sucesso em {idioma.upper()}")
                    else:
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
        
        # Mostrar estatísticas
        self.mostrar_painel_controle()
    
    # ==================== MENU PRINCIPAL ====================
    
    def menu_principal(self):
        """Menu interativo"""
        while True:
            print("\n" + "="*60)
            print("📱 GERADOR REAL v6.0 - MENU PRINCIPAL")
            print("="*60)
            print("1. 🔍 Verificar estrutura")
            print("2. 📱 Gerar artigo de teste")
            print("3. ✍️  Gerar artigo manual")
            print("4. 🚀 PROCESSAR TABELA COMPLETA (FUNNEL)")
            print("5. 📊 Painel de controle")
            print("6. 🗺️  Criar/atualizar sitemap")
            print("7. 🤖 Configurar IA")
            print("8. ❌ Sair")
            
            try:
                opcao = input("\n🎯 Escolha (1-8): ").strip()
                
                if opcao == "1":
                    self.verificar_estrutura()
                elif opcao == "2":
                    self.gerar_artigo_teste()
                elif opcao == "3":
                    self.gerar_artigo_manual()
                elif opcao == "4":
                    self.processar_tabela_completa()
                elif opcao == "5":
                    self.mostrar_painel_controle()
                elif opcao == "6":
                    self.criar_sitemap()
                elif opcao == "7":
                    self.configurar_ia()
                elif opcao == "8":
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
            (self.includes_dir / "sidebar.html", "Sidebar"),
            (self.docs_dir / "assets/css/style.css", "CSS"),
            (self.base_dir / "produtos.csv", "CSV Produtos"),
            (self.base_dir / "config.json", "Configurações"),
        ]
        
        for caminho, nome in arquivos:
            if caminho.exists():
                tamanho = caminho.stat().st_size
                print(f"✅ {nome}: OK ({tamanho} bytes)")
            else:
                print(f"❌ {nome}: Não encontrado")
        
        # Verificar artigos gerados
        artigos = list(self.docs_dir.glob("**/index.html"))
        print(f"\n📄 Artigos gerados: {len(artigos)}")
    
    def gerar_artigo_teste(self):
        """Gera artigo de teste"""
        print("\n🧪 GERANDO ARTIGO DE TESTE...")
        
        artigo = {
            'produto': 'Produto de Teste',
            'categoria': 'testes',
            'tipo_artigo': 'review',
            'site_oficial': 'https://exemplo.com',
            'links_afiliados': 'https://afiliado.com',
            'idioma': 'pt-BR'
        }
        
        slug = self.criar_slug(artigo['produto'])
        titulo = self.criar_titulo_seo(artigo['produto'], artigo['tipo_artigo'], artigo['idioma'])
        
        conteudo = self.gerar_conteudo_basico(
            artigo['produto'],
            artigo['categoria'],
            artigo['tipo_artigo'],
            artigo['site_oficial'],
            artigo['links_afiliados'],
            artigo['idioma']
        )
        
        caminho = self.criar_artigo_completo(
            titulo=titulo,
            conteudo_html=conteudo,
            categoria=artigo['categoria'],
            produto_slug=slug,
            tipo_artigo=artigo['tipo_artigo'],
            nome_original=artigo['produto'],
            site_oficial=artigo['site_oficial'],
            link_afiliado=artigo['links_afiliados'],
            idioma=artigo['idioma']
        )
        
        if caminho:
            print(f"\n✅ Artigo de teste criado:")
            print(f"   📁 {caminho}")
            print(f"   🌐 Acesse: {self.site_url}/{artigo['categoria']}/{slug}/")
    
    def gerar_artigo_manual(self):
        """Gera artigo manual"""
        print("\n✍️  GERAR ARTIGO MANUAL")
        print("-"*40)
        
        try:
            produto = input("Nome do produto: ").strip() or "Produto Teste"
            categoria = input("Categoria (games/smartphones/computadores/eletrodomesticos/healthcare): ").strip() or "testes"
            tipo = input("Tipo (review/guia/preland): ").strip() or "review"
            idioma = input("Idioma (pt-BR/en-US): ").strip() or "pt-BR"
            site = input("Site oficial (opcional): ").strip() or "https://exemplo.com"
            link = input("Link afiliado (opcional): ").strip() or "https://afiliado.com"
            
            if tipo == 'preland':
                produto_data = {
                    'produto': produto,
                    'categoria': categoria,
                    'idioma': idioma,
                    'site_oficial': site,
                    'links_afiliados': link
                }
                
                print(f"\n📝 Confirmar criação de FUNNEL?")
                print(f"   Produto: {produto}")
                print(f"   Funnel: Review + Pre-landing page")
                
                if input("Continuar? (s/n): ").strip().lower() == 's':
                    self.gerar_funnel_completo(produto_data)
                    print("✅ Funnel criado com sucesso!")
                return
            
            slug = self.criar_slug(produto)
            titulo = self.criar_titulo_seo(produto, tipo, idioma)
            
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
                conteudo = self.gerar_conteudo_com_ia(produto, categoria, tipo, site, link, idioma)
            else:
                conteudo = self.gerar_conteudo_basico(produto, categoria, tipo, site, link, idioma)
            
            caminho = self.criar_artigo_completo(
                titulo=titulo,
                conteudo_html=conteudo,
                categoria=categoria,
                produto_slug=slug,
                tipo_artigo=tipo,
                nome_original=produto,
                site_oficial=site,
                link_afiliado=link,
                idioma=idioma,
                is_preland=(tipo == 'preland')
            )
            
            if caminho:
                print(f"\n✅ Artigo criado: {caminho}")
                print(f"🌐 Acesse: {self.site_url}/{categoria}/{slug}/")
            else:
                print("❌ Erro ao criar artigo")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    try:
        # Verificar estrutura
        base_dir = Path(__file__).parent
        docs_dir = base_dir / "docs"
        
        if not docs_dir.exists():
            print("📁 Primeira execução - criando estrutura...")
            docs_dir.mkdir(exist_ok=True)
        
        # Verificar chave API
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        if OPENROUTER_API_KEY:
            print(f"🔑 API Key detectada do .env")
        else:
            print("⚠️  AVISO: OPENROUTER_API_KEY não encontrada no .env")
            print("💡 Crie um arquivo .env na raiz com:")
            print("   OPENROUTER_API_KEY=sua_chave_aqui")
        
        # Iniciar sistema
        gerador = GeradorReal()
        
        # Criar homepage se não existir
        homepage = docs_dir / "index.html"
        if not homepage.exists():
            html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Ofertas - Reviews Honestos</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://topofertas.reviewnexus.blog/assets/js/script.js" defer></script>
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="logo">
                <a href="index.html">🔥 Top Ofertas</a>
            </div>
            <nav class="main-nav">
                <a href="index.html">Home</a>
                <a href="games/index.html">Games</a>
                <a href="smartphones/index.html">Smartphones</a>
                <a href="eletrodomesticos/index.html">Eletrodomésticos</a>
                <a href="computadores/index.html">Computadores</a>
                <a href="healthcare/index.html">Healthcare</a>
            </nav>
        </div>
    </header>
    
    <main class="container">
        <div style="text-align: center; padding: 60px 0;">
            <h1 style="font-size: 2.5rem; margin-bottom: 20px;">Bem-vindo ao Top Ofertas</h1>
            <p style="font-size: 1.2rem; color: #666; max-width: 800px; margin: 0 auto 30px;">
                Reviews honestos e análises detalhadas dos melhores produtos do mercado.
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 40px 0;">
            <a href="games/index.html" class="btn" style="background: #3498db; color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">
                🎮 Games
            </a>
            <a href="smartphones/index.html" class="btn" style="background: #9b59b6; color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">
                📱 Smartphones
            </a>
            <a href="eletrodomesticos/index.html" class="btn" style="background: #2ecc71; color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">
                🏠 Eletrodomésticos
            </a>
            <a href="computadores/index.html" class="btn" style="background: #e74c3c; color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">
                💻 Computadores
            </a>
            <a href="healthcare/index.html" class="btn" style="background: #1abc9c; color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">
                🏥 Healthcare
            </a>
        </div>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Top Ofertas</h3>
                    <p>Os melhores achadinhos online com reviews honestos.</p>
                </div>
                <div class="footer-section">
                    <h4>Links</h4>
                    <a href="sobre-nos.html">Sobre Nós</a>
                    <a href="contato.html">Contato</a>
                    <a href="politica-de-privacidade.html">Política de Privacidade</a>
                </div>
            </div>
            <p class="copyright">&copy; 2025 Top Ofertas. Todos os direitos reservados.</p>
        </div>
    </footer>
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
        import traceback
        traceback.print_exc()