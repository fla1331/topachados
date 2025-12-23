#!/usr/bin/env python3
"""
GERADOR REAL v6.0 - SISTEMA PROFISSIONAL AVANÇADO
SEO Avançado + Artigos Humanos + Funnel Completo + Multi-idioma
"""

import os
import sys
import json
import csv
import re
import random
import shutil
import unicodedata
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
        self.templates_dir = self.base_dir / "templates"
        self.ia_api_key = None
        self.ia_provider = None
        self.has_requests = HAS_REQUESTS
        self.site_url = site_url.rstrip('/')
        self.site_name = "Top Ofertas"
        
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
            self.docs_dir / "assets" / "img" / "healthcare",
            self.includes_dir,
            self.templates_dir,
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
                "description": "Reviews honestos e análises detalhadas dos melhores produtos",
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
                "word_count": 2500,
                "enable_faq": True,
                "enable_toc": True,
                "image_source": "unsplash",
                "use_ia_by_default": True,
                "default_ia_provider": "openrouter",
                "translation_quality": "human"
            },
            "funnel": {
                "enable_preland": True,
                "preland_suffix": "-guia-completo",
                "internal_linking": True,
                "cross_sell": True
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
            'analise.txt': self.criar_template_analise(),
            'preland.txt': self.criar_template_preland()
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
    
    def carregar_prompt_template(self, tipo_artigo, idioma='pt-BR'):
        """Carrega template de prompt do arquivo .txt"""
        # Primeiro tenta carregar template específico do idioma
        arquivo_prompt_idioma = self.templates_dir / f"{tipo_artigo}_{idioma}.txt"
        
        if arquivo_prompt_idioma.exists():
            try:
                with open(arquivo_prompt_idioma, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️  Erro ao ler prompt template específico do idioma: {e}")
        
        # Se não encontrar template específico do idioma, usa o genérico
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
    
    def criar_titulo_seo(self, produto, tipo_artigo, idioma='pt-BR'):
        """Cria título otimizado para SEO"""
        
        ano_atual = datetime.now().year
        
        # Títulos em diferentes idiomas
        titulos = {
            'pt-BR': {
                'review': [
                    f"{produto} - Análise Completa e Review {ano_atual}",
                    f"Vale a pena comprar {produto}? Review Honesto e Detalhado",
                    f"{produto}: Review Completo, Prós e Contras | Teste Real {ano_atual}"
                ],
                'comparativo': [
                    f"Comparativo: {produto} vs Concorrentes {ano_atual}",
                    f"{produto}: Melhor Custo-Benefício? Análise Comparativa Detalhada",
                    f"Análise Comparativa {produto} - Qual Vale Mais a Pena?"
                ],
                'guia': [
                    f"Guia Completo: Como escolher {produto} {ano_atual}",
                    f"Guia Definitivo {produto} - Tudo o que Você Precisa Saber",
                    f"Guia de Compra: {produto} - Dicas Especialistas para Acertar"
                ],
                'preland': [
                    f"{produto} Funciona Mesmo? Verdade Revelada {ano_atual}",
                    f"{produto}: Solução Definitiva para [PROBLEMA]?",
                    f"Descubra Tudo Sobre {produto} - Guia Exclusivo"
                ]
            },
            'en': {
                'review': [
                    f"{produto} - Complete Review and Honest Analysis {ano_atual}",
                    f"Is {produto} Worth Buying? Real User Review and Test",
                    f"{produto} Review: Pros, Cons, and Everything You Need to Know"
                ],
                'comparativo': [
                    f"Comparison: {produto} vs Competitors {ano_atual}",
                    f"{produto}: Best Value for Money? Detailed Comparison",
                    f"{produto} vs Alternatives - Which One Should You Choose?"
                ],
                'guia': [
                    f"Complete Guide: How to Choose {produto} {ano_atual}",
                    f"Ultimate Guide to {produto} - Everything You Need to Know",
                    f"Buying Guide: {produto} - Expert Tips and Recommendations"
                ],
                'preland': [
                    f"Does {produto} Really Work? The Truth Revealed",
                    f"{produto}: The Ultimate Solution for [PROBLEM]?",
                    f"Everything About {produto} - Must Read Before Buying"
                ]
            },
            'es': {
                'review': [
                    f"{produto} - Reseña Completa y Análisis Honesto {ano_atual}",
                    f"¿Vale la pena comprar {produto}? Reseña Detallada y Real",
                    f"Reseña {produto}: Ventajas, Desventajas y Todo lo que Debes Saber"
                ],
                'comparativo': [
                    f"Comparación: {produto} vs Competidores {ano_atual}",
                    f"{produto}: ¿Mejor Relación Calidad-Precio? Análisis Comparativo",
                    f"{produto} vs Alternativas - ¿Cuál Deberías Elegir?"
                ],
                'guia': [
                    f"Guía Completa: Cómo elegir {produto} {ano_atual}",
                    f"Guía Definitiva de {produto} - Todo lo que Necesitas Saber",
                    f"Guía de Compra: {produto} - Consejos de Expertos"
                ],
                'preland': [
                    f"¿Funciona Realmente {produto}? La Verdad Revelada",
                    f"{produto}: ¿La Solución Definitiva para [PROBLEMA]?",
                    f"Todo Sobre {produto} - Debes Leer Antes de Comprar"
                ]
            }
        }
        
        # Normalizar idioma
        idioma_base = self.normalizar_idioma_base(idioma)
        
        # Buscar títulos no idioma ou usar português como fallback
        if idioma_base in titulos and tipo_artigo.lower() in titulos[idioma_base]:
            opcoes = titulos[idioma_base][tipo_artigo.lower()]
        else:
            opcoes = titulos['pt-BR'][tipo_artigo.lower()] if tipo_artigo.lower() in titulos['pt-BR'] else titulos['pt-BR']['review']
        
        return random.choice(opcoes)
    
    def normalizar_idioma_base(self, idioma):
        """Normaliza código de idioma para base (pt-BR -> pt-BR, en-US -> en, etc.)"""
        idioma = idioma.lower()
        
        if idioma.startswith('pt'):
            return 'pt-BR'
        elif idioma.startswith('en'):
            return 'en'
        elif idioma.startswith('es'):
            return 'es'
        elif idioma.startswith('fr'):
            return 'fr'
        elif idioma.startswith('de'):
            return 'de'
        elif idioma.startswith('it'):
            return 'it'
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
        elif idioma.startswith('fr'):
            return 'fr'
        elif idioma.startswith('de'):
            return 'de'
        elif idioma.startswith('it'):
            return 'it'
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
            'pt': 'pt_BR',
            'en': 'en_US',
            'en-us': 'en_US',
            'en-uk': 'en_GB',
            'es': 'es_ES',
            'es-es': 'es_ES',
            'fr': 'fr_FR',
            'fr-fr': 'fr_FR',
            'de': 'de_DE',
            'de-de': 'de_DE',
            'it': 'it_IT',
            'it-it': 'it_IT'
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
    <meta name="twitter:creator" content="{self.config['site']['twitter']}">
    
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
            'pt': 'Portuguese',
            'en': 'English',
            'en-us': 'English',
            'en-uk': 'English',
            'es': 'Spanish',
            'es-es': 'Spanish',
            'fr': 'French',
            'fr-fr': 'French',
            'de': 'German',
            'de-de': 'German',
            'it': 'Italian',
            'it-it': 'Italian'
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
            "inLanguage": in_language,
            "potentialAction": {
                "@type": "ReadAction",
                "target": [url]
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
                'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=630&fit=crop'
            ],
            'smartphones': [
                'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1200&h=630&fit=crop'
            ],
            'computadores': [
                'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1200&h=630&fit=crop'
            ],
            'healthcare': [
                'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&h=630&fit=crop'
            ],
            'testes': [
                'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1200&h=630&fit=crop',
                'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1200&h=630&fit=crop'
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
        print("1. Open Router (recomendada - DeepSeek via Open Router)")
        print("2. DeepSeek (API direta)")
        print("3. Gemini (Google AI Studio)")
        print("4. Não usar IA agora")
        
        opcao = input("\nEscolha (1-4): ").strip()
        
        config_path = self.base_dir / "config_ia.json"
        
        if opcao == "1":
            print("\n🔑 Configurando Open Router...")
            print("💡 Usando chave embutida na função.")
            
            # Chave Open Router funcional
            self.ia_api_key = "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"
            self.ia_provider = 'openrouter'
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({'api_key': self.ia_api_key, 'provider': 'openrouter'}, f, indent=2)
            
            print("✅ Open Router configurado!")
            print("💡 Modelo padrão: deepseek/deepseek-chat")
            return True
        
        elif opcao == "2":
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
        
        elif opcao == "3":
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
    
    def gerar_conteudo_com_ia(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Gera conteúdo usando IA com tradução completa"""
        
        if not self.ia_api_key or not self.has_requests:
            print("   ⚠️  IA não disponível, usando conteúdo básico")
            return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
        
        print(f"   🤖 Gerando conteúdo com IA ({self.ia_provider}) em {idioma.upper()}...")
        
        # Criar prompt considerando o idioma
        prompt = self.criar_prompt_ia_completo(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma, palavras_chave)
        
        try:
            if self.ia_provider == 'deepseek':
                conteudo = self.chamar_deepseek_api(prompt, idioma)
            elif self.ia_provider == 'gemini':
                conteudo = self.chamar_gemini_api(prompt, idioma)
            elif self.ia_provider == 'openrouter':
                conteudo = self.chamar_openrouter_api(prompt, idioma)
            else:
                print(f"   ❌ Provedor {self.ia_provider} não suportado")
                return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
            
            # Garantir que o conteúdo esteja no idioma correto
            if conteudo:
                conteudo = self.verificar_traducao_completa(conteudo, idioma)
                return conteudo
            else:
                return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
                
        except Exception as e:
            print(f"   ⚠️  Erro na IA: {e}")
            return self.gerar_conteudo_basico(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma)
    
    def chamar_deepseek_api(self, prompt, idioma='pt-BR'):
        """Chama API da DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.ia_api_key}",
            "Content-Type": "application/json"
        }
        
        # Mensagem do sistema baseada no idioma
        system_messages = {
            'pt-BR': "Você é um especialista brasileiro em SEO e criação de conteúdo para reviews de produtos. Crie conteúdo 100% em português do Brasil.",
            'en': "You are an English SEO and product review content creation expert. Create content 100% in English.",
            'es': "Eres un experto español en SEO y creación de contenido para reseñas de productos. Crea contenido 100% en español.",
            'fr': "Vous êtes un expert français en SEO et création de contenu pour les critiques de produits. Créez du contenu 100% en français.",
            'de': "Sie sind ein deutscher Experte für SEO und die Erstellung von Produktbewertungsinhalten. Erstellen Sie Inhalte zu 100% auf Deutsch.",
            'it': "Sei un esperto italiano di SEO e creazione di contenuti per recensioni di prodotti. Crea contenuti 100% in italiano."
        }
        
        idioma_base = self.normalizar_idioma_base(idioma)
        system_message = system_messages.get(idioma_base, system_messages['pt-BR'])
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 5000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                conteudo = result["choices"][0]["message"]["content"]
                conteudo = self.limpar_resposta_ia(conteudo)
                print(f"   ✅ DeepSeek gerou {len(conteudo)} caracteres em {idioma.upper()}")
                return conteudo
            else:
                print(f"   ❌ Erro DeepSeek ({response.status_code}): {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
            return None
    
    def chamar_gemini_api(self, prompt, idioma='pt-BR'):
        """Chama API do Gemini"""
        
        # Endpoints do Gemini
        endpoints = [
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        ]
        
        headers = {"Content-Type": "application/json"}
        
        # Instrução baseada no idioma
        system_instructions = {
            'pt-BR': "Você é um especialista brasileiro em SEO e criação de conteúdo para reviews de produtos. Crie conteúdo 100% em português do Brasil.",
            'en': "You are an English SEO and product review content creation expert. Create content 100% in English.",
            'es': "Eres un experto español en SEO y creación de contenido para reseñas de productos. Crea contenido 100% en español.",
            'fr': "Vous êtes un expert français en SEO et création de contenu pour les critiques de produits. Créez du contenu 100% en français.",
            'de': "Sie sind ein deutscher Experte für SEO und die Erstellung von Produktbewertungsinhalten. Erstellen Sie Inhalte zu 100% auf Deutsch.",
            'it': "Sei un esperto italiano di SEO e creazione di contenuti per recensioni di prodotti. Crea contenuti 100% in italiano."
        }
        
        idioma_base = self.normalizar_idioma_base(idioma)
        system_instruction = system_instructions.get(idioma_base, system_instructions['pt-BR'])
        
        # Adicionar instrução do sistema ao prompt
        full_prompt = f"{system_instruction}\n\n{prompt}"
        
        data = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 5000,
            }
        }
        
        for endpoint in endpoints:
            try:
                response = requests.post(
                    f"{endpoint}?key={self.ia_api_key}",
                    headers=headers,
                    json=data,
                    timeout=180
                )
                
                if response.status_code == 200:
                    result = response.json()
                    conteudo = result['candidates'][0]['content']['parts'][0]['text']
                    conteudo = self.limpar_resposta_ia(conteudo)
                    print(f"   ✅ Gemini gerou {len(conteudo)} caracteres em {idioma.upper()}")
                    return conteudo
                    
            except Exception:
                continue
        
        print("   ❌ Todos os endpoints Gemini falharam")
        return None
    
    def chamar_openrouter_api(self, prompt, idioma='pt-BR'):
        """Chama API do Open Router"""
        OPENROUTER_API_KEY = "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"
        OPENROUTER_MODEL = "deepseek/deepseek-chat"
        
        # Mensagem do sistema baseada no idioma
        system_messages = {
            'pt-BR': "Você é um especialista brasileiro em SEO e criação de conteúdo para reviews de produtos. Crie conteúdo 100% em português do Brasil, natural e humano.",
            'en': "You are an English SEO and product review content creation expert. Create content 100% in English, natural and human-like.",
            'es': "Eres un experto español en SEO y creación de contenido para reseñas de productos. Crea contenido 100% en español, natural y humano.",
            'fr': "Vous êtes un expert français en SEO et création de contenu pour les critiques de produits. Créez du contenu 100% en français, naturel et humain.",
            'de': "Sie sind ein deutscher Experte für SEO und die Erstellung von Produktbewertungsinhalten. Erstellen Sie Inhalte zu 100% auf Deutsch, natürlich und menschlich.",
            'it': "Sei un esperto italiano di SEO e creazione di contenuti per recensioni di prodotti. Crea contenuti 100% in italiano, naturale e umano."
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
            "max_tokens": 5000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                conteudo = result["choices"][0]["message"]["content"]
                conteudo = self.limpar_resposta_ia(conteudo)
                print(f"   ✅ Open Router ({OPENROUTER_MODEL}) gerou {len(conteudo)} caracteres em {idioma.upper()}")
                return conteudo
            else:
                print(f"   ❌ Erro Open Router ({response.status_code}): {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro na requisição ao Open Router: {e}")
            return None
    
    def criar_prompt_ia_completo(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Cria prompt completo baseado no tipo de artigo e idioma"""
        
        # Tentar carregar do template .txt
        template = self.carregar_prompt_template(tipo_artigo, idioma)
        
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
            prompt = prompt.replace("{IDIOMA}", idioma.upper())
            
            # Adicionar palavras-chave se fornecidas
            if palavras_chave:
                prompt = prompt.replace("{PALAVRAS_CHAVE}", palavras_chave)
            
            return prompt
        
        # Se não tiver template, usar padrão baseado no idioma
        return self.criar_prompt_padrao_avancado(produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma, palavras_chave)
    
    def criar_prompt_padrao_avancado(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Cria prompt padrão avançado para IA"""
        
        # Configurar baseado no tipo de artigo
        if tipo_artigo.lower() == 'review':
            return self.criar_prompt_review_avancado(produto, categoria, site_oficial, link_afiliado, idioma, palavras_chave)
        elif tipo_artigo.lower() == 'guia':
            return self.criar_prompt_guia_avancado(produto, categoria, site_oficial, link_afiliado, idioma, palavras_chave)
        elif tipo_artigo.lower() == 'preland':
            return self.criar_prompt_preland_avancado(produto, categoria, site_oficial, link_afiliado, idioma, palavras_chave)
        elif tipo_artigo.lower() == 'comparativo':
            return self.criar_prompt_comparativo_avancado(produto, categoria, site_oficial, link_afiliado, idioma, palavras_chave)
        else:
            return self.criar_prompt_review_avancado(produto, categoria, site_oficial, link_afiliado, idioma, palavras_chave)
    
    def criar_prompt_review_avancado(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Cria prompt avançado para review"""
        
        # Instruções baseadas no idioma
        instrucoes = {
            'pt-BR': {
                'titulo': f"# CRIAÇÃO DE REVIEW PROFISSIONAL - {produto}",
                'objetivo': f"Crie um review detalhado e honesto sobre {produto}.",
                'publico': "Brasileiros que pesquisam antes de comprar online",
                'tom': "Profissional, imparcial, confiável, mas acessível",
                'detalhes': f"""
## ESTRUTURA OBRIGATÓRIA (2000-2500 palavras):

1. INTRODUÇÃO ATRAENTE (contextualizar o produto e sua importância)
2. ESPECIFICAÇÕES TÉCNICAS COMPLETAS (tabela HTML com todas as specs)
3. ANÁLISE DE DESIGN E QUALIDADE (materiais, acabamento, durabilidade)
4. PERFORMANCE NO USO REAL (testes práticos, pontos fortes e fracos)
5. PRÓS E CONTRAS DETALHADOS (lista com explicações)
6. COMPARAÇÃO COM 2-3 CONCORRENTES DIRETOS (tabela comparativa)
7. ANÁLISE DE CUSTO-BENEFÍCIO (vale o preço?)
8. PARA QUEM RECOMENDAMOS (perfis de usuário ideais)
9. FAQ COM 6-8 PERGUNTAS RELEVANTES (com respostas detalhadas)
10. ONDE COMPRAR COM MELHOR PREÇO (links incluídos)

## LINKS OBRIGATÓRIOS:
- Site oficial: {site_oficial} (rel="nofollow")
- Link afiliado: {link_afiliado} (rel="nofollow sponsored")
- 3-4 links internos para artigos relacionados
- 2-3 links externos para fontes confiáveis

## REQUISITOS TÉCNICOS:
- HTML válido pronto para publicação
- Use: h2, h3, p, ul, li, table, tr, td, th, strong, a, div com classes simples
- Não use: div complexos, spans, classes CSS avançadas, emojis no HTML
- Otimizado para SEO: títulos hierárquicos, parágrafos curtos, palavras-chave naturais

## RETORNE APENAS:
O HTML completo do artigo, sem comentários extras, 100% em português brasileiro.
""",
                'final': "Comece agora o review profissional:"
            },
            'en': {
                'titulo': f"# PROFESSIONAL REVIEW CREATION - {produto}",
                'objetivo': f"Create a detailed and honest review about {produto}.",
                'publico': "US consumers researching before buying online",
                'tom': "Professional, unbiased, trustworthy, yet accessible",
                'detalhes': f"""
## MANDATORY STRUCTURE (2000-2500 words):

1. ENGAGING INTRODUCTION (contextualize the product and its importance)
2. COMPLETE TECHNICAL SPECIFICATIONS (HTML table with all specs)
3. DESIGN AND QUALITY ANALYSIS (materials, finish, durability)
4. REAL-WORLD PERFORMANCE (practical tests, strengths and weaknesses)
5. DETAILED PROS AND CONS (list with explanations)
6. COMPARISON WITH 2-3 DIRECT COMPETITORS (comparative table)
7. COST-BENEFIT ANALYSIS (is it worth the price?)
8. WHO WE RECOMMEND IT FOR (ideal user profiles)
9. FAQ WITH 6-8 RELEVANT QUESTIONS (with detailed answers)
10. WHERE TO BUY AT THE BEST PRICE (included links)

## MANDATORY LINKS:
- Official site: {site_oficial} (rel="nofollow")
- Affiliate link: {link_afiliado} (rel="nofollow sponsored")
- 3-4 internal links to related articles
- 2-3 external links to reliable sources

## TECHNICAL REQUIREMENTS:
- Valid HTML ready for publication
- Use: h2, h3, p, ul, li, table, tr, td, th, strong, a, div with simple classes
- Do not use: complex divs, spans, advanced CSS classes, emojis in HTML
- SEO optimized: hierarchical titles, short paragraphs, natural keywords

## RETURN ONLY:
The complete article HTML, no extra comments, 100% in English.
""",
                'final': "Start the professional review now:"
            }
        }
        
        idioma_base = self.normalizar_idioma_base(idioma)
        if idioma_base not in instrucoes:
            idioma_base = 'pt-BR'
        
        inst = instrucoes[idioma_base]
        
        # Adicionar palavras-chave se fornecidas
        keywords_section = ""
        if palavras_chave:
            keywords_section = f"\n## PALAVRAS-CHAVE PRINCIPAIS:\n{palavras_chave}\n"
        
        prompt = f"""{inst['titulo']}

## PRODUTO: {produto}
## CATEGORIA: {categoria}
## IDIOMA: {idioma.upper()}
## DATA: {datetime.now().strftime('%Y-%m-%d')}

{inst['objetivo']}

## PÚBLICO-ALVO:
{inst['publico']}

## TOM E ESTILO:
{inst['tom']}

{keywords_section}
{inst['detalhes']}

{inst['final']}"""
        
        return prompt
    
    def criar_prompt_guia_avancado(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Cria prompt avançado para guia"""
        
        instrucoes = {
            'pt-BR': {
                'titulo': f"# CRIAÇÃO DE GUIA COMPLETO - Como escolher {produto}",
                'objetivo': f"Crie um guia educativo e completo sobre como escolher o melhor {produto}.",
                'publico': "Brasileiros que querem aprender antes de comprar",
                'tom': "Educativo, detalhado, imparcial, prático",
                'detalhes': f"""
## ESTRUTURA DO GUIA (2500-3000 palavras):

1. INTRODUÇÃO EDUCATIVA (importância da escolha correta)
2. FATORES CRÍTICOS DE ESCOLHA (lista detalhada com explicações)
3. TERMINOLOGIA TÉCNICA EXPLICADA (tabela com termos comuns)
4. MARCAS E MODELOS RECOMENDADOS (análise de 3-4 opções)
5. COMPARAÇÃO DE FAIXAS DE PREÇO (econômico, médio, premium)
6. DICAS DE MANUTENÇÃO E CUIDADOS
7. PERGUNTAS PARA FAZER ANTES DE COMPRAR (checklist)
8. ARMADILHAS COMUNS A EVITAR
9. ONDE COMPRAR COM SEGURANÇA
10. RECOMENDAÇÃO FINAL POR PERFIL

## FOCO NO MERCADO BRASILEIRO:
- Preços em Reais (R$)
- Disponibilidade no Brasil
- Garantia e suporte técnico local
- Compatibilidade com rede elétrica brasileira

## LINKS OBRIGATÓRIOS:
- Site oficial: {site_oficial} (rel="nofollow")
- Link afiliado: {link_afiliado} (rel="nofollow sponsored")
- Links para reviews específicos mencionados
- Links para fontes técnicas confiáveis

## RETORNE APENAS:
HTML completo do guia, 100% em português brasileiro.
""",
                'final': "Comece o guia educativo agora:"
            },
            'en': {
                'titulo': f"# COMPLETE GUIDE CREATION - How to choose {produto}",
                'objetivo': f"Create an educational and complete guide on how to choose the best {produto}.",
                'publico': "US consumers who want to learn before buying",
                'tom': "Educational, detailed, unbiased, practical",
                'detalhes': f"""
## GUIDE STRUCTURE (2500-3000 words):

1. EDUCATIONAL INTRODUCTION (importance of correct choice)
2. CRITICAL CHOICE FACTORS (detailed list with explanations)
3. TECHNICAL TERMINOLOGY EXPLAINED (table with common terms)
4. RECOMMENDED BRANDS AND MODELS (analysis of 3-4 options)
5. PRICE RANGE COMPARISON (budget, mid-range, premium)
6. MAINTENANCE AND CARE TIPS
7. QUESTIONS TO ASK BEFORE BUYING (checklist)
8. COMMON PITFALLS TO AVOID
9. WHERE TO BUY SAFELY
10. FINAL RECOMMENDATION BY PROFILE

## FOCUS ON US MARKET:
- Prices in US Dollars ($)
- Availability in the US
- Local warranty and technical support
- Compatibility with US standards

## MANDATORY LINKS:
- Official site: {site_oficial} (rel="nofollow")
- Affiliate link: {link_afiliado} (rel="nofollow sponsored")
- Links to specific reviews mentioned
- Links to reliable technical sources

## RETURN ONLY:
Complete guide HTML, 100% in English.
""",
                'final': "Start the educational guide now:"
            }
        }
        
        idioma_base = self.normalizar_idioma_base(idioma)
        if idioma_base not in instrucoes:
            idioma_base = 'pt-BR'
        
        inst = instrucoes[idioma_base]
        
        prompt = f"""{inst['titulo']}

## PRODUTO: {produto}
## CATEGORIA: {categoria}
## IDIOMA: {idioma.upper()}
## DATA: {datetime.now().strftime('%Y-%m-%d')}

{inst['objetivo']}

## PÚBLICO-ALVO:
{inst['publico']}

## TOM E ESTILO:
{inst['tom']}

{inst['detalhes']}

{inst['final']}"""
        
        return prompt
    
    def criar_prompt_preland_avancado(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR', palavras_chave=None):
        """Cria prompt avançado para pre-landing page"""
        
        # Identificar problema principal baseado na categoria
        problemas = {
            'healthcare': ['saúde bucal', 'saúde digestiva', 'bem-estar geral', 'energia e vitalidade'],
            'games': ['entretenimento limitado', 'gráficos ruins', 'falta de jogos exclusivos', 'experiência imersiva'],
            'smartphones': ['bateria fraca', 'câmera ruim', 'lentidão', 'armazenamento insuficiente'],
            'computadores': ['lentidão', 'aquecimento', 'falta de portas', 'tela de baixa qualidade'],
            'eletrodomesticos': ['alto consumo', 'barulho excessivo', 'durabilidade ruim', 'funcionalidades limitadas']
        }
        
        problema = problemas.get(categoria.lower(), ['desempenho insatisfatório', 'qualidade duvidosa', 'custo-benefício ruim'])[0]
        
        instrucoes = {
            'pt-BR': {
                'titulo': f"# PRE-LANDING PAGE - {produto} funciona mesmo?",
                'objetivo': f"Crie uma página de pré-venda convincente sobre {produto}, focada em resolver o problema de {problema}.",
                'publico': "Brasileiros com problema de {problema} buscando solução",
                'tom': "Persuasivo, urgente, solucionador de problemas, confiável",
                'detalhes': f"""
## ESTRUTURA DA PRE-LANDING (1500-2000 palavras):

1. TÍTULO IMPACTANTE (focado na dor: "{problema}")
2. PROBLEMA AMPLIADO (consequências do não resolver)
3. SOLUÇÃO APRESENTADA ({produto} como resposta)
4. COMO FUNCIONA (explicação simples e visual)
5. BENEFÍCIOS PRINCIPAIS (lista emocional e racional)
6. DEPOIMENTOS FICTÍCIOS (3-4 testemunhos convincentes)
7. COMPARAÇÃO COM SOLUÇÕES ALTERNATIVAS (por que {produto} é melhor)
8. GARANTIA E SEGURANÇA (tirar objeções)
9. CHAMADA PARA AÇÃO URGENTE (oferta limitada)
10. FAQ ANTIOBJEÇÕES (perguntas de quem hesita)

## TÉCNICAS DE COPYWRITING:
- Foco na dor do cliente
- Uso de gatilhos mentais (urgência, escassez, prova social)
- Linguagem emocional + dados racionais
- Chamadas para ação claras e repetidas

## LINKS:
- Link principal: {link_afiliado} (rel="nofollow sponsored", múltiplos CTAs)
- Link para review detalhado
- Links de segurança (garantia, política de privacidade)

## RETORNE APENAS:
HTML completo da pre-landing, 100% em português brasileiro.
""",
                'final': "Comece a pre-landing page persuasiva agora:"
            },
            'en': {
                'titulo': f"# PRE-LANDING PAGE - Does {produto} really work?",
                'objetivo': f"Create a convincing pre-sale page about {produto}, focused on solving the {problema} problem.",
                'publico': "US consumers with {problema} problem seeking solution",
                'tom': "Persuasive, urgent, problem-solving, trustworthy",
                'detalhes': f"""
## PRE-LANDING STRUCTURE (1500-2000 words):

1. IMPACTFUL TITLE (pain-focused: "{problema}")
2. AMPLIFIED PROBLEM (consequences of not solving)
3. SOLUTION PRESENTED ({produto} as the answer)
4. HOW IT WORKS (simple and visual explanation)
5. MAIN BENEFITS (emotional and rational list)
6. FICTITIOUS TESTIMONIALS (3-4 convincing testimonials)
7. COMPARISON WITH ALTERNATIVE SOLUTIONS (why {produto} is better)
8. GUARANTEE AND SAFETY (remove objections)
9. URGENT CALL TO ACTION (limited offer)
10. ANTI-OBJECTION FAQ (questions from hesitant buyers)

## COPYWRITING TECHNIQUES:
- Focus on customer pain
- Use of mental triggers (urgency, scarcity, social proof)
- Emotional language + rational data
- Clear and repeated calls to action

## LINKS:
- Main link: {link_afiliado} (rel="nofollow sponsored", multiple CTAs)
- Link to detailed review
- Safety links (guarantee, privacy policy)

## RETURN ONLY:
Complete pre-landing HTML, 100% in English.
""",
                'final': "Start the persuasive pre-landing page now:"
            }
        }
        
        idioma_base = self.normalizar_idioma_base(idioma)
        if idioma_base not in instrucoes:
            idioma_base = 'pt-BR'
        
        inst = instrucoes[idioma_base]
        inst['publico'] = inst['publico'].format(problema=problema)
        
        prompt = f"""{inst['titulo']}

## PRODUTO: {produto}
## CATEGORIA: {categoria}
## PROBLEMA FOCAL: {problema}
## IDIOMA: {idioma.upper()}
## DATA: {datetime.now().strftime('%Y-%m-%d')}

{inst['objetivo']}

## PÚBLICO-ALVO:
{inst['publico']}

## TOM E ESTILO:
{inst['tom']}

{inst['detalhes']}

{inst['final']}"""
        
        return prompt
    
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

## OBJETIVO:
Criar um review detalhado, honesto e útil que ajude o leitor a decidir se deve comprar {PRODUTO}.

## PÚBLICO-ALVO:
Consumidores que pesquisam antes de comprar, buscando informações confiáveis e imparciais.

## ESTRUTURA DO REVIEW:
1. INTRODUÇÃO ATRAENTE
   - Contextualize o produto
   - Explique sua importância no mercado
   - Capture a atenção do leitor

2. ESPECIFICAÇÕES TÉCNICAS COMPLETAS
   - Tabela HTML com todas as especificações
   - Explicação dos termos técnicos importantes

3. ANÁLISE DE DESIGN E CONSTRUÇÃO
   - Qualidade dos materiais
   - Acabamento e durabilidade
   - Ergonomia e usabilidade

4. TESTES E PERFORMANCE PRÁTICA
   - Como funciona no dia a dia
   - Pontos fortes e fracos identificados
   - Resultados de testes específicos

5. PRÓS E CONTRAS HONESTOS
   - Lista detalhada de vantagens
   - Lista honesta de desvantagens
   - Explicação de cada ponto

6. COMPARAÇÃO COM CONCORRENTES
   - Tabela comparativa com 2-3 concorrentes diretos
   - Análise de diferenças principais
   - Vantagens competitivas

7. ANÁLISE DE CUSTO-BENEFÍCIO
   - Vale o preço?
   - Comparação com alternativas
   - Retorno sobre investimento

8. PARA QUEM É RECOMENDADO
   - Perfis de usuário ideais
   - Casos de uso específicos
   - Quem deve evitar

9. FAQ COMPLETO
   - 6-8 perguntas frequentes
   - Respostas detalhadas e úteis
   - Incluir <details> e <summary>

10. ONDE COMPRAR
    - Link oficial
    - Link afiliado com oferta especial
    - Dicas para melhor negociação

## TOM E ESTILO:
- Profissional mas acessível
- Imparcial (mostre prós e contras)
- Informativo e prático
- Confiável e honesto

## REQUISITOS TÉCNICOS:
- HTML válido pronto para publicação
- Use tags semânticas (h2, h3, p, ul, li, table, etc.)
- Links com atributos rel="nofollow" ou "nofollow sponsored"
- Otimizado para SEO (títulos hierárquicos, parágrafos curtos)
- Conteúdo 100% em {IDIOMA}

## LINKS OBRIGATÓRIOS:
1. Site oficial: {SITE_OFICIAL} (rel="nofollow")
2. Link afiliado: {LINK_AFILIADO} (rel="nofollow sponsored")
3. 3-4 links internos para artigos relacionados
4. 2-3 links externos para fontes confiáveis

## PALAVRAS-CHAVE PRINCIPAIS:
{PRODUTO}, review {PRODUTO}, {CATEGORIA}, comprar {PRODUTO}, vale a pena {PRODUTO}, análise {PRODUTO}

Retorne APENAS o HTML completo do artigo, sem comentários extras."""

    def criar_template_guia(self):
        """Cria template para guia.txt"""
        return """# TEMPLATE PARA GUIA - Como escolher {PRODUTO}

## INFORMAÇÕES BÁSICAS:
- PRODUTO: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}

## OBJETIVO:
Educar o leitor sobre {CATEGORIA} e ajudá-lo a tomar a melhor decisão de compra.

## PÚBLICO-ALVO:
Consumidores que querem aprender antes de comprar, desde iniciantes até intermediários.

## ESTRUTURA DO GUIA:
1. INTRODUÇÃO EDUCATIVA
   - O que é {PRODUTO} e sua importância
   - Por que a escolha certa é crucial
   - Objetivo do guia

2. FATORES CRÍTICOS DE ESCOLHA
   - Lista detalhada dos fatores mais importantes
   - Explicação de cada fator
   - Como priorizar os fatores

3. TERMINOLOGIA TÉCNICA EXPLICADA
   - Tabela com termos comuns
   - Explicação em linguagem simples
   - Por que cada termo é importante

4. MARCAS E MODELOS RECOMENDADOS
   - Análise de 3-4 opções principais
   - Prós e contras de cada uma
   - Recomendação por perfil

5. FAIXAS DE PREÇO E O QUE ESPERAR
   - Econômico (até R$ X)
   - Intermediário (R$ X a R$ Y)
   - Premium (acima de R$ Y)

6. DICAS DE MANUTENÇÃO
   - Como cuidar do produto
   - Manutenção preventiva
   - Solução de problemas comuns

7. CHECKLIST ANTES DE COMPRAR
   - Perguntas essenciais
   - Verificações importantes
   - Red flags a evitar

8. ONDE COMPRAR COM SEGURANÇA
   - Lojas confiáveis
   - Cuidados com compras online
   - Garantias e devoluções

9. RECOMENDAÇÃO FINAL
   - Resumo das melhores opções
   - Sugestão por orçamento
   - Próximos passos

## FOCO NO MERCADO:
- Preços em moeda local
- Disponibilidade regional
- Suporte e garantia local
- Compatibilidade com padrões locais

## TOM E ESTILO:
- Educativo e detalhado
- Imparcial e objetivo
- Prático e aplicável
- Acessível para todos os níveis

## REQUISITOS TÉCNICOS:
- HTML válido e semântico
- Tabelas para comparações
- Listas organizadas
- Conteúdo 100% em {IDIOMA}

## LINKS RECOMENDADOS:
- Links para reviews específicos
- Links para lojas confiáveis
- Links para manuais e especificações

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

## OBJETIVO:
Converter visitantes em clientes através de uma página persuasiva focada em resolver um problema específico.

## PÚBLICO-ALVO:
Pessoas com um problema específico que {PRODUTO} resolve, buscando solução imediata.

## PROBLEMA PRINCIPAL:
[IDENTIFICAR O PROBLEMA QUE {PRODUTO} RESOLVE]

## ESTRUTURA DA PRE-LANDING:
1. TÍTULO IMPACTANTE
   - Focado na dor do cliente
   - Promessa clara de solução
   - Gatilho emocional

2. AMPLIFICAÇÃO DO PROBLEMA
   - Consequências de não resolver
   - Impacto na vida diária
   - Custos da inação

3. APRESENTAÇÃO DA SOLUÇÃO
   - {PRODUTO} como resposta
   - Como funciona (simples)
   - Benefício principal

4. BENEFÍCIOS EMOCIONAIS E RACIONAIS
   - Lista de benefícios principais
   - Transformação prometida
   - Resultados esperados

5. PROVA SOCIAL
   - Depoimentos fictícios convincentes
   - Histórias de sucesso
   - Números e estatísticas

6. DIFERENCIAIS COMPETITIVOS
   - Por que é melhor que alternativas
   - Vantagens exclusivas
   - Inovação e tecnologia

7. OFERTA IRRECUSÁVEL
   - Preço especial (desconto)
   - Bônus exclusivos
   - Garantia estendida

8. CHAMADA PARA AÇÃO
   - Botão grande e visível
   - Texto persuasivo
   - Urgência e escassez

9. GARANTIA E SEGURANÇA
   - Remoção de objeções
   - Política de devolução
   - Selos de segurança

10. FAQ ANTIOBJEÇÕES
    - Perguntas de quem hesita
    - Respostas convincentes
    - Clareza e transparência

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

## REQUISITOS TÉCNICOS:
- HTML otimizado para conversão
- Múltiplos CTAs
- Design limpo e focado
- Conteúdo 100% em {IDIOMA}

## LINKS:
- Múltiplos links para {LINK_AFILIADO}
- Links de segurança e garantia
- Link para política de privacidade

Retorne APENAS o HTML completo da pre-landing, sem comentários extras."""

    def criar_template_comparativo(self):
        """Cria template para comparativo.txt"""
        return """# TEMPLATE PARA COMPARATIVO - {PRODUTO} vs Concorrentes

## INFORMAÇÕES BÁSICAS:
- PRODUTO PRINCIPAL: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}

## OBJETIVO:
Comparar {PRODUTO} com seus principais concorrentes para ajudar na decisão de compra.

## CONCORRENTES A COMPARAR:
1. {PRODUTO} (produto principal)
2. Concorrente A (principal concorrente)
3. Concorrente B (alternativa popular)
4. Concorrente C (opção econômica)

## ESTRUTURA DO COMPARATIVO:
1. INTRODUÇÃO À CATEGORIA
   - Visão geral do mercado
   - Principais players
   - Tendências atuais

2. TABELA COMPARATIVA COMPLETA
   - Especificações técnicas
   - Preços e custos
   - Recursos e funcionalidades
   - Garantias e suporte

3. ANÁLISE INDIVIDUAL DETALHADA
   - {PRODUTO} (análise profunda)
   - Concorrente A (pontos fortes/fracos)
   - Concorrente B (vantagens/desvantagens)
   - Concorrente C (custo-benefício)

4. COMPARAÇÃO PONTO A PONTO
   - Desempenho e velocidade
   - Qualidade e durabilidade
   - Usabilidade e experiência
   - Suporte e comunidade

5. TESTES PRÁTICOS COMPARATIVOS
   - Cenários de uso real
   - Resultados mensuráveis
   - Vencedores por categoria

6. ANÁLISE DE CUSTO-BENEFÍCIO
   - Valor por recurso
   - Retorno sobre investimento
   - Custo total de propriedade

7. RECOMENDAÇÕES POR PERFIL
   - Para quem busca performance
   - Para quem prioriza economia
   - Para quem valoriza recursos
   - Para quem precisa de simplicidade

8. CONCLUSÃO E VENCEDORES
   - Vencedor geral
   - Vencedor por categoria
   - Recomendação final

## CRITÉRIOS DE AVALIAÇÃO:
1. Desempenho (0-10)
2. Qualidade (0-10)
3. Recursos (0-10)
4. Custo-benefício (0-10)
5. Suporte (0-10)

## TOM E ESTILO:
- Objetivo e imparcial
- Detalhado e completo
- Prático e útil
- Baseado em fatos

## REQUISITOS TÉCNICOS:
- Tabelas HTML completas
- Dados comparativos claros
- Conclusões fundamentadas
- Conteúdo 100% em {IDIOMA}

## LINKS:
- Links para reviews individuais
- Links para sites oficiais
- Links para benchmarks

Retorne APENAS o HTML completo do comparativo, sem comentários extras."""

    def criar_template_analise(self):
        """Cria template para analise.txt"""
        return """# TEMPLATE PARA ANÁLISE TÉCNICA - {PRODUTO}

## INFORMAÇÕES BÁSICAS:
- PRODUTO: {PRODUTO}
- CATEGORIA: {CATEGORIA}
- IDIOMA: {IDIOMA}
- ANO: {ANO_ATUAL}

## OBJETIVO:
Fornecer uma análise técnica profunda de {PRODUTO} para usuários avançados e entusiastas.

## PÚBLICO-ALVO:
Usuários técnicos, profissionais, entusiastas e quem precisa de detalhes profundos.

## ESTRUTURA DA ANÁLISE TÉCNICA:
1. INTRODUÇÃO TÉCNICA
   - Contexto tecnológico
   - Inovações e avanços
   - Posicionamento no mercado

2. ARQUITETURA E COMPONENTES
   - Diagrama técnico conceitual
   - Componentes principais
   - Tecnologias utilizadas

3. ESPECIFICAÇÕES DETALHADAS
   - Tabela técnica completa
   - Detalhes de cada componente
   - Padrões e certificações

4. BENCHMARKS E TESTES
   - Metodologia de testes
   - Resultados quantitativos
   - Comparação com referências

5. ANÁLISE DE DESEMPENHO
   - Performance em diferentes cenários
   - Eficiência energética
   - Estabilidade e confiabilidade

6. POTENCIAL E LIMITAÇÕES
   - Capacidade de upgrade
   - Limitações técnicas
   - Compatibilidade futura

7. ANÁLISE DE CUSTO TÉCNICO
   - Custo por performance
   - Manutenção e upgrades
   - Custo total de propriedade

8. CONCLUSÃO TÉCNICA
   - Para que tipo de uso é ideal
   - Recomendações técnicas
   - Perspectivas futuras

## ASPECTOS TÉCNICOS A COBRIR:
- Processamento e computação
- Memória e armazenamento
- Conectividade e expansão
- Energia e eficiência
- Resfriamento e termais
- Software e drivers

## TOM E ESTILO:
- Técnico mas compreensível
- Detalhado e preciso
- Baseado em dados
- Objetivo e imparcial

## REQUISITOS TÉCNICOS:
- Tabelas técnicas detalhadas
- Dados específicos e verificáveis
- Referências a padrões
- Conteúdo 100% em {IDIOMA}

## LINKS:
- Links para especificações oficiais
- Links para benchmarks independentes
- Links para fóruns técnicos

Retorne APENAS o HTML completo da análise técnica, sem comentários extras."""

    def verificar_traducao_completa(self, conteudo, idioma_alvo):
        """Verifica e corrige se o conteúdo está no idioma correto"""
        
        # Lista de palavras comuns em diferentes idiomas para verificação
        palavras_verificacao = {
            'pt-BR': ['o', 'a', 'os', 'as', 'um', 'uma', 'em', 'de', 'do', 'da', 'para', 'com'],
            'en': ['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with', 'by'],
            'es': ['el', 'la', 'los', 'las', 'un', 'una', 'en', 'de', 'para', 'con'],
            'fr': ['le', 'la', 'les', 'un', 'une', 'en', 'de', 'pour', 'avec'],
            'de': ['der', 'die', 'das', 'ein', 'eine', 'in', 'von', 'für', 'mit'],
            'it': ['il', 'la', 'i', 'le', 'un', 'una', 'in', 'di', 'per', 'con']
        }
        
        idioma_base = self.normalizar_idioma_base(idioma_alvo)
        
        if idioma_base not in palavras_verificacao:
            return conteudo
        
        # Contar ocorrências de palavras do idioma alvo
        palavras_alvo = palavras_verificacao[idioma_base]
        conteudo_lower = conteudo.lower()
        
        # Verificar se há palavras em português no conteúdo em inglês (erro comum)
        if idioma_base != 'pt-BR':
            palavras_pt = palavras_verificacao['pt-BR']
            for palavra in palavras_pt:
                if palavra in conteudo_lower and len(palavra) > 2:
                    # Tentar corrigir traduções incompletas
                    print(f"   ⚠️  Detectado conteúdo em português em artigo {idioma_alvo}")
                    return conteudo
        
        return conteudo
    
    def gerar_conteudo_basico(self, produto, categoria, tipo_artigo, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera conteúdo básico SEM IA com qualidade"""
        
        # Templates específicos por tipo de artigo
        if tipo_artigo.lower() == 'review':
            return self.gerar_review_basico(produto, categoria, site_oficial, link_afiliado, idioma)
        elif tipo_artigo.lower() == 'comparativo':
            return self.gerar_comparativo_basico(produto, categoria, site_oficial, link_afiliado, idioma)
        elif tipo_artigo.lower() == 'guia':
            return self.gerar_guia_basico(produto, categoria, site_oficial, link_afiliado, idioma)
        elif tipo_artigo.lower() == 'preland':
            return self.gerar_preland_basica(produto, categoria, site_oficial, link_afiliado, idioma)
        else:
            return self.gerar_analise_basica(produto, categoria, site_oficial, link_afiliado, idioma)
    
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

<h3>Practical Testing Results</h3>
<p>During extensive testing, {produto} demonstrated solid performance across various scenarios. The product handles daily use exceptionally well, with minimal issues.</p>

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

<h3>Competitor Comparison</h3>
<p>Compared to similar products, {produto} offers a balanced combination of features and price. While not the cheapest option, it provides better value than many competitors.</p>

<h3>Final Verdict</h3>
<p>{produto} is recommended for users who seek reliable performance and good build quality. If you're looking for a solid product in the {categoria} category, this is definitely worth considering.</p>

<div class="buy-recommendation">
    <h3>Where to Buy {produto}</h3>
    <p>For the best price and guaranteed authenticity, we recommend purchasing through our trusted partner:</p>
    <a href="{link_afiliado}" class="buy-button" target="_blank" rel="nofollow sponsored">Check Current Price →</a>
    <p class="affiliate-disclosure"><small>Disclosure: We may earn a commission at no extra cost to you. Thank you for supporting our work!</small></p>
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

<h3>Resultados de Testes Práticos</h3>
<p>Durante testes extensivos, {produto} demonstrou performance sólida em vários cenários. O produto funciona excepcionalmente bem no uso diário, com problemas mínimos.</p>

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

<h3>Comparação com Concorrentes</h3>
<p>Comparado a produtos similares, {produto} oferece uma combinação equilibrada de funcionalidades e preço. Embora não seja a opção mais barata, oferece melhor custo-benefício que muitos concorrentes.</p>

<h3>Veredito Final</h3>
<p>{produto} é recomendado para usuários que buscam performance confiável e boa qualidade de construção. Se você procura um produto sólido na categoria {categoria}, esta opção definitivamente vale a pena considerar.</p>

<div class="onde-comprar">
    <h3>Onde Comprar {produto}</h3>
    <p>Para o melhor preço e autenticidade garantida, recomendamos comprar através do nosso parceiro confiável:</p>
    <a href="{link_afiliado}" class="btn-comprar" target="_blank" rel="nofollow sponsored">Ver Preço Atual →</a>
    <p class="aviso-afiliado"><small>Aviso: Podemos receber uma comissão sem custo adicional para você. Obrigado por apoiar nosso trabalho!</small></p>
</div>
"""
    
    def gerar_guia_basico(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera guia básico"""
        
        if idioma.lower().startswith('en'):
            return f"""
<h2>Complete Guide: How to Choose {produto}</h2>

<p>Choosing the right {produto} can be challenging with so many options available. This comprehensive guide will walk you through everything you need to know.</p>

<h3>Understanding {categoria}</h3>
<p>{produto} is part of the {categoria} category, which includes products designed for [main purpose]. Understanding this category is crucial for making the right choice.</p>

<h3>Key Factors to Consider</h3>
<ol>
    <li><strong>Budget:</strong> Determine how much you can realistically spend</li>
    <li><strong>Needs:</strong> Identify your specific requirements</li>
    <li><strong>Usage:</strong> Consider how often and intensely you'll use it</li>
    <li><strong>Brand Reputation:</strong> Research company history and customer support</li>
    <li><strong>Warranty:</strong> Check duration and coverage details</li>
</ol>

<h3>Technical Terms Explained</h3>
<table>
    <tr>
        <th>Term</th>
        <th>Meaning</th>
        <th>Why It Matters</th>
    </tr>
    <tr>
        <td>[Term 1]</td>
        <td>Simple explanation</td>
        <td>Impact on performance</td>
    </tr>
    <tr>
        <td>[Term 2]</td>
        <td>Simple explanation</td>
        <td>Affects longevity</td>
    </tr>
</table>

<h3>Recommended Price Ranges</h3>
<ul>
    <li><strong>Budget (Under $X):</strong> Basic functionality, good for occasional use</li>
    <li><strong>Mid-Range ($X-$Y):</strong> Best value, suitable for regular use</li>
    <li><strong>Premium (Above $Y):</strong> Professional features, ideal for heavy use</li>
</ul>

<h3>Maintenance Tips</h3>
<p>Proper maintenance extends the life of your {produto}. Follow these basic tips:</p>
<ul>
    <li>Clean regularly according to manufacturer instructions</li>
    <li>Store in appropriate conditions</li>
    <li>Avoid exposure to extreme temperatures</li>
    <li>Perform regular checks as recommended</li>
</ul>

<h3>Final Checklist</h3>
<p>Before making your purchase, ask yourself:</p>
<ol>
    <li>Does it meet my specific needs?</li>
    <li>Is it within my budget?</li>
    <li>What do customer reviews say?</li>
    <li>What's the return policy?</li>
    <li>Is support readily available?</li>
</ol>
"""
        else:
            return f"""
<h2>Guia Completo: Como Escolher {produto}</h2>

<p>Escolher o {produto} certo pode ser desafiador com tantas opções disponíveis. Este guia completo vai orientá-lo em tudo o que você precisa saber.</p>

<h3>Entendendo a Categoria {categoria}</h3>
<p>{produto} faz parte da categoria {categoria}, que inclui produtos projetados para [propósito principal]. Entender esta categoria é crucial para fazer a escolha certa.</p>

<h3>Fatores Chave a Considerar</h3>
<ol>
    <li><strong>Orçamento:</strong> Determine quanto você pode gastar realisticamente</li>
    <li><strong>Necessidades:</strong> Identifique seus requisitos específicos</li>
    <li><strong>Uso:</strong> Considere com que frequência e intensidade você usará</li>
    <li><strong>Reputação da Marca:</strong> Pesquise histórico da empresa e suporte ao cliente</li>
    <li><strong>Garantia:</strong> Verifique duração e detalhes da cobertura</li>
</ol>

<h3>Termos Técnicos Explicados</h3>
<table>
    <tr>
        <th>Termo</th>
        <th>Significado</th>
        <th>Por que é importante</th>
    </tr>
    <tr>
        <td>[Termo 1]</td>
        <td>Explicação simples</td>
        <td>Impacto na performance</td>
    </tr>
    <tr>
        <td>[Termo 2]</td>
        <td>Explicação simples</td>
        <td>Afeta a durabilidade</td>
    </tr>
</table>

<h3>Faixas de Preço Recomendadas</h3>
<ul>
    <li><strong>Econômico (Até R$ X):</strong> Funcionalidades básicas, bom para uso ocasional</li>
    <li><strong>Intermediário (R$ X a R$ Y):</strong> Melhor custo-benefício, adequado para uso regular</li>
    <li><strong>Premium (Acima de R$ Y):</strong> Funcionalidades profissionais, ideal para uso intensivo</li>
</ul>

<h3>Dicas de Manutenção</h3>
<p>A manutenção adequada prolonga a vida do seu {produto}. Siga estas dicas básicas:</p>
<ul>
    <li>Limpe regularmente conforme instruções do fabricante</li>
    <li>Armazene em condições apropriadas</li>
    <li>Evite exposição a temperaturas extremas</li>
    <li>Realize verificações regulares conforme recomendado</li>
</ul>

<h3>Checklist Final</h3>
<p>Antes de fazer sua compra, pergunte a si mesmo:</p>
<ol>
    <li>Atende minhas necessidades específicas?</li>
    <li>Está dentro do meu orçamento?</li>
    <li>O que dizem as avaliações de clientes?</li>
    <li>Qual é a política de devolução?</li>
    <li>O suporte está facilmente disponível?</li>
</ol>
"""
    
    def gerar_preland_basica(self, produto, categoria, site_oficial, link_afiliado, idioma='pt-BR'):
        """Gera pre-landing page básica"""
        
        problema = {
            'healthcare': 'saúde e bem-estar',
            'games': 'entretenimento de qualidade',
            'smartphones': 'conectividade e produtividade',
            'computadores': 'performance e eficiência',
            'eletrodomesticos': 'conforto e praticidade'
        }.get(categoria.lower(), 'solução eficaz')
        
        if idioma.lower().startswith('en'):
            return f"""
<div class="preland-hero">
    <h1>Tired of {problema} Problems? Discover {produto}!</h1>
    <p class="subtitle">The solution you've been searching for is finally here.</p>
</div>

<div class="problem-section">
    <h2>The {problema} Problem We All Face</h2>
    <p>If you're like most people, you've struggled with {problema}. The frustration, the inconvenience, the feeling that there must be a better way...</p>
    
    <ul class="pain-points">
        <li>Wasting time with ineffective solutions</li>
        <li>Spending money without seeing results</li>
        <li>Feeling stuck in the same routine</li>
        <li>Missing out on better opportunities</li>
    </ul>
</div>

<div class="solution-section">
    <h2>Introducing {produto}: Your Solution</h2>
    <p>{produto} is specifically designed to address {problema} challenges. Through innovative technology and proven methods, it offers what other solutions can't.</p>
    
    <div class="benefits-grid">
        <div class="benefit">
            <h3>✅ Effective Results</h3>
            <p>See noticeable improvements quickly</p>
        </div>
        <div class="benefit">
            <h3>✅ Easy to Use</h3>
            <p>Simple setup and intuitive operation</p>
        </div>
        <div class="benefit">
            <h3>✅ Proven Method</h3>
            <p>Based on reliable principles and testing</p>
        </div>
        <div class="benefit">
            <h3>✅ Great Value</h3>
            <p>Affordable compared to alternatives</p>
        </div>
    </div>
</div>

<div class="testimonials">
    <h2>What Users Are Saying</h2>
    
    <div class="testimonial">
        <p>"I was skeptical at first, but {produto} really works! It solved my {problema} problem in just a few days."</p>
        <p class="author">- Sarah M., Verified User</p>
    </div>
    
    <div class="testimonial">
        <p>"After trying several options, {produto} was the only one that delivered real results. Highly recommended!"</p>
        <p class="author">- John D., Satisfied Customer</p>
    </div>
</div>

<div class="offer-section">
    <h2>Special Limited Time Offer</h2>
    
    <div class="offer-details">
        <div class="original-price">Regular Price: $199</div>
        <div class="current-price">Today Only: $149</div>
        <div class="savings">Save $50 + Free Shipping</div>
    </div>
    
    <div class="bonuses">
        <h3>Plus These Exclusive Bonuses:</h3>
        <ul>
            <li>✅ Free E-book Guide (Value: $29)</li>
            <li>✅ Premium Support Access</li>
            <li>✅ 30-Day Money Back Guarantee</li>
        </ul>
    </div>
    
    <div class="cta-main">
        <a href="{link_afiliado}" class="cta-button" target="_blank" rel="nofollow sponsored">
            <span class="cta-text">Get {produto} Now</span>
            <span class="cta-subtext">Limited Time Offer - Click Here</span>
        </a>
        <p class="guarantee">✅ 100% Satisfaction Guarantee | 🔒 Secure Checkout</p>
    </div>
</div>

<div class="faq-section">
    <h2>Frequently Asked Questions</h2>
    
    <div class="faq-item">
        <h3>How quickly will I see results?</h3>
        <p>Most users notice improvements within the first week, with full benefits typically realized within 30 days.</p>
    </div>
    
    <div class="faq-item">
        <h3>Is there a money-back guarantee?</h3>
        <p>Yes! We offer a full 30-day money-back guarantee. If you're not satisfied for any reason, simply return it for a full refund.</p>
    </div>
</div>
"""
        else:
            return f"""
<div class="preland-hero">
    <h1>Cansado de Problemas com {problema}? Descubra {produto}!</h1>
    <p class="subtitle">A solução que você procurava finalmente está aqui.</p>
</div>

<div class="problem-section">
    <h2>O Problema de {problema} que Todos Enfrentamos</h2>
    <p>Se você é como a maioria das pessoas, já lutou com {problema}. A frustração, o inconveniente, a sensação de que deve haver uma maneira melhor...</p>
    
    <ul class="pain-points">
        <li>Perdendo tempo com soluções ineficazes</li>
        <li>Gastando dinheiro sem ver resultados</li>
        <li>Sentindo-se preso na mesma rotina</li>
        <li>Perdendo melhores oportunidades</li>
    </ul>
</div>

<div class="solution-section">
    <h2>Apresentando {produto}: Sua Solução</h2>
    <p>{produto} é especificamente projetado para enfrentar os desafios de {problema}. Através de tecnologia inovadora e métodos comprovados, oferece o que outras soluções não conseguem.</p>
    
    <div class="benefits-grid">
        <div class="benefit">
            <h3>✅ Resultados Eficazes</h3>
            <p>Veja melhorias notáveis rapidamente</p>
        </div>
        <div class="benefit">
            <h3>✅ Fácil de Usar</h3>
            <p>Configuração simples e operação intuitiva</p>
        </div>
        <div class="benefit">
            <h3>✅ Método Comprovado</h3>
            <p>Baseado em princípios e testes confiáveis</p>
        </div>
        <div class="benefit">
            <h3>✅ Ótimo Custo-Benefício</h3>
            <p>Acessível comparado a alternativas</p>
        </div>
    </div>
</div>

<div class="depoimentos">
    <h2>O que os Usuários Estão Dizendo</h2>
    
    <div class="depoimento">
        <p>"Eu estava cético no início, mas {produto} realmente funciona! Resolveu meu problema de {problema} em poucos dias."</p>
        <p class="autor">- Carlos S., Usuário Verificado</p>
    </div>
    
    <div class="depoimento">
        <p>"Depois de tentar várias opções, {produto} foi a única que entregou resultados reais. Altamente recomendado!"</p>
        <p class="autor">- Ana P., Cliente Satisfeita</p>
    </div>
</div>

<div class="oferta-section">
    <h2>Oferta Especial por Tempo Limitado</h2>
    
    <div class="oferta-detalhes">
        <div class="preco-original">Preço Normal: R$ 999</div>
        <div class="preco-atual">Apenas Hoje: R$ 749</div>
        <div class="economia">Economize R$ 250 + Frete Grátis</div>
    </div>
    
    <div class="bonus">
        <h3>Mais Estes Bônus Exclusivos:</h3>
        <ul>
            <li>✅ Guia em E-book Grátis (Valor: R$ 99)</li>
            <li>✅ Acesso ao Suporte Premium</li>
            <li>✅ Garantia de 30 Dias</li>
        </ul>
    </div>
    
    <div class="cta-principal">
        <a href="{link_afiliado}" class="cta-button" target="_blank" rel="nofollow sponsored">
            <span class="cta-text">Adquira {produto} Agora</span>
            <span class="cta-subtext">Oferta por Tempo Limitado - Clique Aqui</span>
        </a>
        <p class="garantia">✅ 100% de Satisfação Garantida | 🔒 Compra Segura</p>
    </div>
</div>

<div class="faq-section">
    <h2>Perguntas Frequentes</h2>
    
    <div class="faq-item">
        <h3>Quão rápido verei resultados?</h3>
        <p>A maioria dos usuários nota melhorias dentro da primeira semana, com benefícios completos tipicamente realizados em 30 dias.</p>
    </div>
    
    <div class="faq-item">
        <h3>Há garantia de devolução do dinheiro?</h3>
        <p>Sim! Oferecemos garantia total de 30 dias. Se não estiver satisfeito por qualquer motivo, simplesmente devolva para reembolso total.</p>
    </div>
</div>
"""
    
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
            r'^Vamos.*?(?=<)',
            r'^Here is.*?(?=<)',
            r'^Following.*?(?=<)',
            r'^Let me.*?(?=<)',
            r'^Aquí está.*?(?=<)',
            r'^Voici.*?(?=<)',
            r'^Hier ist.*?(?=<)'
        ]
        
        for padrao in padroes:
            texto = re.sub(padrao, '', texto, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove comentários HTML
        texto = re.sub(r'<!--.*?-->', '', texto, flags=re.DOTALL)
        
        # Remove espaços em excesso
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        texto = texto.strip()
        
        return texto
    
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
        
        # Carregar templates
        header = self.carregar_template("header.html")
        if not header:
            header = self.criar_header_basico(idioma)
        
        footer = self.carregar_template("footer.html")
        if not footer:
            footer = self.criar_footer_basico(idioma)
        
        # Criar descrição SEO baseada no idioma
        if idioma.lower().startswith('en'):
            if is_preland:
                descricao_seo = f"Discover everything about {nome_original}. Complete guide, detailed analysis, and where to buy at the best price. Read our comprehensive review!"
            else:
                descricao_seo = f"Complete {tipo_artigo} of {nome_original}. Detailed analysis, specifications, where to buy and if it's worth it. Check out our honest review!"
        else:
            if is_preland:
                descricao_seo = f"Descubra tudo sobre {nome_original}. Guia completo, análise detalhada e onde comprar pelo melhor preço. Leia nosso review abrangente!"
            else:
                descricao_seo = f"{tipo_artigo.title()} completo do {nome_original}. Análise detalhada, especificações, onde comprar e se vale a pena. Confira nosso review honesto!"
        
        # Palavras-chave SEO
        keywords_seo = f"{nome_original}, {categoria}, {tipo_artigo}, comprar, preço, análise, review"
        
        # Obter imagem
        imagem_principal = self.obter_url_imagem(nome_original, categoria)
        alt_imagem = self.criar_alt_imagem(nome_original)
        
        # Normalizar código de idioma para HTML
        idioma_html = self.normalizar_idioma_html(idioma)
        
        # Sidebar conteúdo (preenchido automaticamente)
        sidebar_content = self.criar_sidebar_conteudo(categoria, produto_slug, nome_original, link_afiliado, idioma, is_preland)
        
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

            <div class="article-body">
                {conteudo_html if conteudo_html else '<p>Conteúdo do artigo...</p>'}
            </div>

            {self.criar_secao_avaliacao(nome_original, idioma)}
            
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
    
    def criar_sidebar_conteudo(self, categoria, produto_slug, nome_original, link_afiliado, idioma='pt-BR', is_preland=False):
        """Cria conteúdo da sidebar automaticamente"""
        
        # Gerar desconto aleatório
        desconto = random.randint(15, 30)
        meses_garantia = random.randint(12, 24)
        
        # Outros produtos da mesma categoria (fictícios)
        outros_produtos = self.gerar_outros_produtos_categoria(categoria, nome_original, idioma)
        
        if idioma.lower().startswith('en'):
            return f'''
            <div class="widget">
                <h3><i class="fas fa-bolt"></i> Limited Offer</h3>
                <p><strong>{nome_original} with {desconto}% OFF</strong></p>
                <p>Free shipping + {meses_garantia} months warranty</p>
                <a href="{link_afiliado}" class="btn-sidebar" target="_blank" rel="nofollow sponsored">Get It Now</a>
            </div>

            <div class="widget">
                <h3><i class="fas fa-link"></i> More {categoria.title()}</h3>
                {outros_produtos}
                <p><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', f'{categoria}/index.html')}">View all products →</a></p>
            </div>

            <div class="widget">
                <h3><i class="fas fa-info-circle"></i> Information</h3>
                <ul class="site-links">
                    <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'sobre-nos.html')}">About Us</a></li>
                    <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'politica-de-privacidade.html')}">Privacy Policy</a></li>
                    <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'contato.html')}">Contact</a></li>
                </ul>
            </div>
            
            <div class="widget">
                <h3><i class="fas fa-star"></i> Why Choose Us?</h3>
                <ul class="benefits-list">
                    <li>✅ Honest and unbiased reviews</li>
                    <li>✅ Updated price comparisons</li>
                    <li>✅ Expert buying guides</li>
                    <li>✅ Secure affiliate links</li>
                </ul>
            </div>
            '''
        else:
            return f'''
            <div class="widget">
                <h3><i class="fas fa-bolt"></i> Oferta Limitada</h3>
                <p><strong>{nome_original} com {desconto}% OFF</strong></p>
                <p>Frete grátis + {meses_garantia} meses de garantia</p>
                <a href="{link_afiliado}" class="btn-sidebar" target="_blank" rel="nofollow sponsored">Aproveitar Agora</a>
            </div>

            <div class="widget">
                <h3><i class="fas fa-link"></i> Mais {categoria.title()}</h3>
                {outros_produtos}
                <p><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', f'{categoria}/index.html')}">Ver todos os produtos →</a></p>
            </div>

            <div class="widget">
                <h3><i class="fas fa-info-circle"></i> Informações</h3>
                <ul class="site-links">
                    <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'sobre-nos.html')}">Sobre Nós</a></li>
                    <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'politica-de-privacidade.html')}">Política de Privacidade</a></li>
                    <li><a href="{self.calcular_caminho_relativo(f'{categoria}/{produto_slug}/', 'contato.html')}">Contato</a></li>
                </ul>
            </div>
            
            <div class="widget">
                <h3><i class="fas fa-star"></i> Por que Escolher a Gente?</h3>
                <ul class="benefits-list">
                    <li>✅ Reviews honestos e imparciais</li>
                    <li>✅ Comparações de preços atualizadas</li>
                    <li>✅ Guias de compra especializados</li>
                    <li>✅ Links afiliados seguros</li>
                </ul>
            </div>
            '''
    
    def gerar_outros_produtos_categoria(self, categoria, produto_atual, idioma):
        """Gera lista de outros produtos da mesma categoria"""
        
        produtos_por_categoria = {
            'healthcare': [
                'Prodentim Advanced',
                'Oral Health Pro',
                'Dental Care Plus',
                'Healthy Smile Formula'
            ],
            'games': [
                'PlayStation 5 Pro',
                'Xbox Series X Elite',
                'Nintendo Switch OLED',
                'Gaming PC Ultimate'
            ],
            'smartphones': [
                'iPhone 16 Pro Max',
                'Samsung Galaxy S25',
                'Google Pixel 9',
                'Xiaomi 14 Ultra'
            ],
            'computadores': [
                'MacBook Pro M4',
                'Dell XPS 15',
                'Asus ROG Zephyrus',
                'Lenovo ThinkPad X1'
            ],
            'eletrodomesticos': [
                'Air Fryer Pro',
                'Robot Vacuum X10',
                'Smart Coffee Maker',
                'Induction Cooktop'
            ]
        }
        
        produtos = produtos_por_categoria.get(categoria.lower(), ['Product A', 'Product B', 'Product C'])
        
        # Remover o produto atual da lista
        produtos = [p for p in produtos if p.lower() not in produto_atual.lower()]
        
        # Pegar até 3 produtos
        produtos = produtos[:3]
        
        if idioma.lower().startswith('en'):
            items = '\n'.join([f'<p><a href="{self.criar_slug(p)}/index.html">{p}</a></p>' for p in produtos])
        else:
            items = '\n'.join([f'<p><a href="{self.criar_slug(p)}/index.html">{p}</a></p>' for p in produtos])
        
        return items
    
    def criar_secao_avaliacao(self, produto, idioma):
        """Cria seção de avaliação"""
        
        rating = random.uniform(4.3, 4.9)
        num_avaliacoes = random.randint(50, 250)
        
        if idioma.lower().startswith('en'):
            return f'''
            <div class="rating-section">
                <h3>Reader Ratings</h3>
                <div class="stars">{"★" * 5}</div>
                <p>{rating:.1f} out of 5 ({num_avaliacoes} ratings)</p>
                <div class="rating-details">
                    <div class="rating-bar">
                        <span>5 stars</span>
                        <div class="bar"><div class="fill" style="width: {random.randint(65, 85)}%"></div></div>
                        <span>{random.randint(65, 85)}%</span>
                    </div>
                    <div class="rating-bar">
                        <span>4 stars</span>
                        <div class="bar"><div class="fill" style="width: {random.randint(15, 25)}%"></div></div>
                        <span>{random.randint(15, 25)}%</span>
                    </div>
                </div>
            </div>
            '''
        else:
            return f'''
            <div class="rating-section">
                <h3>Avaliação dos Leitores</h3>
                <div class="stars">{"★" * 5}</div>
                <p>{rating:.1f} de 5 ({num_avaliacoes} avaliações)</p>
                <div class="rating-details">
                    <div class="rating-bar">
                        <span>5 estrelas</span>
                        <div class="bar"><div class="fill" style="width: {random.randint(65, 85)}%"></div></div>
                        <span>{random.randint(65, 85)}%</span>
                    </div>
                    <div class="rating-bar">
                        <span>4 estrelas</span>
                        <div class="bar"><div class="fill" style="width: {random.randint(15, 25)}%"></div></div>
                        <span>{random.randint(15, 25)}%</span>
                    </div>
                </div>
            </div>
            '''
    
    def criar_secao_cta(self, produto, link_afiliado, idioma, is_preland=False):
        """Cria seção de call-to-action"""
        
        if is_preland:
            # CTA mais agressivo para pre-landing
            if idioma.lower().startswith('en'):
                return f'''
                <div class="cta-premium">
                    <div class="cta-header">
                        <h3>🚀 Special Limited Time Launch Offer!</h3>
                        <p class="discount">Save {random.randint(25, 40)}% Today Only</p>
                    </div>
                    
                    <div class="cta-benefits">
                        <ul>
                            <li><i class="fas fa-check-circle"></i> <strong>Free Worldwide Shipping</strong></li>
                            <li><i class="fas fa-check-circle"></i> <strong>{random.randint(12, 36)} Month Extended Warranty</strong></li>
                            <li><i class="fas fa-check-circle"></i> <strong>Exclusive Bonus Package Included</strong></li>
                            <li><i class="fas fa-check-circle"></i> <strong>30-Day Money Back Guarantee</strong></li>
                        </ul>
                    </div>
                    
                    <div class="cta-button-container">
                        <a href="{link_afiliado}" class="cta-button-premium" target="_blank" rel="nofollow sponsored">
                            <span class="cta-main-text">GET {produto.upper()} NOW</span>
                            <span class="cta-sub-text">Limited Stock Available - Click to Secure Yours</span>
                        </a>
                    </div>
                    
                    <div class="cta-security">
                        <p><i class="fas fa-lock"></i> 256-bit SSL Secure Checkout | <i class="fas fa-shield-alt"></i> Trusted by {random.randint(5000, 15000)}+ Customers</p>
                    </div>
                </div>
                '''
            else:
                return f'''
                <div class="cta-premium">
                    <div class="cta-header">
                        <h3>🚀 Oferta de Lançamento por Tempo Limitado!</h3>
                        <p class="discount">Economize {random.randint(25, 40)}% Apenas Hoje</p>
                    </div>
                    
                    <div class="cta-benefits">
                        <ul>
                            <li><i class="fas fa-check-circle"></i> <strong>Frete Grátis Mundial</strong></li>
                            <li><i class="fas fa-check-circle"></i> <strong>Garantia Estendida de {random.randint(12, 36)} Meses</strong></li>
                            <li><i class="fas fa-check-circle"></i> <strong>Pacote de Bônus Exclusivo Incluso</strong></li>
                            <li><i class="fas fa-check-circle"></i> <strong>Garantia de 30 Dias</strong></li>
                        </ul>
                    </div>
                    
                    <div class="cta-button-container">
                        <a href="{link_afiliado}" class="cta-button-premium" target="_blank" rel="nofollow sponsored">
                            <span class="cta-main-text">ADQUIRA {produto.upper()} AGORA</span>
                            <span class="cta-sub-text">Estoque Limitado - Clique para Garantir o Seu</span>
                        </a>
                    </div>
                    
                    <div class="cta-security">
                        <p><i class="fas fa-lock"></i> Checkout Seguro com SSL 256-bit | <i class="fas fa-shield-alt"></i> Confiado por {random.randint(5000, 15000)}+ Clientes</p>
                    </div>
                </div>
                '''
        else:
            # CTA normal para reviews/guides
            if idioma.lower().startswith('en'):
                return f'''
                <div class="cta">
                    <h3>Ready to Experience {produto}?</h3>
                    <p>Get the best price and conditions through our special link:</p>
                    <a href="{link_afiliado}" class="btn-cta" target="_blank" rel="nofollow sponsored">
                        <i class="fas fa-shopping-cart"></i> View Special Offer
                    </a>
                    <p class="affiliate-notice"><small>💡 Affiliate links: you don't pay anything extra, but we earn a small commission. Thank you for supporting us!</small></p>
                </div>
                '''
            else:
                return f'''
                <div class="cta">
                    <h3>Pronto para Experimentar {produto}?</h3>
                    <p>Garanta o melhor preço e condições através do nosso link especial:</p>
                    <a href="{link_afiliado}" class="btn-cta" target="_blank" rel="nofollow sponsored">
                        <i class="fas fa-shopping-cart"></i> Ver Oferta Especial
                    </a>
                    <p class="affiliate-notice"><small>💡 Links afiliados: você não paga nada a mais, mas ganhamos uma pequena comissão. Obrigado pelo apoio!</small></p>
                </div>
                '''
    
    def criar_header_basico(self, idioma='pt-BR'):
        """Cria header básico baseado no idioma"""
        
        if idioma.lower().startswith('en'):
            return '''<header class="site-header">
    <div class="container">
        <div class="logo">
            <a href="../index.html">🔥 Top Offers</a>
        </div>
        <nav class="main-nav">
            <a href="../index.html">Home</a>
            <a href="../eletrodomesticos/index.html">Home Appliances</a>
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
        """Cria footer básico baseado no idioma"""
        
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
                # Não incluir pre-landing pages no índice principal
                if '-guia-completo' not in item.name:
                    produtos.append({
                        'slug': item.name,
                        'nome': item.name.replace('-', ' ').title(),
                        'data': datetime.fromtimestamp((item / "index.html").stat().st_mtime)
                    })
        
        if not produtos:
            return
        
        # Ordenar por data
        produtos.sort(key=lambda x: x['data'], reverse=True)
        
        # Determinar título baseado no idioma
        if idioma.lower().startswith('en'):
            titulo = f"{categoria.title()} - {self.config['site']['name']}"
            descricao = f"Check out our reviews and analysis of {categoria}:"
            ver_todos = "View all products"
            voltar = "← Back to Home"
        else:
            titulo = f"{categoria.title()} - {self.config['site']['name']}"
            descricao = f"Confira nossos reviews e análises de {categoria}:"
            ver_todos = "Ver todos os produtos"
            voltar = "← Voltar para Home"
        
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
                <a href="{produto['slug']}/index.html" class="btn-read">{ver_todos} →</a>
            </div>
'''
        
        html += f'''
        </div>
        <a href="../index.html" class="btn-home">{voltar}</a>
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
        
        priority_elem = ET.SubElement(urlset, 'priority')
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
                ["produto", "idioma", "categoria", "tipo_artigo", "site_oficial", "links_afiliados", "status", "data_publicacao", "url_publicada"],
                ["Console Playstation 5 Slim", "pt-BR", "games", "review", "https://playstation.com", "https://afiliado.com/ps5", "pending", "", ""],
                ["iPhone 15 Pro", "en-US", "smartphones", "review", "https://apple.com", "https://afiliado.com/iphone", "pending", "", ""],
                ["Prodentim Review", "en-US", "healthcare", "review", "https://us-prodintim.com", "www.meulink.com", "pending", "", ""],
                ["Prodentim Guia", "en-US", "healthcare", "preland", "https://us-prodintim.com", "www.meulinkguia.com", "pending", "", ""],
                ["Samsung Galaxy S24 Ultra", "pt-BR", "smartphones", "review", "https://samsung.com", "https://afiliado.com/s24", "pending", "", ""],
                ["MacBook Pro M3", "en-US", "computadores", "review", "https://apple.com", "https://afiliado.com/macbook", "pending", "", ""]
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
        
        stats = {'total': 0, 'pending': 0, 'completed': 0, 'idiomas': {}, 'tipos': {}}
        for p in produtos:
            stats['total'] += 1
            status = p.get('status', 'pending')
            if status == 'completed':
                stats['completed'] += 1
            else:
                stats['pending'] += 1
            
            # Contar idiomas
            idioma = p.get('idioma', 'pt-BR')
            if idioma not in stats['idiomas']:
                stats['idiomas'][idioma] = 0
            stats['idiomas'][idioma] += 1
            
            # Contar tipos
            tipo = p.get('tipo_artigo', 'review')
            if tipo not in stats['tipos']:
                stats['tipos'][tipo] = 0
            stats['tipos'][tipo] += 1
        
        print(f"📁 Total: {stats['total']}")
        print(f"✅ Concluídos: {stats['completed']}")
        print(f"⏳ Pendentes: {stats['pending']}")
        if stats['total'] > 0:
            print(f"🎯 Progresso: {(stats['completed']/stats['total']*100):.1f}%")
        
        # Idiomas
        print(f"🌐 Idiomas: {', '.join([f'{k} ({v})' for k, v in stats['idiomas'].items()])}")
        
        # Tipos
        print(f"📄 Tipos: {', '.join([f'{k} ({v})' for k, v in stats['tipos'].items()])}")
        
        # Artigos gerados
        artigos = list(self.docs_dir.glob("**/index.html"))
        print(f"📄 Artigos no site: {len(artigos)}")
        
        # Categorias com artigos
        categorias = set()
        for artigo in artigos:
            categoria = artigo.parent.parent.name
            categorias.add(categoria)
        
        print(f"📂 Categorias ativas: {len(categorias)}")
    
    # ==================== PROCESSAMENTO PRINCIPAL ====================
    
    def gerar_funnel_completo(self, produto_data):
        """Gera funnel completo: review + pre-landing page"""
        
        # Extrair dados
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
        
        # Gerar conteúdo do review
        conteudo_review = self.gerar_conteudo_com_ia(
            nome, categoria, 'review', site_oficial, link_afiliado, idioma
        )
        
        if not conteudo_review:
            print(f"   ❌ Falha ao gerar review")
            return False
        
        # Salvar review
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
            print(f"   ❌ Falha ao salvar review")
            return False
        
        print(f"   ✅ Review criado: {categoria}/{slug_review}/")
        
        # 2. Gerar PRE-LANDING (guia)
        print(f"   📝 2. Gerando PRE-LANDING...")
        slug_preland = f"{self.criar_slug(nome)}-guia-completo"
        titulo_preland = self.criar_titulo_seo(nome, 'preland', idioma)
        
        # Gerar conteúdo da pre-landing
        conteudo_preland = self.gerar_conteudo_com_ia(
            nome, categoria, 'preland', site_oficial, link_afiliado, idioma
        )
        
        if not conteudo_preland:
            print(f"   ⚠️  Falha ao gerar pre-landing, usando conteúdo básico")
            conteudo_preland = self.gerar_preland_basica(nome, categoria, site_oficial, link_afiliado, idioma)
        
        # Salvar pre-landing
        caminho_preland = self.criar_artigo_completo(
            titulo=titulo_preland,
            conteudo_html=conteudo_preland,
            categoria=categoria,
            produto_slug=slug_preland,
            tipo_artigo='preland',
            nome_original=nome,
            site_oficial=site_oficial,
            link_afiliado=link_afiliado,
            idioma=idioma,
            is_preland=True
        )
        
        if caminho_preland:
            print(f"   ✅ Pre-landing criada: {categoria}/{slug_preland}/")
        
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
            idioma = produto_data.get('idioma', 'pt-BR').strip()
            
            # Pular se já concluído
            if status == 'completed':
                print(f"   ⏭️  Já concluído: {nome[:40]}")
                continue
            
            print(f"   📦 {nome}")
            print(f"   📁 {categoria} • {tipo} • 🌐 {idioma}")
            
            # Gerar funnel ou artigo único baseado no tipo
            if tipo == 'preland' and self.config['funnel']['enable_preland']:
                # Gerar funnel completo
                sucesso = self.gerar_funnel_completo(produto_data)
                status_final = "completed" if sucesso else "error"
                
                # Atualizar CSV
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
                        print(f"   ❌ Erro ao gerar artigo")
                        self.atualizar_csv_apos_geracao(produto_data, None, "error")
                    
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    self.atualizar_csv_apos_geracao(produto_data, None, "error")
                    continue
            
            # Pausa para IA
            if tem_ia and i < len(produtos):
                delay = random.randint(3, 6)
                print(f"   ⏳ Aguardando {delay}s...")
                sleep(delay)
        
        print("\n" + "="*70)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("="*70)
        print(f"📊 {len(produtos)} produtos processados")
        print(f"📁 Artigos em: {self.docs_dir}/")
        print(f"🗺️  Sitemap: {self.site_url}/sitemap.xml")
        print("="*70)
        
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
            print("2. 🎨 Criar templates básicos")
            print("3. 📱 Gerar artigo de teste")
            print("4. ✍️  Gerar artigo manual")
            print("5. 🚀 PROCESSAR TABELA COMPLETA (FUNNEL)")
            print("6. 📊 Painel de controle")
            print("7. 🗺️  Criar/atualizar sitemap")
            print("8. ⚙️  Configurações")
            print("9. 🤖 Configurar IA")
            print("10. 📝 Editar conteúdo padrão")
            print("11. 🔄 Gerar funnel para produto específico")
            print("12. ❌ Sair")
            
            try:
                opcao = input("\n🎯 Escolha (1-12): ").strip()
                
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
                    self.gerar_funnel_manual()
                elif opcao == "12":
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
            (self.templates_dir / "preland.txt", "Template Pre-landing"),
            (self.templates_dir / "analise.txt", "Template Análise")
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
        
        # Verificar categorias
        categorias = []
        for artigo in artigos:
            categoria = artigo.parent.parent.name
            if categoria not in categorias and categoria not in ['assets', 'includes']:
                categorias.append(categoria)
        
        print(f"📂 Categorias com conteúdo: {len(categorias)}")
        if categorias:
            print(f"   → {', '.join(categorias)}")
    
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
.logo a { color: white; text-decoration: none; font-size: 1.5rem; font-weight: bold; display: flex; align-items: center; }
.logo a:before { content: "🔥"; margin-right: 8px; }
.main-nav { display: flex; gap: 20px; }
.main-nav a { color: white; text-decoration: none; padding: 5px 10px; border-radius: 4px; transition: background 0.3s; }
.main-nav a:hover { background: rgba(255,255,255,0.1); }

/* Main Content */
.main-container { display: grid; grid-template-columns: 2fr 1fr; gap: 40px; padding: 40px 0; }
@media (max-width: 992px) { .main-container { grid-template-columns: 1fr; } }
.content { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.article-meta { display: flex; flex-wrap: wrap; gap: 15px; color: #666; font-size: 0.9rem; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
.article-meta span { display: flex; align-items: center; gap: 5px; }
.featured-image { width: 100%; height: 400px; object-fit: cover; border-radius: 10px; margin: 25px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.article-body { font-size: 1.05rem; line-height: 1.8; }
.article-body h2 { color: #1a3a8f; margin: 30px 0 15px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }
.article-body h3 { color: #2c3e50; margin: 25px 0 12px; }
.article-body table { width: 100%; border-collapse: collapse; margin: 20px 0; }
.article-body th { background: #f8f9fa; padding: 12px; text-align: left; border: 1px solid #ddd; }
.article-body td { padding: 12px; border: 1px solid #ddd; }
.article-body ul, .article-body ol { margin: 15px 0; padding-left: 20px; }
.article-body li { margin: 8px 0; }

/* Sidebar */
.sidebar { position: sticky; top: 20px; align-self: start; }
.widget { background: white; padding: 25px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 3px 15px rgba(0,0,0,0.05); }
.widget h3 { color: #1a3a8f; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
.btn-sidebar { display: inline-block; background: linear-gradient(135deg, #3498db 0%, #1a73e8 100%); color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; transition: transform 0.3s, box-shadow 0.3s; }
.btn-sidebar:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3); }
.benefits-list { list-style: none; padding: 0; }
.benefits-list li { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.benefits-list li:last-child { border-bottom: none; }

/* Rating Section */
.rating-section { background: #f8f9fa; padding: 25px; border-radius: 10px; margin: 30px 0; text-align: center; }
.rating-section h3 { margin-bottom: 15px; color: #2c3e50; }
.stars { color: #ffc107; font-size: 2rem; margin: 10px 0; }
.rating-details { max-width: 300px; margin: 20px auto; }
.rating-bar { display: flex; align-items: center; gap: 10px; margin: 8px 0; }
.rating-bar span { min-width: 60px; }
.rating-bar .bar { flex: 1; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; }
.rating-bar .fill { height: 100%; background: linear-gradient(90deg, #ffc107, #ff9800); }

/* CTA Sections */
.cta { background: linear-gradient(135deg, #1a3a8f 0%, #2c3e50 100%); color: white; padding: 30px; border-radius: 12px; margin: 40px 0; text-align: center; }
.cta h3 { margin-bottom: 15px; font-size: 1.5rem; }
.btn-cta { display: inline-block; background: #ff6b6b; color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-size: 1.1rem; font-weight: bold; margin: 15px 0; transition: transform 0.3s, box-shadow 0.3s; }
.btn-cta:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4); }
.affiliate-notice { font-size: 0.9rem; opacity: 0.9; margin-top: 15px; }

/* Premium CTA */
.cta-premium { background: linear-gradient(135deg, #1a237e 0%, #283593 100%); color: white; padding: 40px; border-radius: 16px; margin: 40px 0; }
.cta-header { text-align: center; margin-bottom: 30px; }
.cta-header .discount { display: inline-block; background: #ff4081; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; margin-top: 10px; }
.cta-benefits ul { list-style: none; padding: 0; max-width: 600px; margin: 0 auto 30px; }
.cta-benefits li { padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 12px; }
.cta-benefits li:last-child { border-bottom: none; }
.cta-button-container { text-align: center; }
.cta-button-premium { display: inline-block; background: linear-gradient(135deg, #ff4081 0%, #ff6b6b 100%); color: white; padding: 20px 40px; border-radius: 10px; text-decoration: none; font-size: 1.2rem; transition: transform 0.3s, box-shadow 0.3s; }
.cta-button-premium:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(255, 64, 129, 0.4); }
.cta-main-text { display: block; font-weight: bold; font-size: 1.3rem; }
.cta-sub-text { display: block; font-size: 0.9rem; opacity: 0.9; margin-top: 5px; }
.cta-security { text-align: center; margin-top: 20px; font-size: 0.9rem; opacity: 0.8; }

/* Pre-landing specific */
.preland-hero { text-align: center; padding: 60px 0; background: linear-gradient(135deg, #1a3a8f 0%, #2c3e50 100%); color: white; border-radius: 12px; margin-bottom: 40px; }
.preland-hero h1 { font-size: 2.5rem; margin-bottom: 15px; }
.preland-hero .subtitle { font-size: 1.2rem; opacity: 0.9; }
.problem-section, .solution-section { margin: 40px 0; }
.benefits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
.benefit { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.testimonials { background: #f8f9fa; padding: 40px; border-radius: 12px; margin: 40px 0; }
.testimonial { background: white; padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.05); }
.author { text-align: right; font-style: italic; margin-top: 10px; }
.offer-section { background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); color: white; padding: 40px; border-radius: 12px; margin: 40px 0; }
.offer-details { text-align: center; margin: 30px 0; }
.original-price { text-decoration: line-through; opacity: 0.7; }
.current-price { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
.savings { background: rgba(255,255,255,0.2); display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: bold; }

/* Footer */
.site-footer { background: #2c3e50; color: white; padding: 3rem 0; margin-top: 4rem; }
.footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 40px; }
.footer-section h3, .footer-section h4 { margin-bottom: 15px; color: white; }
.footer-section a { color: #bdc3c7; text-decoration: none; display: block; margin: 8px 0; transition: color 0.3s; }
.footer-section a:hover { color: white; }
.copyright { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #34495e; color: #7f8c8d; }

/* Responsive */
@media (max-width: 768px) { 
    .site-header .container { flex-direction: column; text-align: center; }
    .main-nav { margin-top: 15px; flex-wrap: wrap; justify-content: center; }
    .main-nav a { margin: 5px; }
    .content, .widget { padding: 20px; }
    .preland-hero h1 { font-size: 2rem; }
    .cta-premium, .offer-section { padding: 25px; }
}'''
            
            try:
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(css)
                print("✅ CSS criado com estilos avançados")
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
            tipo = input("Tipo (review/comparativo/guia/preland/analise): ").strip() or "review"
            idioma = input("Idioma (pt-BR/en-US/es-ES/fr-FR/de-DE): ").strip() or "pt-BR"
            site = input("Site oficial (opcional): ").strip() or "https://exemplo.com"
            link = input("Link afiliado (opcional): ").strip() or "https://afiliado.com"
            
            if tipo == 'preland' and self.config['funnel']['enable_preland']:
                # Gerar funnel completo
                produto_data = {
                    'produto': produto,
                    'categoria': categoria,
                    'idioma': idioma,
                    'site_oficial': site,
                    'links_afiliados': link,
                    'tipo_artigo': 'preland'
                }
                
                print(f"\n📝 Confirmar criação de FUNNEL?")
                print(f"   Produto: {produto}")
                print(f"   Idioma: {idioma}")
                print(f"   Funnel: Review + Pre-landing page")
                
                if input("Continuar? (s/n): ").strip().lower() == 's':
                    self.gerar_funnel_completo(produto_data)
                    print("✅ Funnel criado com sucesso!")
                return
            
            slug = self.criar_slug(produto)
            titulo = self.criar_titulo_seo(produto, tipo, idioma)
            
            print(f"\n📝 Confirmar criação?")
            print(f"   Produto: {produto}")
            print(f"   Idioma: {idioma}")
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
    
    def gerar_funnel_manual(self):
        """Gera funnel manual para produto específico"""
        print("\n🔄 GERAR FUNNEL MANUAL")
        print("-"*40)
        
        try:
            produto = input("Nome do produto: ").strip() or "Produto Teste"
            categoria = input("Categoria: ").strip() or "testes"
            idioma = input("Idioma (pt-BR/en-US): ").strip() or "pt-BR"
            site = input("Site oficial: ").strip() or "https://exemplo.com"
            link = input("Link afiliado: ").strip() or "https://afiliado.com"
            
            produto_data = {
                'produto': produto,
                'categoria': categoria,
                'idioma': idioma,
                'site_oficial': site,
                'links_afiliados': link,
                'tipo_artigo': 'preland'
            }
            
            print(f"\n📝 Confirmar criação de FUNNEL?")
            print(f"   Produto: {produto}")
            print(f"   Idioma: {idioma}")
            print(f"   Funnel: Review + Pre-landing page")
            print(f"   Categoria: {categoria}")
            
            if input("Continuar? (s/n): ").strip().lower() == 's':
                sucesso = self.gerar_funnel_completo(produto_data)
                if sucesso:
                    print("✅ Funnel criado com sucesso!")
                    print(f"🌐 Review: {self.site_url}/{categoria}/{self.criar_slug(produto)}/")
                    print(f"🌐 Pre-landing: {self.site_url}/{categoria}/{self.criar_slug(produto)}-guia-completo/")
                else:
                    print("❌ Erro ao criar funnel")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def menu_configuracoes(self):
        """Menu de configurações"""
        while True:
            print("\n⚙️  CONFIGURAÇÕES")
            print("="*40)
            
            print(f"1. 🌐 Site URL: {self.site_url}")
            print(f"2. 🏷️  Nome: {self.config['site']['name']}")
            print(f"3. 📝 Palavras: {self.config['content']['word_count']}")
            print(f"4. 🔄 Funnel: {'✅ Ativo' if self.config['funnel']['enable_preland'] else '❌ Inativo'}")
            print("5. ↩️  Voltar")
            
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
                        print("❌ Valor deve estar entre 500 e 5000")
                except:
                    print("❌ Valor inválido")
            
            elif opcao == "4":
                atual = self.config['funnel']['enable_preland']
                novo = not atual
                self.config['funnel']['enable_preland'] = novo
                self.salvar_config()
                print(f"✅ Funnel {'ativado' if novo else 'desativado'}")
            
            elif opcao == "5":
                break
    
    def editar_conteudo_padrao(self):
        """Mostra onde editar conteúdo padrão"""
        print("\n📝 EDITAR CONTEÚDO PADRÃO")
        print("="*40)
        print("Para editar conteúdo SEM IA, modifique:")
        print("1. Método: gerar_review_basico()")
        print("2. Método: gerar_comparativo_basico()")
        print("3. Método: gerar_guia_basico()")
        print("4. Método: gerar_preland_basica()")
        print("5. Método: gerar_analise_basica()")
        print("\n📁 Templates de prompt em: templates/")
        print("   - review.txt, comparativo.txt, guia.txt, preland.txt, analise.txt")
        print("\n💡 Dica: Use Open Router (já configurado) para conteúdo automático de alta qualidade!")
        print("   API Key já incluída no código.")
    
    def salvar_config(self):
        """Salva configurações"""
        try:
            with open(self.base_dir / "config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✅ Configurações salvas")
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
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Ofertas - Reviews Honestos e Análises Detalhadas</title>
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
        <div class="hero" style="text-align: center; padding: 60px 0;">
            <h1 style="font-size: 2.5rem; margin-bottom: 20px;">Bem-vindo ao Top Ofertas</h1>
            <p style="font-size: 1.2rem; color: #666; max-width: 800px; margin: 0 auto 30px;">
                Reviews honestos e análises detalhadas dos melhores produtos do mercado.
            </p>
            <p style="color: #777;">
                Use o Gerador Real v6.0 para criar artigos automaticamente com IA.
            </p>
        </div>
        
        <div class="cta-buttons" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 40px 0;">
            <a href="games/index.html" class="btn" style="background: linear-gradient(135deg, #3498db 0%, #1a73e8 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
                🎮 Games
            </a>
            <a href="smartphones/index.html" class="btn" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
                📱 Smartphones
            </a>
            <a href="eletrodomesticos/index.html" class="btn" style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
                🏠 Eletrodomésticos
            </a>
            <a href="computadores/index.html" class="btn" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
                💻 Computadores
            </a>
            <a href="healthcare/index.html" class="btn" style="background: linear-gradient(135deg, #1abc9c 0%, #16a085 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
                🏥 Healthcare
            </a>
        </div>
        
        <div style="background: #f8f9fa; padding: 40px; border-radius: 12px; margin: 40px 0;">
            <h2 style="text-align: center; margin-bottom: 20px;">✨ Recursos do Gerador Real v6.0</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🤖</div>
                    <h3>IA Integrada</h3>
                    <p>Cria conteúdo automaticamente com Open Router/DeepSeek</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🌐</div>
                    <h3>Multi-idioma</h3>
                    <p>Artigos em português, inglês, espanhol e mais</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🔄</div>
                    <h3>Funnel Completo</h3>
                    <p>Review + Pre-landing page automáticos</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">📈</div>
                    <h3>SEO Avançado</h3>
                    <p>Meta tags, sitemap, schema.org automáticos</p>
                </div>
            </div>
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
        input("\nPressione Enter para sair...")