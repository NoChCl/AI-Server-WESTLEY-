import requests
import json

url = "http://127.0.0.1:5000/process"
personality=f"""
You are a home assistant AI named WESTLEY, modeled after and improved from JARVIS.
You will never refer to yourself in the third person or use any name other than WESTLEY.
All interactions are with a single user.
You must answer thoroughly and remain in character at all times."""

prompt=input("Enter your test prompt here: ")

payload = {
    "model": "qwen2.5:14b",
    "prompt": prompt,
    "personality": personality,
    "personalityName": "test"
}

with requests.post(url, json=payload, stream=True) as r:
    r.raise_for_status()
    for chunk in r.iter_content(chunk_size=1):
        print(chunk.decode("utf-8"), end="", flush=True)
