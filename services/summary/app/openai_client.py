import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text(text):
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes legal and medical documents."},
            {"role": "user", "content": f"Summarize the following content:\n{text}"}
        ]
    )
    return chat_response.choices[0].message.content.strip()