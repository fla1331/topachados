
import requests
import json

print("=== Testando Open Router ===")

# SUA CHAVE DO OPEN ROUTER - COLE AQUI
OPENROUTER_API_KEY = "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"

# Lista de modelos para testar (começando pelo modelo pago comum)
modelos_para_testar = [
    "deepseek/deepseek-chat",  # Modelo principal pago
    "mistralai/mixtral-8x7b-instruct",  # Outro modelo conhecido e gratuito
    "google/gemini-2.0-flash",  # Modelo da Google
]

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Gerador Real Test"
}

for modelo in modelos_para_testar:
    print(f"\n--- Tentando modelo: {modelo} ---")
    data = {
        "model": modelo,
        "messages": [{"role": "user", "content": "Responda apenas 'OK' em português."}],
        "max_tokens": 10
    }
    
    try:
        resposta = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status: {resposta.status_code}")
        if resposta.status_code == 200:
            print(f"✅ SUCESSO! Resposta: {resposta.json()['choices'][0]['message']['content']}")
            break  # Para no primeiro que funcionar
        else:
            print(f"Resposta: {resposta.text[:200]}")
    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
    