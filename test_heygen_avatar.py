#!/usr/bin/env python3
"""
Test script for HeyGen Avatar Video API using Luna.png avatar
This script demonstrates how to use Luna.png as the avatar and integrate
with OpenAI responses for script content.
"""

import os
import requests
from heygen_avatar_video import HeyGenAvatarVideoClient, VideoInput, VideoDimension


def upload_avatar_image(client: HeyGenAvatarVideoClient, image_path: str) -> str:
    """
    Upload an avatar image to HeyGen and return the asset ID
    
    Args:
        client: HeyGen client instance
        image_path: Path to the avatar image file
        
    Returns:
        Asset ID of the uploaded image
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Avatar image not found: {image_path}")
    
    url = f"{client.base_url}/v1/asset.upload"
    
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/png')}
        headers = {'x-api-key': client.api_key}
        
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result.get('data', {}).get('asset_id')


def get_script_from_openai(prompt: str, openai_api_key: str) -> str:
    """
    Generate script content using OpenAI API
    
    Args:
        prompt: Prompt for script generation
        openai_api_key: OpenAI API key
        
    Returns:
        Generated script content
    """
    try:
        import openai
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful scriptwriter for avatar videos. Write engaging, natural-sounding scripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except ImportError:
        raise ImportError("OpenAI library not installed. Install with: pip install openai")
    except Exception as e:
        raise Exception(f"Failed to generate script with OpenAI: {e}")


def main():
    """Test the HeyGen Avatar Video API with Luna.png avatar"""
    
    # Configuration
    HEYGEN_API_KEY = os.getenv('HEYGEN_API_KEY', 'your-heygen-api-key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')
    
    # Path to Luna.png avatar
    avatar_image_path = "/home/ec2-user/OneDevelopment-Agent/Luna.png"
    
    # Initialize HeyGen client
    client = HeyGenAvatarVideoClient(api_key=HEYGEN_API_KEY)
    
    try:
        # Step 1: Upload Luna.png as avatar image
        print("Uploading Luna.png avatar...")
        avatar_asset_id = upload_avatar_image(client, avatar_image_path)
        print(f"Avatar uploaded with asset ID: {avatar_asset_id}")
        
        # Step 2: Generate script using OpenAI
        print("Generating script with OpenAI...")
        script_prompt = """
        Write a short, engaging introduction script for an AI assistant named Luna. 
        The script should be about 30-45 seconds when spoken naturally.
        Luna should introduce herself as an AI assistant and mention she can help with various tasks.
        Keep the tone friendly and professional.
        """
        
        script_content = get_script_from_openai(script_prompt, OPENAI_API_KEY)
        print(f"Generated script: {script_content}")
        
        # Step 3: Create video input configuration
        video_input = VideoInput(
            avatar_image_asset_id=avatar_asset_id,  # Use uploaded Luna.png
            script=script_content,  # Use OpenAI-generated script
            voice="en-US-JennyNeural",  # Choose appropriate voice
            background="#1a1a2e",  # Dark blue background
            circle_background_color="#16213e"  # Circle background color
        )
        
        # Step 4: Create the video
        print("Creating avatar video...")
        response = client.create_video(
            video_inputs=[video_input],
            title="Luna AI Assistant Introduction",
            caption=True,  # Enable captions for text-based input
            dimension=VideoDimension(width=1280, height=720),
            callback_id="luna_intro_video"
        )
        
        video_id = response.get('data', {}).get('video_id')
        print(f"Video creation initiated with ID: {video_id}")
        
        # Step 5: Wait for completion (optional)
        print("Waiting for video completion...")
        final_status = client.wait_for_video_completion(video_id, timeout=600)
        
        print(f"Video completed successfully!")
        print(f"Status: {final_status.get('status')}")
        
        if final_status.get('video_url'):
            print(f"Video URL: {final_status.get('video_url')}")
        
        if final_status.get('thumbnail_url'):
            print(f"Thumbnail URL: {final_status.get('thumbnail_url')}")
        
        return final_status
        
    except Exception as e:
        print(f"Error during video creation: {e}")
        return None


def test_simple_avatar():
    """Simple test without OpenAI integration"""
    
    HEYGEN_API_KEY = os.getenv('HEYGEN_API_KEY', 'your-heygen-api-key')
    avatar_image_path = "/home/ec2-user/OneDevelopment-Agent/Luna.png"
    
    client = HeyGenAvatarVideoClient(api_key=HEYGEN_API_KEY)
    
    try:
        # Upload avatar
        avatar_asset_id = upload_avatar_image(client, avatar_image_path)
        
        # Use predefined script
        script = "Hello! I'm Luna, your AI assistant. I'm here to help you with various tasks and make your work more efficient. Let's get started!"
        
        video_input = VideoInput(
            avatar_image_asset_id=avatar_asset_id,
            script=script,
            voice="en-US-JennyNeural",
            background="#1a1a2e"
        )
        
        response = client.create_video(
            video_inputs=[video_input],
            title="Luna Introduction",
            caption=True
        )
        
        video_id = response.get('data', {}).get('video_id')
        print(f"Simple test video created with ID: {video_id}")
        
        return response
        
    except Exception as e:
        print(f"Simple test error: {e}")
        return None


if __name__ == "__main__":
    print("=== HeyGen Avatar Video Test with Luna.png ===")
    print("\nChoose test mode:")
    print("1. Full test with OpenAI integration")
    print("2. Simple test without OpenAI")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\nRunning full test with OpenAI integration...")
        main()
    elif choice == "2":
        print("\nRunning simple test...")
        test_simple_avatar()
    else:
        print("Invalid choice. Running simple test...")
        test_simple_avatar()
