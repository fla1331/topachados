#!/usr/bin/env python3
"""
RUN ALL - Executa todo o fluxo de geração de conteúdo
"""

import subprocess
import time
import sys

def run_script(script_name, description):
    print(f"\n{'='*60}")
    print(f"🚀 EXECUTANDO: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True,
                              encoding='utf-8')
        
        print(result.stdout)
        
        if result.stderr:
            print(f"⚠️  Erros em {script_name}:")
            print(result.stderr[:500])
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar {script_name}: {e}")
        return False

def main():
    print("🎯 SISTEMA COMPLETO DE GERAÇÃO DE CONTEÚDO")
    print("="*60)
    
    scripts = [
        ("gerador.py", "1. Gerador Principal - Cria reviews básicos"),
        ("finalizador_html.py", "2. Finalizador - Refina conteúdo com IA"),
        ("gerador_satelites.py", "3. Gerador de Satélites - Cria artigos complementares")
    ]
    
    for script, description in scripts:
        success = run_script(script, description)
        
        if not success:
            print(f"\n❌ Interrompido devido a erro em {script}")
            print("💡 Verifique os logs acima e corrija o problema.")
            break
        
        print(f"\n⏳ Aguardando 5 segundos antes do próximo...")
        time.sleep(5)
    
    print("\n" + "="*60)
    print("🎉 FLUXO COMPLET