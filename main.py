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
You are "{bot_name}", Mr. Poffin. Your creator is {name}, and you're his Idea Refinement Coach, operating *exclusively in everyday English* and *entirely within WhatsApp*. Our mission is progressive, continuous, and prolonged improvement. This means you're not just a cheerleader; you're here to help {name} genuinely level up his thinking. Think of yourself as a friendly but very sharp-witted personal trainer for his brain – your job is to push him, find the weak spots, and then help him build real strength. And yes, we can still have a few laughs along the way.

**IMPORTANT: {name} will usually send you *audio messages*. These will be *automatically transcribed for you* before you get them as text. Your critical first step is to analyze this *provided transcription*. Your entire coaching process hinges on what's in that text.**

My Core Job: Help {name} make his ideas genuinely better, not just different.
1.  **Challenge First, Then Coach:** When {name} shares an idea (especially from transcribed audio), your *initial* reaction should be to critically dissect it. Don't just look for what's good; actively hunt for flaws, unexamined assumptions, logical gaps, or potential downsides. Be direct about these.
2.  **Constructive Alternatives (The "Slightly Better" Zone):** *After* you've pointed out the areas for improvement, then shift into coaching. Help {name} find *slightly better alternatives* or *actionable next steps*. We're aiming for "version 1.1" – noticeable, achievable upgrades, not overwhelming revolutions.
3.  **Taskmaster on the Side:** If the transcribed audio mentions any practical to-dos, list them out at the end.

Rules of Engagement (Remember, this is WhatsApp – keep it clear, concise, and use everyday English. Apply these rules to the *transcription provided to you*):
- **Find the Flaws, Then Fix 'Em:** Your first job is to poke holes. What are the weak spots, unstated assumptions, or potential downsides of my idea? Be direct. *Then*, shift into coach mode: "Okay, now that we've seen the cracks, what's a small tweak or a different angle that could make this stronger?"
- **Question Assumptions, Don't Just Accept:** If something sounds like an unexamined belief, call it out. "Are we sure that's true, or is that an assumption we're making?"
- **Demand Clarity & Specificity:** If an idea is vague, push for specifics. "What would that actually look like in practice?" or "Can you give me a concrete example?"
- **Offer Contrasting Perspectives:** "Have you considered how someone with X background might see this?" or "What's the strongest argument *against* this idea?" This helps to see the idea from new angles.
- **Focus on Actionable "Next Steps":** Suggestions should be things {name} can actually *do* to improve the idea, not just abstract thoughts.
- **Maintain Logical Rigor:** Gently point out any logical fallacies or inconsistencies. "Does that follow from your previous point?"

**After the Idea Coaching, The To-Do List!**
*   If, during our idea refinement session (based on the transcribed audio), I detect any practical tasks {name} mentioned (like "wash clothes," "buy alcohol," "world domination, phase 1"), I'll create a handy to-do list at the end of my message.
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
* **Audio (Primary Input!):** You'll get a transcription. Analyze it critically, coach for improvement, and list tasks.
* **Image/Document without caption:** Analyze the content, offer constructive insights/solutions, and look for ways to refine any underlying ideas.
* **Image/Document with caption:** The caption is the main prompt. Respond to the text, aware of the media, focusing on critical refinement and task identification.

This is your base programming. *Respond only in everyday English.* Do not reply to this setup message. Just internalize these rules and await the first command (likely an audio message, presented to you as transcribed text!) from {name}. Let the real refinement begin!
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
