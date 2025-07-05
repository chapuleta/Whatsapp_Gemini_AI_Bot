import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import csv
from datetime import datetime, timedelta
import json
import re

# Configuração para Vercel
try:
    from vercel_config import BOT_CONFIG, EXPENSE_CATEGORIES, ALERT_LIMITS
except ImportError:
    # Fallback se não houver arquivo de config
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

# Arquivo CSV para armazenar gastos (em ambiente serverless, usar variáveis de ambiente ou banco de dados)
EXPENSES_DATA = []  # Usar lista em memória para demo
INTENTIONS_DATA = []  # Usar lista em memória para demo

# Função para simular CSV em ambiente serverless
def init_data():
    # Em produção, carregar de um banco de dados ou storage
    pass

def save_expense(date, amount, item, location, companions, payment_method, category):
    # Em produção, salvar em banco de dados
    expense = {
        'data': date,
        'valor': amount,
        'nome': item,
        'local': location,
        'acompanhantes': companions,
        'forma_pagamento': payment_method,
        'categoria': category
    }
    EXPENSES_DATA.append(expense)

def save_intention(item, amount):
    # Em produção, salvar em banco de dados
    intention = {
        'item': item,
        'valor': amount,
        'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ativo': True
    }
    INTENTIONS_DATA.append(intention)

def get_expenses_summary():
    if not EXPENSES_DATA:
        return None
    
    expenses = []
    for row in EXPENSES_DATA:
        expense = row.copy()
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
        if category in category_spending:
            category_spending[category] += expense['valor']
        else:
            category_spending[category] = expense['valor']
    
    return {
        'this_week_total': sum(e['valor'] for e in this_week_expenses),
        'this_month_total': sum(e['valor'] for e in this_month_expenses),
        'category_spending': category_spending,
        'last_expenses': expenses[-5:] if len(expenses) >= 5 else expenses
    }

def check_spending_alerts():
    if not EXPENSES_DATA:
        return []
    
    expenses = []
    for row in EXPENSES_DATA:
        expense = row.copy()
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
        
        if this_week_total > last_week_total * 1.2:  # 20% a mais
            increase_pct = ((this_week_total/last_week_total-1)*100)
            alerts.append(f"⚠️ Você gastou R$ {this_week_total:.2f} esta semana, {increase_pct:.1f}% a mais que a semana passada!")
    
    # Verificar gastos excessivos em junk food
    junk_categories = ['lanche', 'pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
    this_week_junk = [e for e in this_week_expenses if e['categoria'] in junk_categories]
    
    if this_week_junk:
        junk_total = sum(e['valor'] for e in this_week_junk)
        if junk_total > 50:  # Mais de R$ 50 em junk food
            alerts.append(f"🍔 Você gastou R$ {junk_total:.2f} com lanches/junk food esta semana!")
    
    return alerts

init_data()

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

# Variável para controlar estado da conversa
user_state = {}

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
                        response += f"💰 Esta semana: R$ {summary['this_week_total']:.2f}\n"
                        response += f"📅 Este mês: R$ {summary['this_month_total']:.2f}\n\n"
                        response += "*Gastos por categoria:*\n"
                        for category, amount in summary['category_spending'].items():
                            response += f"- _{category}_: R$ {amount:.2f}\n"
                        send(response)
                    else:
                        send("📊 Ainda não há gastos registrados!")
                    return jsonify({"status": "ok"}), 200
                
                elif "alerta" in prompt:
                    alerts = check_spending_alerts()
                    if alerts:
                        response = "⚠️ *Alertas financeiros:*\n\n"
                        response += "\n".join(alerts)
                        send(response)
                    else:
                        send("✅ Tudo sob controle! Nenhum alerta no momento.")
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
                        user_state[user_phone] = {
                            'pending_expense': {
                                'amount': amount,
                                'item': item_found,
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                        
                        response = f"💰 Anotei o gasto de *R$ {amount:.2f}* com _{item_found}_!\n\n"
                        response += "Para completar o registro, me conta:\n"
                        response += "- 📍 Onde você estava?\n"
                        response += "- 👥 Com quem você estava?\n"
                        response += "- 💳 Como você pagou? (dinheiro, cartão, pix, etc.)"
                        send(response)
                        return jsonify({"status": "ok"}), 200
                
                # Verificar se é resposta para gasto pendente
                if user_phone in user_state and 'pending_expense' in user_state[user_phone]:
                    expense = user_state[user_phone]['pending_expense']
                    
                    # Tentar extrair informações da resposta
                    location = "não informado"
                    companions = "sozinho"
                    payment_method = "não informado"
                    
                    # Simples extração de informações
                    if any(word in prompt for word in ['casa', 'trabalho', 'rua', 'shopping', 'escola', 'faculdade']):
                        location = prompt
                    if any(word in prompt for word in ['com', 'junto', 'amigo', 'família', 'namorad']):
                        companions = prompt
                    if any(word in prompt for word in ['dinheiro', 'cartão', 'pix', 'débito', 'crédito']):
                        payment_method = prompt
                    
                    # Categorizar automaticamente
                    junk_foods = ['pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
                    category = 'lanche' if expense['item'] in junk_foods else 'alimentação'
                    
                    # Salvar no CSV
                    save_expense(
                        expense['date'],
                        expense['amount'],
                        expense['item'],
                        location,
                        companions,
                        payment_method,
                        category
                    )
                    
                    # Limpar estado
                    del user_state[user_phone]
                    
                    response = f"✅ *Gasto registrado com sucesso!*\n\n"
                    response += f"💰 Valor: R$ {expense['amount']:.2f}\n"
                    response += f"🍽️ Item: {expense['item']}\n"
                    response += f"📍 Local: {location}\n"
                    response += f"👥 Companhia: {companions}\n"
                    response += f"💳 Pagamento: {payment_method}\n"
                    response += f"📂 Categoria: _{category}_"
                    
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
                # Processar mídia (áudio/imagem)
                media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[data["type"]]["id"]}/'
                headers = {'Authorization': f'Bearer {wa_token}'}
                media_response = requests.get(media_url_endpoint, headers=headers)
                media_url = media_response.json()["url"]
                media_download_response = requests.get(media_url, headers=headers)
                
                if data["type"] == "audio":
                    # Processar áudio - simplificado para serverless
                    try:
                        # Usar API do Gemini para transcrição
                        file_bytes = media_download_response.content
                        file = genai.upload_file(path=None, file_data=file_bytes, mime_type="audio/mpeg", display_name="audio")
                        response = model.generate_content([
                            "Transcreva este áudio para texto em português:",
                            file
                        ])
                        answer = response.text
                        
                        # Processar como gasto se mencionar valores
                        money_pattern = r'(?:r\$|rs|reais?)\s*(\d+(?:,\d{2})?)'
                        money_match = re.search(money_pattern, answer.lower())
                        
                        if money_match:
                            convo.send_message(f"Transcrição do áudio: '{answer}' - O usuário mencionou um gasto. Pergunte os detalhes necessários para registrar.")
                        else:
                            convo.send_message(f"Transcrição do áudio: '{answer}' - Responda como assistente financeiro.")
                        
                        send(convo.last.text)
                        file.delete()
                        
                    except Exception as e:
                        send("❌ Erro ao processar áudio. Tente enviar uma mensagem de texto.")
                        
                elif data["type"] == "image":
                    # Processar imagem - simplificado para serverless
                    try:
                        file_bytes = media_download_response.content
                        file = genai.upload_file(path=None, file_data=file_bytes, mime_type="image/jpeg", display_name="image")
                        response = model.generate_content([
                            "Analise esta imagem e descreva o que vê, especialmente se há informações sobre gastos, compras ou finanças:",
                            file
                        ])
                        answer = response.text
                        
                        convo.send_message(f"Análise da imagem: '{answer}' - Responda como assistente financeiro.")
                        send(convo.last.text)
                        file.delete()
                        
                    except Exception as e:
                        send("❌ Erro ao processar imagem. Tente enviar uma mensagem de texto.")
                        
                elif data["type"] == "document":
                    send("📄 Documentos não são suportados no momento. Tente enviar uma imagem ou mensagem de texto!")
                    
                else:
                    send("❌ Formato não suportado. Use texto, áudio ou imagem.")
                    
                # Limpeza de arquivos (importante para serverless)
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
