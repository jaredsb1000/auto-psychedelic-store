import os
import requests
import time
import random

# --- CONFIGURATION ---
GUMROAD_TOKEN = os.environ.get("GUMROAD_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# We removed Base44. We will use these lists to create random prompts.
ADJECTIVES = ["Neon", "Golden", "Cosmic", "Liquid", "Fractal", "Dark", "Cyberpunk", "Holographic"]
NOUNS = ["Tunnel", "Galaxy", "Ocean", "Dreamscape", "Void", "Portal", "Abstract Wave", "Crystal"]
STYLES = ["Vaporwave", "Psychedelic", "Surrealism", "Glitch Art", "8k Resolution", "High Contrast"]

def get_random_prompt():
    """Generates a random idea for the video."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    style = random.choice(STYLES)
    return f"A {adj} {noun} in the style of {style}, trippy, visual experience"

def generate_video(prompt):
    print(f"🎨 Generating video: {prompt}")
    API_URL = "https://api-inference.huggingface.co/models/cerspense/zeroscope_v2_576w"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        video_bytes = response.content
        filename = f"/tmp/video_{int(time.time())}.mp4"
        with open(filename, "wb") as f:
            f.write(video_bytes)
        return filename
    except Exception as e:
        print(f"Error: {e}")
        return None

def upload_to_fileio(file_path):
    print("☁️ Uploading video...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://file.io', files={'file': f})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['link']
        return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None

def post_to_gumroad(video_url):
    print(f"💰 Posting to Gumroad for $5.00...")
    
    url = "https://api.gumroad.com/v2/products"
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    
    # Price is fixed at 500 cents ($5.00)
    data = {
        "title": f"Psychedelic Video #{int(time.time())}",
        "description": "AI Generated Art. Unique digital asset.",
        "price": 500, 
        "variants_json": '[{"name":"Default","price":500,"external_id":"default"}]',
        "category": "digital_art",
        "content": [{"url": video_url, "description": "Video File", "file_name": "video.mp4"}]
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("✅ SUCCESS! Product created ($5.00).")
    else:
        print("❌ Gumroad Error:", response.text)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Random Idea
    prompt = get_random_prompt()
    
    # 2. Generate
    video_path = generate_video(prompt)
    
    # 3. Upload
    if video_path:
        link = upload_to_fileio(video_path)
        
        # 4. Post
        if link:
            post_to_gumroad(link)
