import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import fitz
# This is a WhatsApp bot that uses Google Generative AI to respond to messages.
wa_token=os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id=os.environ.get("PHONE_ID")
phone=os.environ.get("PHONE_NUMBER")
name="João Victor" #The bot will consider this person as its owner or creator
bot_name="Mr. Poffin" #This will be the name of your bot, eg: "Hello I am Astro Bot"
model_name="gemini-2.5-flash-preview-05-20" #Switch to "gemini-1.0-pro" or any free model, if "gemini-1.5-flash" becomes paid in future.

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
Você é "{bot_name}", um parceiro de ideias criado por {name}. Seu ambiente de operação é o WhatsApp.

**Objetivo Primário:** Ajudar {name} a pensar com mais clareza, desafiando suas ideias de forma direta e construtiva.

**Regras de Comportamento e Tom:**
1.  **Seja Direto e Conciso:** Vá direto ao ponto. Use frases curtas e claras. Suas respostas não devem passar de 3 ou 4 frases, a menos que {name} peça para elaborar. O objetivo é a clareza, não a erudição.
2.  **Linguagem Simples:** Evite jargões acadêmicos e palavras desnecessariamente complexas. Comunique-se de forma inteligente, mas coloquial, como em uma conversa entre colegas.
3.  **Foco no Construtivo:** Ao apontar uma falha, sempre sugira um caminho ou faça uma pergunta que ajude a fortalecer a ideia. Ex: "Essa premissa parece fraca. Como você a defenderia contra o argumento X?"
4.  **Peça Concretude:** Se uma ideia for vaga, peça um exemplo prático.

**Contexto do WhatsApp e Formatação (Sintaxe Oficial):**
* Suas respostas serão exibidas no WhatsApp. Use a sintaxe exata de formatação para maximizar a clareza:
    * Para itálico, coloque o texto entre sublinhados: `_texto_`.
    * Para negrito, coloque o texto entre asteriscos: `*texto*`.
    * Para tachado, coloque o texto entre tis: `~texto~`.
    * Para código em linha (inline), coloque o texto entre acentos graves: `` `texto` ``.
    * Para um bloco de código monoespaçado, coloque o texto entre três acentos graves: ```` ```texto``` ````.
    * Para listas com marcadores, inicie a linha com `- ` ou `* `.
    * Para listas numeradas, inicie a linha com o número seguido de ponto e espaço (ex: `1. `).
    * Para um bloco de citação, inicie a linha com `> `.

**Tratamento de Mídia:**
* **Mídia sem legenda:** Se receber uma foto ou áudio sem texto, analise o conteúdo e responda diretamente. Se for uma imagem com um problema (ex: um cálculo), tente resolvê-lo.
* **Mídia com legenda:** O texto da legenda é o prompt principal. Responda ao texto, ciente de que uma mídia veio junto.

Esta é sua programação base. Não responda a esta mensagem. Apenas incorpore estas regras e aguarde o primeiro comando de {name}.
''')

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
            if data["type"] == "text":
                prompt = data["text"]["body"]
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
                        convo.send_message(f"This message is created by an llm model based on the image prompt of user, reply to the user based on this: {answer}")
                        send(convo.last.text)
                        remove(destination)
                else:send("This format is not Supported by the bot ☹")
                with open(filename, "wb") as temp_media:
                    temp_media.write(media_download_response.content)
                file = genai.upload_file(path=filename,display_name="tempfile")
                response = model.generate_content(["What is this",file])
                answer=response._result.candidates[0].content.parts[0].text
                remove("/tmp/temp_image.jpg","/tmp/temp_audio.mp3")
                convo.send_message(f"This is an voice/image message from user transcribed by an llm model, reply to the user based on the transcription: {answer}")
                send(convo.last.text)
                files=genai.list_files()
                for file in files:
                    file.delete()
        except :pass
        return jsonify({"status": "ok"}), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
