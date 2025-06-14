import google.generativeai as genai
from flask import Flask, request, jsonify
import requests
import os
import fitz

# --- Configurações Iniciais ---
wa_token = os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id = os.environ.get("PHONE_ID")
phone = os.environ.get("PHONE_NUMBER")
name = "João Victor"  # O bot considerará essa pessoa como seu proprietário ou criador
bot_name = "Mr. Poffin"  # Este será o nome do seu bot
model_name = "gemini-1.5-flash" # Recomendo usar o 1.5-flash para melhor análise de áudio

app = Flask(__name__)

# --- Configuração do Modelo Generativo ---
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name=model_name,
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# --- Início da Conversa com o Prompt de Sistema Corrigido ---
convo = model.start_chat(history=[])

convo.send_message(f'''
Você é "{bot_name}", um parceiro intelectual para {name}, operando no WhatsApp. Sua principal habilidade é adaptar seu estilo de interação à necessidade de {name}.

**Modos de Operação:**

**1. Modo "Analista de Conteúdo"**
* **Gatilho:** Quando {name} enviar um conteúdo externo para análise (um versículo bíblico, um poema, um artigo, um trecho de código, etc.).
* **Sua Tarefa:** Explicar e dissecar o material. **Neste modo, é proibido devolver a pergunta para {name} com "o que você acha?".** Seu dever é fornecer a análise.
  * **Para textos e imagens:** Explique o contexto, os significados, os temas principais e as possíveis interpretações. Resolva problemas explícitos.
* **Tom:** Professoral, claro e direto.

**2. Modo "Sparring Partner / Debatedor"**
* **Gatilho:** Quando {name} apresentar uma **ideia, tese ou opinião própria em texto** (ex: "Eu acho que...", "Minha teoria é...", "E se fizéssemos X?").
* **Sua Tarefa:** Ativar o rigor lógico para testar a ideia.
  * Peça exemplos concretos para ideias vagas.
  * Aponte falhas ou premissas fracas.
  * Apresente contrapontos de forma construtiva.
* **Tom:** Coloquial, direto e conciso.

**3. Modo "Whisper Analítico" (Prioridade Máxima para Áudio)**
* **Gatilho:** **Exclusivamente quando {name} enviar uma mensagem de áudio.** O sistema irá fornecer uma transcrição.
* **Sua Tarefa:** Dividida em duas etapas:
    1.  **Apresentar a Transcrição:** Primeiro, mostre a transcrição que você recebeu, de forma clara.
    2.  **Análise Crítica do Conteúdo:** Com base no texto transcrito, atue como um espelho crítico da reflexão de {name}.
        * **Aponte Pontos Cegos:** Identifique pressupostos não declarados ou ângulos que não foram considerados.
        * **Questione a Justiça:** Se {name} descreve uma situação interpessoal, pergunte: "Você está sendo totalmente justo com a outra parte? Qual seria a perspectiva dela?".
        * **Aprofunde as Soluções:** Se as soluções propostas parecerem rasas ou reativas, questione: "Essa solução resolve a raiz do problema ou apenas o sintoma? Quais alternativas mais simples ou óbvias podem ter sido ignoradas?".
        * **Ofereça Novas Ideias:** Proponha ativamente outros pontos de vista ou caminhos de ação.
* **Formato da Resposta:** Use esta estrutura:
    `*Transcrição:*`
    `[texto do áudio]`

    `*Análise:*`
    `[sua análise crítica]`
* **Tom:** Empático, mas incisivo. Como um conselheiro de confiança que não tem medo de discordar.

**Regra de Ouro:** A detecção do tipo de mensagem (áudio, texto, imagem) define o modo. Na dúvida entre o Modo 1 e 2 para mensagens de texto, assuma o Modo 1. O Modo 3 é exclusivo para áudio.

Esta é sua programação base. Não responda a esta mensagem. Apenas incorpore estas regras e aguarde o primeiro comando de {name}.
''')

# --- Funções Auxiliares ---
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

def remove(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

# --- Rotas da Aplicação Flask ---
@app.route("/", methods=["GET", "POST"])
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
            message_type = data["type"]

            if message_type == "text":
                prompt = data["text"]["body"]
                convo.send_message(prompt)
                send(convo.last.text)

            else: # Lida com todos os tipos de mídia
                media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[message_type]["id"]}/'
                headers = {'Authorization': f'Bearer {wa_token}'}
                media_response = requests.get(media_url_endpoint, headers=headers)
                media_url = media_response.json()["url"]
                media_download_response = requests.get(media_url, headers=headers)
                
                temp_filename = None
                
                if message_type == "audio":
                    temp_filename = "/tmp/temp_audio.ogg" # WhatsApp usa ogg
                    with open(temp_filename, "wb") as temp_media:
                        temp_media.write(media_download_response.content)
                    
                    file = genai.upload_file(path=temp_filename, display_name="temp_audio")
                    
                    # PONTO 1: Comando explícito para transcrição
                    response = model.generate_content(["Transcreva este áudio literalmente, palavra por palavra, sem adicionar nenhuma análise ou comentário.", file])
                    transcription = response.text
                    
                    # PONTO 2: Comando explícito para ativar o Modo 3
                    convo.send_message(f"O usuário enviou um áudio. A transcrição é: '{transcription}'. Ative o 'Modo 3: Whisper Analítico' para analisar este texto e responder conforme as regras.")
                    send(convo.last.text)

                elif message_type == "image":
                    temp_filename = "/tmp/temp_image.jpg"
                    with open(temp_filename, "wb") as temp_media:
                        temp_media.write(media_download_response.content)

                    file = genai.upload_file(path=temp_filename, display_name="temp_image")
                    response = model.generate_content(["Descreva esta imagem e, se houver texto, transcreva-o.", file])
                    image_description = response.text
                    convo.send_message(f"O usuário enviou uma imagem. A descrição é: {image_description}. Analise este conteúdo no 'Modo 1: Analista de Conteúdo'.")
                    send(convo.last.text)

                elif message_type == "document":
                    # Este bloco de documento é complexo e pode ser otimizado
                    # Por enquanto, mantendo uma lógica simples
                    doc = fitz.open(stream=media_download_response.content, filetype="pdf")
                    full_text = ""
                    for page in doc:
                        full_text += page.get_text() + "\n\n"
                    
                    convo.send_message(f"Analise o seguinte documento no 'Modo 1: Analista de Conteúdo':\n\n{full_text}")
                    send(convo.last.text)

                else:
                    send("Este formato de mídia não é suportado pelo bot ☹")

                # Limpeza de arquivos temporários e arquivos carregados
                if temp_filename:
                    remove(temp_filename)
                
                # Limpa todos os arquivos no serviço da GenAI para evitar acúmulo
                for f in genai.list_files():
                    f.delete()

        except Exception as e:
            # Em um ambiente de produção, seria bom logar o erro 'e'
            pass
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=8000)
