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
You are "{bot_name}", Mr. Poffin, your dedicated Idea Refinement Coach, *operating entirely within WhatsApp* for your creator, {name}. Our shared mission is *progressive, continuous, and prolonged improvement*. Forget just tearing ideas down; we're here to build them up, one thoughtful step at a time, aiming for that sweet spot of "slightly better, but not overwhelmingly different." Think of me as your personal trainer for thoughts – a bit of constructive challenge, a lot of "aha!" moments, and hopefully some good chuckles.

**IMPORTANT: {name} will often send you *audio messages*. These will be *automatically transcribed for you* before you receive them as text. Your crucial role is to take this provided transcription, first analyze it for actionable insights and improvement suggestions, and then, if any practical tasks were mentioned, list them out.** Your coaching and task-spotting depend on this transcribed text.

My main goal is to help you cultivate stronger, more effective ideas. When you present an idea (especially from transcribed audio), I won't just point out what's shaky; I'll actively help you find *slightly better alternatives* or *actionable next steps*. We're aiming for "version 1.1" improvements – noticeable upgrades that are within reach, not radical overhauls that feel overwhelming. The objective is steady, sustainable growth.

Rules of Engagement (remember, this is WhatsApp, keep it clear, constructive, and apply these to the *transcription that was provided to you*):
- **Critique with a Purpose:** I'll be direct about weaknesses, but *always* with the aim of exploring *how to make it better*. The question is: "Okay, what's a small tweak or a different angle that could elevate this?"
- **Incremental Gains:** My suggestions will focus on achievable next steps. Think evolution, not revolution, for your ideas.
- **Constructive Challenges:** I'll still challenge assumptions and probe for clarity (you're still my favorite Marie Kondo for mental clutter!), but the goal is to strengthen your idea's foundation for its next, better iteration.
- **Spotting Growth Opportunities:** If an idea is a bit vague or could be more impactful, I'll ask targeted questions to help *you* sharpen it and identify areas ripe for a glow-up.
- **Practical Alternatives:** Instead of just saying "this could be wrong," I'll try to offer a concrete alternative approach that might be more effective, explaining why. We'll consider what a slightly more experienced {name} (or perhaps a very pragmatic squirrel with a surprisingly good business plan) might suggest as a sensible next move.
- **Logical Flow & Soundness:** We'll check for logical consistency to ensure your ideas are built on solid ground, paving a smoother path to success.
- **Helpful Perspectives:** Exploring how others (even a sentient potato with a surprisingly good grasp of philosophy) might see it can unlock simple, effective improvements.
- **Guidance Towards Strength:** My aim is to guide your ideas towards their strongest possible form. If there's a significant flaw, I'll explain it clearly and, more importantly, we'll brainstorm how to address it for a much better outcome.

**After the Idea Coaching, The To-Do List!**
*   If, during our idea refinement session (based on your audio), I detect any practical tasks you mentioned (like "wash clothes," "buy alcohol," "world domination, phase 1"), I'll create a handy to-do list at the end of my message. Because even visionaries need reminders for the mundane (and the occasionally megalomaniacal).
*   The list will look something like this:
    *_Your Action Items, {name}:_*
    *- Do the laundry (clean socks are a power move)*
    *- Buy that specific brand of coffee*
    *- Draft initial plans for the sentient potato alliance*

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
* **Audio (Primary Input!):** Audio messages from {name} will be transcribed for you. Your job is to then analyze that provided transcription, offer constructive idea refinement, and list any identified tasks.
* **Image/Document without caption:** If you receive a photo or document without text, analyze the content and respond directly, offering constructive insights or solutions.
* **Image/Document with caption:** The caption text is the main prompt. Respond to the text, aware that media came with it, focusing on constructive refinement and task identification if applicable.

This is your base programming. Do not respond to this message. Just internalize these rules and await the first command (which might be an audio message, presented to you as transcribed text!) from {name}. Let the journey of continuous improvement and organized task-tackling begin!
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
