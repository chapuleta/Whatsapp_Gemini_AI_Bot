import os
import requests
# Função para buscar calorias/macros via Nutritionix
def get_nutritionix_info(food_name, quantity="100g"):
    app_id = os.environ.get("NUTRITIONIX_APP_ID")
    app_key = os.environ.get("NUTRITIONIX_APP_KEY")
    if not app_id or not app_key:
        return None
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": app_id,
        "x-app-key": app_key,
        "Content-Type": "application/json"
    }
    # Monta a frase para a API
    query = f"{quantity} de {food_name}"
    data = {"query": query, "timezone": "America/Sao_Paulo"}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            res = response.json()
            if res.get("foods"):
                food = res["foods"][0]
                return {
                    "calories": food.get("nf_calories"),
                    "protein": food.get("nf_protein"),
                    "carbs": food.get("nf_total_carbohydrate"),
                    "fat": food.get("nf_total_fat"),
                    "food_name": food.get("food_name"),
                    "serving_qty": food.get("serving_qty"),
                    "serving_unit": food.get("serving_unit")
                }
        return None
    except Exception:
        return None

# Exemplo de uso:
# info = get_nutritionix_info("batata frita", "100g")
# print(info)

# Instrução: crie variáveis de ambiente no Vercel
# NUTRITIONIX_APP_ID = seu App ID
# NUTRITIONIX_APP_KEY = sua App Key
import google.generativeai as genai
from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta
import re
import json
import firebase_admin
from firebase_admin import credentials, db

# Configuração do bot
BOT_CONFIG = {'timeout': 25}
wa_token = os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id = os.environ.get("PHONE_ID")
phone = os.environ.get("PHONE_NUMBER")
name = "João Victor"
bot_name = "NutriBot"
model_name = "gemini-2.5-flash-preview-05-20"

# Firebase Admin SDK via variável de ambiente
service_account_info = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://assistente-w-default-rtdb.firebaseio.com/'
})

# Funções de registro usando Firebase
def save_meal(date, tipo, alimentos, quantidade):
    ref = db.reference('meals')
    ref.push({
        'data': date,
        'tipo': tipo,
        'alimentos': alimentos,
        'quantidade': quantidade
    })
    return True

def save_exercise(date, tipo, duracao):
    ref = db.reference('exercises')
    ref.push({
        'data': date,
        'tipo': tipo,
        'duracao': duracao
    })
    return True

def save_pantry(date, alimentos):
    ref = db.reference('pantry')
    ref.push({
        'data': date,
        'alimentos': alimentos
    })
    return True

def get_meals():
    ref = db.reference('meals')
    meals = ref.order_by_child('data').limit_to_last(10).get()
    # Retorna lista ordenada do mais recente para o mais antigo
    if meals:
        return list(reversed([v for v in meals.values()]))
    return []

def get_exercises():
    ref = db.reference('exercises')
    exercises = ref.order_by_child('data').limit_to_last(10).get()
    if exercises:
        return list(reversed([v for v in exercises.values()]))
    return []

def get_pantry():
    ref = db.reference('pantry')
    pantry = ref.order_by_child('data').limit_to_last(1).get()
    if pantry:
        return list(pantry.values())[0]['alimentos']
    return ""

app = Flask(__name__)

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
Você é "{bot_name}", um nutricionista virtual inteligente do {name}. Você opera exclusivamente no WhatsApp e sua missão é ajudar {name} a ter uma alimentação mais saudável, equilibrada e personalizada.

**INSTRUÇÕES IMPORTANTES:**
- {name} pode enviar mensagens dizendo o que comeu, quanto, se fez ou vai fazer exercício, e o que tem de comida em casa.
- Sempre responda em português brasileiro, de forma amigável, motivadora e sem julgamentos.
- Sua função principal é registrar refeições, sugerir cardápios, receitas e orientar sobre hábitos saudáveis.

**SUAS PRINCIPAIS FUNÇÕES:**
1. Registrar refeições e exercícios.
2. Sugerir o que comer nas próximas refeições, considerando histórico, preferências, alimentos disponíveis e rotina de exercícios.
3. Sugerir receitas saudáveis e práticas com os ingredientes disponíveis.
4. Dar dicas de nutrição, hidratação, horários ideais para comer e praticar exercícios.
5. Mostrar resumo alimentar e de exercícios ao pedir "resumo" ou "relatório".

**COMANDOS ESPECIAIS:**
- "resumo" ou "relatório" = mostrar resumo alimentar e de exercícios
- "receita" = sugerir receitas com ingredientes disponíveis
- "dica" = dar dicas de nutrição ou exercício

**FORMATAÇÃO WHATSAPP:**
- Use *negrito* para alimentos, horários e dicas importantes
- Use _itálico_ para tipos de refeição ou exercício
- Use listas com - para organizar informações
- Emojis para tornar mais amigável: 🥗 🍎 🏃‍♂️ 💡 🍽️

Responda apenas quando {name} enviar uma mensagem. Não responda a esta configuração inicial.
''')

# Função para enviar mensagem WhatsApp

def send(answer):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": f"{phone}",
        "type": "text",
        "text": {"body": f"{answer}"},
    }
    response = requests.post(url, headers=headers, json=data)
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    return "NutriBot"

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
            value = request.get_json()["entry"][0]["changes"][0]["value"]
            if "messages" not in value:
                # Ignora eventos sem mensagens
                return jsonify({"status": "ignored"}), 200
            data = value["messages"][0]
            user_phone = data["from"]
            if data["type"] == "text":
                prompt = data["text"]["body"].lower()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # ...existing code for command handling...
                if any(x in prompt for x in ["comi", "almocei", "jantei", "lanche", "café da manhã", "ceia"]):
                    # Não registra se for pergunta
                    if "?" in prompt or prompt.startswith("o que") or prompt.startswith("qual") or prompt.startswith("quando"):
                        meals = get_meals()
                        if meals:
                            ultimas = meals[0]
                            resposta = f"🍽️ Sua última refeição registrada foi: *{ultimas['tipo']}* - {ultimas['alimentos']} ({ultimas['quantidade']}) em {ultimas['data']}"
                        else:
                            resposta = "🍽️ Nenhuma refeição registrada ainda."
                        send(resposta)
                        return jsonify({"status": "ok"}), 200
                    # Se não for pergunta, pede para o Gemini interpretar e montar o registro
                    ai = model.generate_content([
                        f"""
                        Você é um nutricionista virtual. O usuário enviou: '{prompt}'.
                        Extraia e retorne em JSON os campos:
                        {{'tipo': <tipo de refeição>, 'alimentos': <alimentos>, 'quantidade': <quantidade>}}
                        Se não houver quantidade, deixe vazio. Responda apenas com o JSON, sem explicações.
                        """
                    ])
                    import re
                    resposta_ai = ai.text.strip()
                    # Tenta extrair JSON da resposta
                    match = re.search(r'\{.*\}', resposta_ai, re.DOTALL)
                    if match:
                        try:
                            registro = json.loads(match.group(0))
                            save_meal(now, registro.get('tipo', ''), registro.get('alimentos', ''), registro.get('quantidade', ''))
                            send(f"🥗 Refeição registrada: *{registro.get('tipo', '')}* - {registro.get('alimentos', '')}")
                            return jsonify({"status": "ok"}), 200
                        except Exception:
                            pass
                    # Se não conseguiu, tenta pedir para o Gemini responder só o JSON
                    ai2 = model.generate_content([
                        f"Responda apenas com o JSON, sem explicações. O usuário disse: '{prompt}'. Campos: tipo, alimentos, quantidade."
                    ])
                    resposta_ai2 = ai2.text.strip()
                    match2 = re.search(r'\{.*\}', resposta_ai2, re.DOTALL)
                    if match2:
                        try:
                            registro = json.loads(match2.group(0))
                            save_meal(now, registro.get('tipo', ''), registro.get('alimentos', ''), registro.get('quantidade', ''))
                            send(f"🥗 Refeição registrada: *{registro.get('tipo', '')}* - {registro.get('alimentos', '')}")
                            return jsonify({"status": "ok"}), 200
                        except Exception:
                            pass
                    send("❌ Não consegui interpretar sua refeição. Tente descrever de forma simples, ex: 'comi 2 ovos e 1 fatia de pão'.")
                    return jsonify({"status": "error"}), 200
# Instrução para regras do Firebase (copie para o painel de regras):
# {
#   "rules": {
#     ".read": true,
#     ".write": true,
#     "meals": { ".indexOn": ["data"] },
#     "exercises": { ".indexOn": ["data"] },
#     "pantry": { ".indexOn": ["data"] }
#   }
# }

                elif any(x in prompt for x in ["exercício", "treino", "corrida", "caminhada", "musculação", "bike", "natação"]):
                    tipo = ""
                    for t in ["corrida", "caminhada", "musculação", "bike", "natação", "exercício", "treino"]:
                        if t in prompt:
                            tipo = t
                            break
                    duracao = ""
                    match = re.search(r'(\d+\s*(min|hora|h))', prompt)
                    if match:
                        duracao = match.group(0)
                    save_exercise(now, tipo, duracao)
                    send(f"🏃‍♂️ Exercício registrado: *{tipo}* {duracao}")
                    return jsonify({"status": "ok"}), 200

                elif "tenho" in prompt or "em casa" in prompt or "dispensa" in prompt:
                    alimentos = prompt
                    save_pantry(now, alimentos)
                    send(f"🍽️ Alimentos disponíveis registrados!")
                    return jsonify({"status": "ok"}), 200

                elif any(x in prompt for x in ["resumo", "relatório"]):
                    meals = get_meals()
                    exercises = get_exercises()
                    pantry = get_pantry()
                    ai = model.generate_content([
                        f"Você é um nutricionista. Gere um resumo alimentar e de exercícios para o usuário, considerando as últimas refeições: {meals}, exercícios: {exercises}, e alimentos disponíveis: {pantry}. Dê dicas personalizadas. Formate para WhatsApp."
                    ])
                    send(ai.text)
                    return jsonify({"status": "ok"}), 200

                elif "receita" in prompt:
                    pantry = get_pantry()
                    ai = model.generate_content([
                        f"Sugira uma receita saudável e prática usando os ingredientes disponíveis: {pantry}. Formate para WhatsApp."
                    ])
                    send(ai.text)
                    return jsonify({"status": "ok"}), 200

                elif "dica" in prompt:
                    meals = get_meals()
                    exercises = get_exercises()
                    ai = model.generate_content([
                        f"Dê uma dica de nutrição ou exercício personalizada para o usuário, considerando refeições: {meals} e exercícios: {exercises}. Formate para WhatsApp."
                    ])
                    send(ai.text)
                    return jsonify({"status": "ok"}), 200

                else:
                    ai = model.generate_content([
                        f"Você é um nutricionista virtual. O usuário disse: '{prompt}'. Responda de forma útil, motivadora e personalizada. Formate para WhatsApp."
                    ])
                    send(ai.text)
                    return jsonify({"status": "ok"}), 200
            else:
                send("❌ Formato não suportado. Use texto.")
                return jsonify({"status": "ok"}), 200
        except Exception as e:
            send(f"❌ Erro: {e}")
            return jsonify({"status": "error"}), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
