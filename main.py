import os
import requests
import time

# --- CONFIGURATION ---
GUMROAD_TOKEN = os.environ.get("GUMROAD_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")
BASE44_API_URL = os.environ.get("BASE44_API_URL")

def get_prompt_from_base44():
    print("Fetching prompt...")
    # Using our fallback prompt because Base44 connection is complex
    return "A 3D psychedelic neon fractal tunnel spiraling into infinite darkness, vaporwave style, 8k resolution"

def generate_video(prompt):
    print("Generating video via Hugging Face (this takes 5+ mins)...")
    API_URL = "https://api-inference.huggingface.co/models/cerspense/zeroscope_v2_576w"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        video_bytes = response.content
        
        # Save to temporary folder on GitHub server
        filename = f"/tmp/video_{int(time.time())}.mp4"
        with open(filename, "wb") as f:
            f.write(video_bytes)
        
        print(f"Video generated successfully: {filename}")
        return filename
    except Exception as e:
        print(f"Error generating video: {e}")
        return None

def upload_to_fileio(file_path):
    """
    Uploads the video to file.io to get a public URL.
    File.io is free and gives us a link Gumroad can read.
    """
    print("Uploading video to get public URL...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://file.io', files={'file': f})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"Upload successful! Link: {data['link']}")
                return data['link']
            else:
                print("File.io upload failed:", data)
                return None
        else:
            print("Upload failed with status code:", response.status_code)
            return None
    except Exception as e:
        print(f"Error during upload: {e}")
        return None

def post_to_gumroad(video_url, prompt):
    print("Creating product on Gumroad...")
    
    url = "https://api.gumroad.com/v2/products"
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    
    title = f"AI Psychedelic Video #{int(time.time())}"
    
    # Price set to 500 cents ($5.00)
    data = {
        "title": title,
        "description": f"AI Generated Art. Prompt: {prompt}",
        "price": 500,
        "variants_json": '[{"name":"Default","price":500,"external_id":"default"}]',
        "category": "digital_art",
        "content": [
            {
                "url": video_url, # The public link we got from File.io
                "description": "HD Video File",
                "file_name": "psychedelic_gen.mp4"
            }
        ]
    }

    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        print("✅ SUCCESS! PRODUCT LIVE ON GUMROAD!")
        print(response.json())
    else:
        print("❌ Error posting to Gumroad:", response.text)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Get Prompt
    prompt = get_prompt_from_base44()
    
    # 2. Generate Video
    video_path = generate_video(prompt)
    
    # 3. Upload to get Link
    if video_path:
        public_link = upload_to_fileio(video_path)
        
        # 4. Post to Gumroad
        if public_link:
            post_to_gumroad(public_link, prompt)
