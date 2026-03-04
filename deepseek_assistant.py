import requests
from gtts import gTTS
from playsound import playsound
import os

# ------------------------
API_KEY = "ff8cf1fff71844bd86c722232af1f636"  # <-- અહીં તમારી API key paste કરો
API_URL = "https://api.deepseek.com/v1/chat/completions"
# ------------------------

# DeepSeek API function
def ask_deepseek(question):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": question}]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Network Error: {e}"

# Voice output function using gTTS + playsound
def speak(text):
    try:
        tts = gTTS(text=text, lang='gu')  # Gujarati
        fp = "temp.mp3"
        tts.save(fp)
        playsound(fp)
        os.remove(fp)
    except Exception as e:
        print(f"Voice Error: {e}")

# Main loop
print("DeepSeek AI Assistant શરૂ છે! Type 'exit' to quit.")
while True:
    user_input = input("તમારો પ્રશ્ન લખો: ")
    if user_input.lower() in ["exit", "quit"]:
        print("અલવિદા!")
        break
    answer = ask_deepseek(user_input)
    print("Assistant:", answer)
    speak(answer)
