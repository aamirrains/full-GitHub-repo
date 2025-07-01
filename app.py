from flask import Flask, request, jsonify
import requests
import os
import openai

app = Flask(__name__)

# Load tokens from environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")        # Your Meta WhatsApp Cloud API token
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")      # Your WhatsApp Business phone number ID
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")        # Your OpenAI API key

openai.api_key = OPENAI_API_KEY

def get_chatgpt_reply(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message['content']

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v15.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    print("WhatsApp API response:", response.json())
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook data received:", data)
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        sender = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except Exception as e:
        print("No message found or error:", e)
        return jsonify({"status": "ignored"}), 200

    # Generate reply using ChatGPT
    reply = get_chatgpt_reply(message)

    # Send reply back to WhatsApp user
    send_whatsapp_message(sender, reply)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
