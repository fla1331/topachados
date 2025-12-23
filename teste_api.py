import requests
import json

# TESTE 1: DeepSeek (use SUA chave real se tiver)
print("=== Testando DeepSeek ===")
url_deepseek = "https://api.deepseek.com/v1/chat/completions"
headers_deepseek = {
    "Authorization": "Bearer sk-db954932604245b3a9e9921189118642",  # Substitua pela sua chave!
    "Content-Type": "application/json"
}
data_deepseek = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Diga olá em português."}]
}

try:
    resposta = requests.post(url_deepseek, headers=headers_deepseek, json=data_deepseek, timeout=10)
    print(f"Status Code: {resposta.status_code}")
    print(f"Resposta: {resposta.text[:200]}...")
except Exception as e:
    print(f"ERRO na conexão: {type(e).__name__}: {e}")

print("\n" + "="*40 + "\n")

# TESTE 2: Gemini (use SUA chave real)
print("=== Testando Gemini ===")
sua_chave_gemini = "AIzaSyCcpvY9GU_0eBed02cVHq5nZ2sUS1Bly70"  # Use a chave que você configurou
url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AIzaSyCcpvY9GU_0eBed02cVHq5nZ2sUS1Bly70}"
headers_gemini = {"Content-Type": "application/json"}
data_gemini = {
    "contents": [{"parts": [{"text": "Diga olá em português."}]}]
}

try:
    resposta = requests.post(url_gemini, headers=headers_gemini, json=data_gemini, timeout=10)
    print(f"Status Code: {resposta.status_code}")
    print(f"Resposta: {resposta.text[:200]}...")
except Exception as e:
    print(f"ERRO na conexão: {type(e).__name__}: {e}")