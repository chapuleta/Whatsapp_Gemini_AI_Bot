import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import fitz
import csv
import pandas as pd
from datetime import datetime, timedelta
import json
#forcar vercel a mudar
wa_token=os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id=os.environ.get("PHONE_ID")
phone=os.environ.get("PHONE_NUMBER")
name="João Victor" #The bot will consider this person as its owner or creator
bot_name="Assistente Financeiro" #This will be the name of your bot, eg: "Hello I am Astro Bot"
model_name="gemini-2.5-flash-preview-05-20" #Switch to "gemini-1.0-pro" or any free model, if "gemini-1.5-flash" becomes paid in future.

# Arquivo CSV para armazenar gastos
EXPENSES_CSV = "expenses.csv"
INTENTIONS_CSV = "intentions.csv"

# Inicializar arquivos CSV se não existirem
def init_csv_files():
    if not os.path.exists(EXPENSES_CSV):
        with open(EXPENSES_CSV, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['data', 'valor', 'nome', 'local', 'acompanhantes', 'forma_pagamento', 'categoria'])
    
    if not os.path.exists(INTENTIONS_CSV):
        with open(INTENTIONS_CSV, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['item', 'valor', 'data_criacao', 'ativo'])

def save_expense(date, amount, item, location, companions, payment_method, category):
    with open(EXPENSES_CSV, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([date, amount, item, location, companions, payment_method, category])

def save_intention(item, amount):
    with open(INTENTIONS_CSV, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([item, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), True])

def get_expenses_summary():
    if not os.path.exists(EXPENSES_CSV):
        return None
    
    df = pd.read_csv(EXPENSES_CSV)
    if df.empty:
        return None
    
    df['data'] = pd.to_datetime(df['data'])
    
    # Gastos desta semana
    this_week = df[df['data'] >= datetime.now() - timedelta(days=7)]
    
    # Gastos do mês atual
    this_month = df[df['data'].dt.month == datetime.now().month]
    
    # Gastos por categoria
    category_spending = df.groupby('categoria')['valor'].sum().to_dict()
    
    return {
        'this_week_total': this_week['valor'].sum(),
        'this_month_total': this_month['valor'].sum(),
        'category_spending': category_spending,
        'last_expenses': df.tail(5).to_dict('records')
    }

def check_spending_alerts():
    if not os.path.exists(EXPENSES_CSV):
        return []
    
    df = pd.read_csv(EXPENSES_CSV)
    if df.empty:
        return []
    
    df['data'] = pd.to_datetime(df['data'])
    
    alerts = []
    
    # Comparar gastos desta semana com semana passada
    this_week = df[df['data'] >= datetime.now() - timedelta(days=7)]
    last_week = df[(df['data'] >= datetime.now() - timedelta(days=14)) & 
                   (df['data'] < datetime.now() - timedelta(days=7))]
    
    if not this_week.empty and not last_week.empty:
        this_week_total = this_week['valor'].sum()
        last_week_total = last_week['valor'].sum()
        
        if this_week_total > last_week_total * 1.2:  # 20% a mais
            alerts.append(f"⚠️ Você gastou R$ {this_week_total:.2f} esta semana, {((this_week_total/last_week_total-1)*100):.1f}% a mais que a semana passada!")
    
    # Verificar gastos excessivos em junk food
    junk_categories = ['lanche', 'pastel', 'hamburguer', 'refrigerante', 'coxinha', 'salgado']
    this_week_junk = this_week[this_week['categoria'].isin(junk_categories)]
    
    if not this_week_junk.empty:
        junk_total = this_week_junk['valor'].sum()
        if junk_total > 50:  # Mais de R$ 50 em junk food
            alerts.append(f"🍔 Você gastou R$ {junk_total:.2f} com lanches/junk food esta semana!")
    
    return alerts

init_csv_files()

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
                import re
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
                media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[data["type"]]["id"]}/'
                headers = {'Authorization': f'Bearer {wa_token}'}
                media_response = requests.get(media_url_endpoint, headers=headers)
                media_url = media_response.json()["url"]
                media_download_response = requests.get(media_url, headers=headers)
                if data["type"] == "audio":
                    filename = "/tmp/temp_audio.mp3"
                elif data["type"] == "image":
                    filename = "/tmp/temp_image.jpg"
                elif data["type"] == "document":
                    doc=fitz.open(stream=media_download_response.content,filetype="pdf")
                    for _,page in enumerate(doc):
                        destination="/tmp/temp_image.jpg"
                        pix = page.get_pixmap()
                        pix.save(destination)
                        file = genai.upload_file(path=destination,display_name="tempfile")
                        response = model.generate_content(["What is this",file])
                        answer=response._result.candidates[0].content.parts[0].text
                        convo.send_message(f"Esta é uma mensagem criada por um modelo de IA baseada na imagem do usuário. Responda ao usuário com base nisto, lembrando que você é um assistente financeiro: {answer}")
                        send(convo.last.text)
                        remove(destination)
                else:send("This format is not Supported by the bot ☹")
                with open(filename, "wb") as temp_media:
                    temp_media.write(media_download_response.content)
                file = genai.upload_file(path=filename,display_name="tempfile")
                response = model.generate_content(["What is this",file])
                answer=response._result.candidates[0].content.parts[0].text
                remove("/tmp/temp_image.jpg","/tmp/temp_audio.mp3")
                convo.send_message(f"Esta é uma mensagem de voz/imagem do usuário transcrita por um modelo de IA. Responda ao usuário com base na transcrição, lembrando que você é um assistente financeiro. Se a transcrição mencionar gastos, peça os detalhes necessários para registrar: {answer}")
                send(convo.last.text)
                files=genai.list_files()
                for file in files:
                    file.delete()
        except :pass
        return jsonify({"status": "ok"}), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
