#!/usr/bin/env python3
"""
Teste local do sistema de assistente financeiro
"""
import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simular variáveis de ambiente
os.environ['WA_TOKEN'] = 'test_token'
os.environ['GEN_API'] = 'test_api'
os.environ['PHONE_ID'] = 'test_phone_id'
os.environ['PHONE_NUMBER'] = 'test_phone'

# Simular as funções do Gemini para teste
class MockGenAI:
    def configure(self, api_key):
        pass
    
    def GenerativeModel(self, model_name, generation_config=None, safety_settings=None):
        return MockModel()
    
    def upload_file(self, path=None, file_data=None, mime_type=None):
        return MockFile()
    
    def list_files(self):
        return []

class MockModel:
    def start_chat(self, history=None):
        return MockConvo()
    
    def generate_content(self, prompt):
        return MockResponse()

class MockConvo:
    def __init__(self):
        self.last = MockResponse()
    
    def send_message(self, message):
        print(f"[GEMINI] {message}")
        self.last = MockResponse()

class MockResponse:
    def __init__(self):
        self.text = "Resposta simulada do Gemini"

class MockFile:
    def delete(self):
        pass

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
        print(f"[WHATSAPP] Enviando: {json.get('text', {}).get('body', 'mensagem')}")
        return MockResponse()
    
    def get(self, url, headers=None):
        return MockResponse()

requests = MockRequests()
sys.modules['requests'] = requests

# Substituir Flask
class MockFlask:
    def __init__(self, name):
        self.name = name
    
    def route(self, path, methods=None):
        def decorator(func):
            return func
        return decorator
    
    def run(self, debug=False, port=None):
        pass

sys.modules['flask'] = types.ModuleType('flask')
sys.modules['flask'].Flask = MockFlask
sys.modules['flask'].request = types.ModuleType('request')
sys.modules['flask'].jsonify = lambda x: x

# Agora importar o main
try:
    from main import save_expense, get_expenses_summary, check_spending_alerts, EXPENSES_DATA, INTENTIONS_DATA
    
    print("🧪 TESTE LOCAL DO ASSISTENTE FINANCEIRO")
    print("=" * 50)
    
    # Teste 1: Salvar gastos
    print("\n1. Testando salvamento de gastos...")
    save_expense(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        8.50,
        'pastel',
        'cantina',
        'sozinho',
        'dinheiro',
        'lanche'
    )
    save_expense(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        15.00,
        'hamburguer',
        'lanchonete',
        'com amigo',
        'cartão',
        'lanche'
    )
    
    print(f"✅ Gastos salvos: {len(EXPENSES_DATA)}")
    
    # Teste 2: Resumo
    print("\n2. Testando resumo...")
    summary = get_expenses_summary()
    if summary:
        print(f"✅ Resumo gerado:")
        print(f"   - Total de gastos: {summary['total_expenses']}")
        print(f"   - Total semanal: R$ {summary['this_week_total']:.2f}")
        print(f"   - Total mensal: R$ {summary['this_month_total']:.2f}")
        print(f"   - Gastos por categoria: {summary['category_spending']}")
    else:
        print("❌ Erro ao gerar resumo")
    
    # Teste 3: Alertas
    print("\n3. Testando alertas...")
    alerts = check_spending_alerts()
    if alerts:
        print(f"✅ Alertas encontrados: {len(alerts)}")
        for alert in alerts:
            print(f"   - {alert}")
    else:
        print("✅ Nenhum alerta (normal para poucos gastos)")
    
    # Teste 4: Backup
    print("\n4. Testando backup...")
    try:
        import json
        import tempfile
        backup_file = os.path.join(tempfile.gettempdir(), 'expenses_backup.json')
        if os.path.exists(backup_file):
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Backup encontrado: {len(data.get('expenses', []))} gastos")
                print(f"   Arquivo: {backup_file}")
        else:
            print("⚠️ Nenhum backup encontrado")
    except Exception as e:
        print(f"❌ Erro ao verificar backup: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TESTE CONCLUÍDO!")
    print("\nPara usar o bot:")
    print("1. Configure as variáveis de ambiente no Vercel")
    print("2. Faça o deploy: vercel --prod")
    print("3. Configure o webhook do WhatsApp")
    print("4. Teste enviando: 'gastei R$ 8 com pastel'")
    print("5. Use comandos: 'resumo', 'alerta', 'teste gasto'")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()
