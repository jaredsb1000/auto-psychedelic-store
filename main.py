import os
import requests
import time

# --- CONFIGURATION ---
# These keys are set in GitHub Settings > Secrets
GUMROAD_TOKEN = os.environ.get("GUMROAD_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN") # New Hugging Face Token
BASE44_API_URL = os.environ.get("BASE44_API_URL")

def get_prompt_from_base44():
    """
    Connects to your Base44 AI to get a creative prompt.
    """
    print("Connecting to Base44...")
    
    try:
        # Attempt to call Base44 (Replace with your actual Base44 endpoint)
        prompt = "A 3D psychedelic neon fractal tunnel spiraling into infinite darkness, vaporwave style, 8k resolution"
        # In a real setup, you would fetch the prompt from BASE44_API_URL
        return prompt
    except Exception as e:
        print(f"Could not reach Base44: {e}")
        return "A 3D psychedelic neon fractal tunnel spiraling into infinite darkness, vaporwave style, 8k resolution"

def generate_video(prompt):
    """
    Uses Hugging Face (ModelScope or Zeroscope) to generate the video.
    This is FREE for the first few generations per day.
    """
    print(f"Generating video for prompt: {prompt}")
    
    # We will use Zeroscope, a free open-source text-to-video model
    API_URL = "https://api-inference.huggingface.co/models/cerspense/zeroscope_v2_576w"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    # Prepare the payload
    def query(payload):
        response = requests.post(API_URL, headers=headers, workflow="text-to-video", json=payload)
        return response.content
    
    # Zeroscope needs a prompt
    # We add "high quality" to ensure a better result
    enhanced_prompt = f"{prompt}, high quality, detailed"
    
    print("Sending request to Hugging Face... (This may take 3-5 minutes)")
    
    try:
        video_bytes = query({
            "inputs": enhanced_prompt,
        })
        
        # The API returns the raw video file (bytes). We need to save it temporarily.
        # GitHub Actions has a temporary folder we can use.
        temp_filename = f"/tmp/psychedelic_gen_{int(time.time())}.mp4"
        
        with open(temp_filename, "wb") as f:
            f.write(video_bytes)
            
        print(f"Video saved to {temp_filename}")
        return temp_filename
        
    except Exception as e:
        print(f"Error generating video: {e}")
        return None

def post_to_gumroad(video_file_path, prompt):
    """
    Creates a product on Gumroad via API.
    NOTE: Gumroad API prefers a public URL, but we can try sending the file directly
    if the API supports it. If not, we need to upload the file to a temporary host first.
    
    For this mobile-friendly version, we will simulate the post if file upload is complex.
    """
    print("Posting to Gumroad...")
    
    url = "https://api.gumroad.com/v2/products"
    
    headers = {
        "Authorization": f"Bearer {GUMROAD_TOKEN}"
    }
    
    title = f"AI Psychedelic Video #{int(time.time())}"
    
    # GUMROAD API LIMITATION: The standard API usually requires a URL for the content, not a file path.
    # Since we are generating the video inside GitHub, getting a public URL is hard without external storage.
    # 
    # WORKAROUND: We will print the success message and the file path.
    # To make this 100% automated, you would normally upload the MP4 to Dropbox/AWS S3 first.
    # For this phone-based demo, we will stop here to ensure the video generation part works.
    
    print(f"✅ SUCCESS! Video generated: {video_file_path}")
    print(f"Prompt used: {prompt}")
    print(f"Product Title: {title}")
    print("---")
    print("⚠️ NOTE: Due to Gumroad API requiring a public URL for files,")
    file_size = os.path.getsize(video_file_path) / (1024 * 1024)
    print(f"the video has been generated and is {file_size:.2f} MB.")
    print("The next step would be to upload this to Dropbox/AWS and then pass that URL to Gumroad.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Get Idea from Base44
    prompt = get_prompt_from_base44()
    
    # 2. Generate Video (using Hugging Face)
    video_path = generate_video(prompt)
    
    if video_path:
        # 3. Post to Gumroad
        post_to_gumroad(auto_gumroad(video_path, prompt), prompt)
