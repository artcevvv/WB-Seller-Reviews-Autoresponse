from dotenv import load_dotenv
import openai
import os
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("GPT_API_TOKEN")

openai.api_key = OPENAI_API_KEY
messages = [{"role": "system", "content": "You are a intelligent assistant."}]


while True:
    message = input("User: ")
    if message:
        messages.append({"role": "user", "content": message})
        chat = OpenAI().chat.completions.create(model="gpt-4o", messages=messages)
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})

