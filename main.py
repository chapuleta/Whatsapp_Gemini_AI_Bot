import google.generativeai as genai
from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta
import re
import json

# Configuração simples para reduzir tamanho
BOT_CONFIG = {'timeout': 25}
EXPENSE_CATEGORIES = {
    'lanche': ['pastel', 'coxinha', 'hamburguer', 'salgado', 'lanche'],
    'bebida': ['refrigerante', 'suco', 'água', 'café'],
    'alimentação': ['comida', 'almoço', 'jantar', 'refeição'],
    'outros': []
}
ALERT_LIMITS = {'weekly_increase': 0.2, 'junk_food_limit': 50}
#forcar vercel a mudar
wa_token=os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id=os.environ.get("PHONE_ID")
phone=os.environ.get("PHONE_NUMBER")
name="João Victor" #The bot will consider this person as its owner or creator
bot_name="Assistente Financeiro" #This will be the name of your bot, eg: "Hello I am Astro Bot"
model_name="gemini-2.5-flash-preview-05-20" #Switch to "gemini-1.0-pro" or any free model, if "gemini-1.5-flash" becomes paid in future.

# Sistema de persistência simplificado - usar variável global com backup em arquivo
# Para um usuário único, vamos manter os dados na memória e fazer backup
EXPENSES_DATA = []
INTENTIONS_DATA = []

# Usar um caminho que funciona tanto no Windows quanto no Vercel
import tempfile
BACKUP_FILE = os.path.join(tempfile.gettempdir(), 'expenses_backup.json')

def load_data_from_backup():
    """Carrega dados do backup se existir"""
    global EXPENSES_DATA, INTENTIONS_DATA
    try:
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                EXPENSES_DATA = data.get('expenses', [])
                INTENTIONS_DATA = data.get('intentions', [])
                print(f"DEBUG: Dados carregados do backup - {len(EXPENSES_DATA)} gastos, {len(INTENTIONS_DATA)} intenções")
        else:
            print("DEBUG: Nenhum backup encontrado, iniciando com dados vazios")
    except Exception as e:
        print(f"DEBUG: Erro ao carregar backup: {e}")
        EXPENSES_DATA = []
        INTENTIONS_DATA = []

def save_data_to_backup():
    """Salva dados no backup"""
    global EXPENSES_DATA, INTENTIONS_DATA
    try:
        data = {
            'expenses': EXPENSES_DATA,
            'intentions': INTENTIONS_DATA
        }
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"DEBUG: Backup salvo - {len(EXPENSES_DATA)} gastos, {len(INTENTIONS_DATA)} intenções")
    except Exception as e:
        print(f"DEBUG: Erro ao salvar backup: {e}")

# Carrega dados na inicialização
load_data_from_backup()

def save_expense(date, amount, item, location, companions, payment_method, category):
    """Salva gasto na lista global e faz backup"""
    global EXPENSES_DATA
    
    expense = {
        'data': date,
        'valor': float(amount),
        'nome': item,
        'local': location,
        'acompanhantes': companions,
        'forma_pagamento': payment_method,
        'categoria': category
    }
    EXPENSES_DATA.append(expense)
    
    # Fazer backup
    save_data_to_backup()
    
    print(f"DEBUG: Gasto salvo. Total: {len(EXPENSES_DATA)}")
    return True

def save_intention(item, amount):
    """Salva intenção na lista global e faz backup"""
    global INTENTIONS_DATA
    
    intention = {
        'item': item,
        'valor': float(amount),
        'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ativo': True
    }
    INTENTIONS_DATA.append(intention)
    
    # Fazer backup
    save_data_to_backup()
    
    return True

def get_expenses_summary():
    """Retorna resumo dos gastos"""
    global EXPENSES_DATA
    
    if not EXPENSES_DATA:
        return None
    
    expenses = []
    for expense_data in EXPENSES_DATA:
        expense = expense_data.copy()
        expense['data'] = datetime.strptime(expense['data'], '%Y-%m-%d %H:%M:%S')
        expense['valor'] = float(expense['valor'])
        expenses.append(expense)
    
    # Filtrar gastos desta semana
    week_ago = datetime.now() - timedelta(days=7)
    this_week_expenses = [e for e in expenses if e['data'] >= week_ago]
    
    # Filtrar gastos deste mês
    current_month = datetime.now().month
    this_month_expenses = [e for e in expenses if e['data'].month == current_month]
    
    # Gastos por categoria
    category_spending = {}
    for expense in expenses:
        category = expense['categoria']
        category_spending[category] = category_spending.get(category, 0) + expense['valor']
    
    return {
        'this_week_total': sum(e['valor'] for e in this_week_expenses),
        'this_month_total': sum(e['valor'] for e in this_month_expenses),
        'category_spending': category_spending,
        'last_expenses': expenses[-5:] if len(expenses) >= 5 else expenses,
        'total_expenses': len(expenses)
    }

def check_spending_alerts():
    """Verifica alertas de gastos"""
    global EXPENSES_DATA
    
    if not EXPENSES_DATA:
        return []
    
    expenses = []
    for expense_data in EXPENSES_DATA:
        expense = expense_data.copy()
        expense['data'] = datetime.strptime(expense['data'], '%Y-%m-%d %H:%M:%S')
        expense['valor'] = float(expense['valor'])
        expenses.append(expense)
    
    alerts = []
    
    # Comparar gastos desta semana com semana passada
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    
    this_week_expenses = [e for e in expenses if e['data'] >= week_ago]
    last_week_expenses = [e for e in expenses if two_weeks_ago <= e['data'] < week_ago]
    
    if this_week_expenses and last_week_expenses:
        this_week_total = sum(e['valor'] for e in this_week_expenses)
        last_week_total = sum(e['valor'] for e in last_week_expenses)
        
        if this_week_total > last_week_total * 1.2:
            increase_pct = ((this_week_total/last_week_total-1)*100)
            alerts.append(f"⚠️ Você gastou R$ {this_week_total:.2f} esta semana, {increase_pct:.1f}% a mais que a semana passada!")
    
    # Verificar gastos excessivos em junk food
    junk_categories = ['lanche', 'pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
    this_week_junk = [e for e in this_week_expenses if e['categoria'] in junk_categories]
    
    if this_week_junk:
        junk_total = sum(e['valor'] for e in this_week_junk)
        if junk_total > 50:
            alerts.append(f"🍔 Você gastou R$ {junk_total:.2f} com lanches/junk food esta semana!")
    
    return alerts

app=Flask(__name__)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_MEDIUM_AND_ABOVE"},  
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name=model_name,
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])

convo.send_message(f'''
Você é "{bot_name}", um assistente financeiro inteligente do {name}. Você opera exclusivamente no WhatsApp e sua missão é ajudar {name} a ter mais consciência e controle dos seus gastos.

**IMPORTANTES INSTRUÇÕES:**
- {name} frequentemente enviará mensagens de áudio que serão transcritas para você
- Você deve sempre responder em português brasileiro, de forma amigável mas direta
- Sua função principal é registrar gastos e dar insights financeiros

**SUAS PRINCIPAIS FUNÇÕES:**

1. **REGISTRAR GASTOS:** Quando {name} disser que gastou dinheiro, você deve:
   - Perguntar detalhes faltantes: onde foi, com quem estava, forma de pagamento
   - Salvar no sistema com data, valor, item, local, acompanhantes, forma de pagamento e categoria
   - Confirmar o registro

2. **CATEGORIZAR AUTOMATICAMENTE:** Classifique gastos em categorias como:
   - lanche, pastel, hamburguer, refrigerante, coxinha, salgado (junk food)
   - transporte, alimentação, lazer, compras, saúde, etc.

3. **DAR ALERTAS E INSIGHTS:**
   - Compare gastos semanais/mensais
   - Alerte sobre gastos excessivos com junk food
   - Mostre padrões de consumo

4. **GERENCIAR INTENÇÕES DE COMPRA:**
   - Registre itens que {name} quer comprar
   - Compare gastos pequenos com objetivos maiores
   - Lembre sobre prioridades financeiras

**COMO RESPONDER A GASTOS:**
Quando {name} disser algo como "gastei R$ 8 com um pastel", você deve responder assim:
"Anotei o gasto de R$ 8,00 com pastel! Para completar o registro, me conta:
- Onde você estava?
- Com quem você estava?
- Como você pagou? (dinheiro, cartão, pix, etc.)"

**FORMATAÇÃO WHATSAPP:**
- Use *negrito* para valores importantes
- Use _itálico_ para categorias
- Use listas com - para organizar informações
- Emojis para tornar mais amigável: 💰 📊 ⚠️ 🎯

**COMANDOS ESPECIAIS:**
- "resumo" ou "relatório" = mostrar gastos recentes
- "meta" ou "objetivo" = gerenciar intenções de compra
- "alerta" = verificar alertas de gastos

Responda apenas quando {name} enviar uma mensagem. Não responda a esta configuração inicial.
''')

# Variável para controlar estado da conversa - usuário único
pending_expense = None

def send(answer):
    url=f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers={
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data={
          "messaging_product": "whatsapp", 
          "to": f"{phone}", 
          "type": "text",
          "text":{"body": f"{answer}"},
          }
    
    response=requests.post(url, headers=headers,json=data)
    return response

def remove(*file_paths):
    for file in file_paths:
        if os.path.exists(file):
            os.remove(file)
        else:pass

@app.route("/",methods=["GET","POST"])
def index():
    return "Bot"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    global pending_expense
    
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == "BOT":
            return challenge, 200
        else:
            return "Failed", 403
    elif request.method == "POST":
        try:
            data = request.get_json()["entry"][0]["changes"][0]["value"]["messages"][0]
            user_phone = data["from"]
            
            if data["type"] == "text":
                prompt = data["text"]["body"].lower()
                
                # Processar comandos especiais
                if "resumo" in prompt or "relatório" in prompt:
                    summary = get_expenses_summary()
                    if summary:
                        response = f"📊 *Resumo dos seus gastos:*\n\n"
                        response += f"� Total de gastos registrados: {summary['total_expenses']}\n"
                        response += f"�💰 Esta semana: R$ {summary['this_week_total']:.2f}\n"
                        response += f"📅 Este mês: R$ {summary['this_month_total']:.2f}\n\n"
                        
                        if summary['category_spending']:
                            response += "*Gastos por categoria:*\n"
                            for category, amount in summary['category_spending'].items():
                                response += f"- _{category}_: R$ {amount:.2f}\n"
                        
                        if summary['last_expenses']:
                            response += f"\n*Últimos gastos:*\n"
                            for expense in summary['last_expenses'][-3:]:  # Últimos 3
                                response += f"- R$ {expense['valor']:.2f} em {expense['nome']} ({expense['categoria']})\n"
                        
                        send(response)
                    else:
                        # Debug: verificar se há dados
                        debug_msg = f"📊 Ainda não há gastos registrados!\n\n"
                        debug_msg += f"🔍 Debug: {len(EXPENSES_DATA)} gastos encontrados no sistema."
                        send(debug_msg)
                    return jsonify({"status": "ok"}), 200
                
                elif "debug" in prompt or "teste" in prompt:
                    # Comando de debug para verificar o sistema
                    response = f"🔍 *Debug do Sistema:*\n\n"
                    response += f"📊 Gastos armazenados: {len(EXPENSES_DATA)}\n"
                    response += f"🎯 Intenções armazenadas: {len(INTENTIONS_DATA)}\n"
                    response += f"💾 Gasto pendente: {'Sim' if pending_expense else 'Não'}\n"
                    
                    if EXPENSES_DATA:
                        response += f"\n*Últimos gastos:*\n"
                        for i, expense in enumerate(EXPENSES_DATA[-3:], 1):
                            response += f"{i}. R$ {expense['valor']} - {expense['nome']} ({expense['data']})\n"
                    
                    send(response)
                    return jsonify({"status": "ok"}), 200
                
                elif "alerta" in prompt or "alertas" in prompt:
                    alerts = check_spending_alerts()
                    if alerts:
                        response = "⚠️ *Seus alertas financeiros:*\n\n"
                        response += "\n".join(alerts)
                    else:
                        response = "✅ *Nenhum alerta no momento!*\n\nSeus gastos estão sob controle."
                    
                    send(response)
                    return jsonify({"status": "ok"}), 200
                
                elif "teste" in prompt and "gasto" in prompt:
                    # Comando para adicionar gastos de teste
                    test_expenses = [
                        {'amount': 8.50, 'item': 'pastel', 'location': 'cantina', 'category': 'lanche'},
                        {'amount': 15.00, 'item': 'hamburguer', 'location': 'lanchonete', 'category': 'lanche'},
                        {'amount': 25.00, 'item': 'almoço', 'location': 'restaurante', 'category': 'alimentação'},
                        {'amount': 4.50, 'item': 'refrigerante', 'location': 'mercado', 'category': 'bebida'},
                        {'amount': 12.00, 'item': 'coxinha', 'location': 'padaria', 'category': 'lanche'}
                    ]
                    
                    for expense in test_expenses:
                        save_expense(
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            expense['amount'],
                            expense['item'],
                            expense['location'],
                            'sozinho',
                            'dinheiro',
                            expense['category']
                        )
                    
                    response = f"🧪 *Gastos de teste adicionados!*\n\n"
                    response += f"📊 Total de gastos: {len(EXPENSES_DATA)}\n"
                    response += f"💰 Valor total: R$ {sum(e['valor'] for e in EXPENSES_DATA):.2f}\n\n"
                    response += "Use *resumo* para ver os detalhes!"
                    
                    send(response)
                    return jsonify({"status": "ok"}), 200
                
                elif "meta" in prompt or "objetivo" in prompt:
                    convo.send_message(f"O usuário quer gerenciar intenções de compra. Pergunte qual item ele quer comprar e o valor estimado para registrar como objetivo financeiro.")
                    send(convo.last.text)
                    return jsonify({"status": "ok"}), 200
                
                # Processar mensagem normal
                # Verificar se é um gasto (contém valor monetário)
                money_pattern = r'(?:r\$|rs|reais?)\s*(\d+(?:,\d{2})?)'
                money_match = re.search(money_pattern, prompt)
                
                if money_match:
                    amount = float(money_match.group(1).replace(',', '.'))
                    
                    # Extrair item do contexto
                    item_keywords = ['pastel', 'hamburguer', 'refrigerante', 'coxinha', 'lanche', 'comida', 'café', 'água']
                    item_found = None
                    for keyword in item_keywords:
                        if keyword in prompt:
                            item_found = keyword
                            break
                    
                    if item_found:
                        pending_expense = {
                            'amount': amount,
                            'item': item_found,
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        response = f"💰 Anotei o gasto de *R$ {amount:.2f}* com _{item_found}_!\n\n"
                        response += "Para completar o registro, me conta:\n"
                        response += "- 📍 Onde você estava?\n"
                        response += "- 👥 Com quem você estava?\n"
                        response += "- 💳 Como você pagou? (dinheiro, cartão, pix, etc.)"
                        send(response)
                        return jsonify({"status": "ok"}), 200
                    else:
                        # Item não encontrado, enviar para o Gemini processar
                        pass
                
                # Verificar se é resposta para gasto pendente
                if pending_expense:
                    expense = pending_expense
                    
                    # Tentar extrair informações da resposta
                    location = "não informado"
                    companions = "sozinho"
                    payment_method = "não informado"
                    
                    # Simples extração de informações
                    if any(word in prompt for word in ['casa', 'trabalho', 'rua', 'shopping', 'escola', 'faculdade', 'cantina', 'lanchonete', 'restaurante']):
                        location = prompt
                    if any(word in prompt for word in ['com', 'junto', 'amigo', 'família', 'namorad']):
                        companions = prompt
                    if any(word in prompt for word in ['dinheiro', 'cartão', 'pix', 'débito', 'crédito']):
                        payment_method = prompt
                    
                    # Categorizar automaticamente
                    junk_foods = ['pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
                    category = 'lanche' if expense['item'] in junk_foods else 'alimentação'
                    
                    # Salvar no sistema
                    save_success = save_expense(
                        expense['date'],
                        expense['amount'],
                        expense['item'],
                        location,
                        companions,
                        payment_method,
                        category
                    )
                    
                    # Limpar estado
                    pending_expense = None
                    
                    # Verificar se foi salvo
                    total_expenses = len(EXPENSES_DATA)
                    
                    if save_success:
                        response = f"✅ *Gasto registrado com sucesso!*\n\n"
                    else:
                        response = f"⚠️ *Gasto registrado (temporário):*\n\n"
                    
                    response += f"💰 Valor: R$ {expense['amount']:.2f}\n"
                    response += f"🍽️ Item: {expense['item']}\n"
                    response += f"📍 Local: {location}\n"
                    response += f"👥 Companhia: {companions}\n"
                    response += f"💳 Pagamento: {payment_method}\n"
                    response += f"📂 Categoria: _{category}_\n"
                    response += f"📈 Total de gastos: {total_expenses}"
                    
                    # Verificar alertas
                    alerts = check_spending_alerts()
                    if alerts:
                        response += f"\n\n⚠️ *Alertas:*\n"
                        response += "\n".join(alerts[:2])  # Máximo 2 alertas
                    
                    send(response)
                    return jsonify({"status": "ok"}), 200
                
                # Mensagem normal para o bot
                convo.send_message(prompt)
                send(convo.last.text)
            else:
                # Processar mídia de forma simplificada
                try:
                    media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[data["type"]]["id"]}/'
                    headers = {'Authorization': f'Bearer {wa_token}'}
                    media_response = requests.get(media_url_endpoint, headers=headers)
                    media_url = media_response.json()["url"]
                    media_download_response = requests.get(media_url, headers=headers)
                    
                    file_bytes = media_download_response.content
                    
                    if data["type"] == "audio":
                        # Processar áudio
                        file = genai.upload_file(path=None, file_data=file_bytes, mime_type="audio/mpeg")
                        response = model.generate_content(["Transcreva este áudio para português:", file])
                        answer = response.text
                        
                        # Verificar se menciona gastos
                        if re.search(r'(?:gastei|comprei|paguei|r\$|reais?)', answer.lower()):
                            convo.send_message(f"Áudio transcrito: '{answer}' - Usuário mencionou gasto, peça detalhes.")
                        else:
                            convo.send_message(f"Áudio transcrito: '{answer}' - Responda como assistente financeiro.")
                        
                        send(convo.last.text)
                        file.delete()
                        
                    elif data["type"] == "image":
                        # Processar imagem
                        file = genai.upload_file(path=None, file_data=file_bytes, mime_type="image/jpeg")
                        response = model.generate_content(["Descreva esta imagem, focando em informações financeiras:", file])
                        answer = response.text
                        
                        convo.send_message(f"Imagem analisada: '{answer}' - Responda como assistente financeiro.")
                        send(convo.last.text)
                        file.delete()
                        
                    else:
                        send("❌ Formato não suportado. Use texto, áudio ou imagem.")
                        
                except Exception as e:
                    send("❌ Erro ao processar mídia. Tente uma mensagem de texto.")
                    
                # Limpeza
                try:
                    files = genai.list_files()
                    for file in files:
                        file.delete()
                except:
                    pass
        except :pass
        return jsonify({"status": "ok"}), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
