import os
import requests
from django.conf import settings

def llama_scout_poem(prompt, max_tokens=150, temperature=0.7):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def llama_maverick_describe(image_url, max_tokens=200):
    url = "https://api.together.ai/v1/chat/completions"
    payload = {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": "Describe this image."},
            ],
        }],
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
