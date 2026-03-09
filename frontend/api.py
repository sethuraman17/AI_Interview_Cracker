import requests

API_URL = "http://127.0.0.1:8000/ask"

def ask_backend(question: str) -> str:
    response = requests.post(
        API_URL,
        json={"question": question},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["answer"]
