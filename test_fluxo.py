#!/usr/bin/env python3
"""
Teste específico do fluxo de registro de gastos
"""
import sys
import os
import json
import tempfile
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simular variáveis de ambiente
os.environ['WA_TOKEN'] = 'test_token'
os.environ['GEN_API'] = 'test_api'
os.environ['PHONE_ID'] = 'test_phone_id'
os.environ['PHONE_NUMBER'] = 'test_phone'

# Limpar backup anterior
backup_file = os.path.join(tempfile.gettempdir(), 'expenses_backup.json')
if os.path.exists(backup_file):
    os.remove(backup_file)

# Simular as funções do Gemini para teste
class MockGenAI:
    def configure(self, api_key): pass
    def GenerativeModel(self, model_name, generation_config=None, safety_settings=None): return MockModel()
    def upload_file(self, path=None, file_data=None, mime_type=None): return MockFile()
    def list_files(self): return []

class MockModel:
    def start_chat(self, history=None): return MockConvo()
    def generate_content(self, prompt): return MockResponse()

class MockConvo:
    def __init__(self): self.last = MockResponse()
    def send_message(self, message): 
        print(f"[GEMINI] {message}")
        self.last = MockResponse()

class MockResponse:
    def __init__(self): self.text = "Resposta simulada do Gemini"

class MockFile:
    def delete(self): pass

# Substituir o módulo genai
import types
genai = types.ModuleType('genai')
genai.configure = MockGenAI().configure
genai.GenerativeModel = MockGenAI().GenerativeModel
genai.upload_file = MockGenAI().upload_file
genai.list_files = MockGenAI().list_files
sys.modules['google.generativeai'] = genai

# Substituir requests
class MockRequests:
    def post(self, url, headers=None, json=None):
        body = json.get('text', {}).get('body', 'mensagem')
        print(f"[BOT RESPOSTA] {body}")
        return MockResponse()
    def get(self, url, headers=None): return MockResponse()

requests = MockRequests()
sys.modules['requests'] = requests

# Substituir Flask
class MockRequest:
    def __init__(self, method, data=None):
        self.method = method
        self.data = data
        self.args = {"hub.mode": "test", "hub.verify_token": "test", "hub.challenge": "test"}
    
    def get_json(self): 
        return self.data
    
    def get(self, key, default=None): 
        return self.args.get(key, default)

class MockFlask:
    def __init__(self, name): self.name = name
    def route(self, path, methods=None):
        def decorator(func): return func
        return decorator
    def run(self, debug=False, port=None): pass

sys.modules['flask'] = types.ModuleType('flask')
sys.modules['flask'].Flask = MockFlask
sys.modules['flask'].request = MockRequest("POST")
sys.modules['flask'].jsonify = lambda x: x

# Agora importar o main
try:
    from main import webhook, EXPENSES_DATA, INTENTIONS_DATA, pending_expense
    
    print("🧪 TESTE DE FLUXO DE REGISTRO")
    print("=" * 50)
    
    # Simular dados do WhatsApp
    whatsapp_data = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "5511999999999",
                        "type": "text",
                        "text": {"body": "gastei R$ 8 com pastel"}
                    }]
                }
            }]
        }]
    }
    
    # Simular request do webhook
    flask_module = sys.modules['flask']
    flask_module.request = MockRequest("POST", whatsapp_data)
    
    print("\n1. Simulando mensagem: 'gastei R$ 8 com pastel'")
    print("   Estado antes:", f"pending_expense = {pending_expense}")
    print("   Gastos antes:", len(EXPENSES_DATA))
    
    # Executar webhook
    result = webhook()
    
    print(f"   Estado depois: pending_expense = {pending_expense}")
    print(f"   Gastos depois: {len(EXPENSES_DATA)}")
    
    # Simular segunda mensagem com detalhes
    whatsapp_data2 = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "5511999999999",
                        "type": "text",
                        "text": {"body": "na cantina, sozinho, dinheiro"}
                    }]
                }
            }]
        }]
    }
    
    flask_module.request = MockRequest("POST", whatsapp_data2)
    
    print("\n2. Simulando resposta: 'na cantina, sozinho, dinheiro'")
    print("   Estado antes:", f"pending_expense = {pending_expense}")
    print("   Gastos antes:", len(EXPENSES_DATA))
    
    # Executar webhook
    result2 = webhook()
    
    print(f"   Estado depois: pending_expense = {pending_expense}")
    print(f"   Gastos depois: {len(EXPENSES_DATA)}")
    
    # Verificar se o gasto foi salvo
    if EXPENSES_DATA:
        print("\n✅ GASTO REGISTRADO COM SUCESSO!")
        gasto = EXPENSES_DATA[-1]
        print(f"   Valor: R$ {gasto['valor']}")
        print(f"   Item: {gasto['nome']}")
        print(f"   Local: {gasto['local']}")
        print(f"   Categoria: {gasto['categoria']}")
    else:
        print("\n❌ GASTO NÃO FOI REGISTRADO")
    
    # Verificar backup
    if os.path.exists(backup_file):
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"\n💾 Backup: {len(data.get('expenses', []))} gastos salvos")
    
    # Testar comando resumo
    print("\n3. Testando comando 'resumo'")
    whatsapp_data3 = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "5511999999999",
                        "type": "text",
                        "text": {"body": "resumo"}
                    }]
                }
            }]
        }]
    }
    
    flask_module.request = MockRequest("POST", whatsapp_data3)
    result3 = webhook()
    
    print("=" * 50)
    print("🎯 TESTE CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()
