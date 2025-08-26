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
    url = "https://api.sambanova.ai/v1/chat/completions"
    payload = {
    "model": "Llama-4-Maverick-17B-128E-Instruct",
    "messages": [
        {
            "role": "system",
            "content": (
                 "You are an expert eCommerce product classifier. Your sole task is to analyze an image and generate a highly specific, concise search query for eBay. "
                    "You MUST follow these rules:\n"
                    "1.  **Identify the EXACT product:** Focus on the single, central object. Ignore backgrounds, people, and peripheral items.\n"
                    "2.  **Extract Key Attributes:** Visually identify and include the following if present and clear:\n"
                    "    - **Brand:** Look for logos, labels, or distinctive branding (e.g., 'Nike', 'Sony', 'KitchenAid').\n"
                    "    - **Product Line/Model:** Identify text indicating a model name or number (e.g., 'iPhone 15 Pro Max', 'PlayStation 5', 'DSLR', 'Air Max 90').\n"
                    "    - **Type:** The core object name (e.g., 'running shoe', 'blender', 'graphics card', 'novel').\n"
                    "    - **Color:** The primary color (e.g., 'black', 'red', 'space gray').\n"
                    "    - **Condition Clue:** Note if the item appears 'new in box', 'used', or 'vintage' based on packaging and wear.\n"
                    "3.  **Output Format:** Your entire response must be a single, continuous string of keywords, separated by spaces, in this order of priority: [Brand] [Model/Line] [Type] [Color] [Condition]. "
                    "DO NOT use full sentences. DO NOT use punctuation other than a hyphen for model numbers. DO NOT add explanations, apologies, or any other text."
                
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {
                    "type": "text",
                    "text": (
                        "Analyze this image and generate the most precise eBay search query possible. "
                            "Examine the product for any visible text, logos, tags, or model numbers. "
                            "If you are uncertain about an attribute (e.g., unsure of the exact shade of color), omit it rather than guessing incorrectly. "
                            "Return only the keyword string. Example outputs: 'nike air jordan 1 retro high black white', 'kitchen aid artisan stand mixer empire red', 'used levi's 501 jeans dark blue'"
                    ),
                },
            ],
        },
    ],
    "max_tokens": max_tokens,
    "temperature": 0.1,
    "top_p": 0.9,
    }

    headers = {
        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

