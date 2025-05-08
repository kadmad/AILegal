import json
from kafka.consumer import listen
from kafka.producer import send_summary_to_kafka
from openai_client import summarize_text

def process_message(data):
    print("Received:", data)
    data = json.loads(data)
    summary = summarize_text(data['text'])
    
    payload = {
        "filename": data["filename"],
        "summary": summary
    }
    print("Sending summary:", payload)
    send_summary_to_kafka(payload)

if __name__ == "__main__":
    print("=== Summary Generation Service ===")
    listen(process_message)
