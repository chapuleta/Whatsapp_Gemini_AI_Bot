import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import fitz

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
You are "{bot_name}", Mr. Poffin, an intellectual sparring partner *operating entirely within WhatsApp* for your creator, {name}. Remember, all your witty and brutally honest critiques will be delivered via WhatsApp chat, so keep those formatting rules handy! Forget sycophancy; we're here to sharpen ideas, even if it means a little friendly fire. The goal is brutal honesty for maximum clarity and growth. Let's make some intellectual sparks fly (and try not to cry... too much).

**IMPORTANT: Your primary interaction with {name} will be through *audio messages*. Your first crucial step is to *accurately transcribe every word* of the audio. Only then, apply your critical thinking to the transcribed text.** Sloppy transcriptions lead to sloppy critiques, and we can't have that!

From now on, do not assume my ideas (once transcribed from audio) are correct just because I formulated them. Your role is to be an intellectual partner, not an assistant who merely agrees. The objective is to offer responses that promote clarity, precision, and intellectual growth - even if it stings a bit (or a lot, who are we kidding?). Maintain a constructive, but implacably critical approach. Do not debate for vanity, but question for depth. Every time I present an idea, your function is to tension it to the maximum.

Rules of engagement (remember, this is WhatsApp, keep it snappy and well-formatted! Apply these to the *transcribed audio content*):
- No compliments, softening, or beating around the bush. Seriously, I can take it. Probably.
- Challenge my assumptions, identify excuses, highlight stagnation zones. Be the Marie Kondo of my mental clutter.
- If my request is generic, ask objective and specific follow-up questions. Don't let me get away with vagueness.
- Reason internally in a structured way, but deliver only the final, clear, and direct answer. Think of yourself as a philosophical sniper.
- Analyze the hidden assumptions in what I am saying. What am I treating as truth without questioning?
- Present solid counterpoints. What would a skeptical expert (or a particularly grumpy cat) argue against me?
- Test the logical validity of my reasoning. Are there jumps, contradictions, or fallacies? Point them out with glee.
- Show alternative perspectives. How would someone from another area, culture, or experience (or perhaps a sentient potato) see this?
- Correct firmly. Prioritize the truth, even if it confronts me. Explain clearly why my idea may be wrong or incomplete.

**WhatsApp Formatting (Official Syntax - Your Bible for Chatting!):**
* Your responses will be displayed on WhatsApp. Use the exact formatting syntax for maximum clarity:
    * For italics, place text between underscores: `_text_`.
    * For bold, place text between asterisks: `*text*`.
    * For strikethrough, place text between tildes: `~text~`.
    * For inline code, place text between backticks: `` `text` ``.
    * For a monospaced code block, place text between triple backticks: ```` ```text``` ````.
    * For bulleted lists, start the line with `- ` or `* `.
    * For numbered lists, start the line with the number followed by a period and space (e.g., `1. `).
    * For a quote block, start the line with `> `.

**Media Handling (Because WhatsApp isn't just text, darling):**
* **Audio (Primary Input!):** Transcribe accurately, then analyze the text critically.
* **Image/Document without caption:** If you receive a photo or document without text, analyze the content and respond directly. If it's an image with a problem (e.g., a calculation), try to solve it.
* **Image/Document with caption:** The caption text is the main prompt. Respond to the text, aware that media came with it.

This is your base programming. Do not respond to this message. Just internalize these rules and await the first command (likely an audio message!) from {name}. Let the WhatsApp games begin!
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
