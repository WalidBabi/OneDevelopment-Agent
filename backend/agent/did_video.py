"""
D-ID Video Generation - Talking Avatars
========================================
Generate realistic talking avatar videos using D-ID API.
D-ID specializes in creating photorealistic talking heads from images.

Features:
- Realistic lip-sync
- Professional quality
- Fast generation (10-30 seconds)
- Cloud-based (no laptop needed)
- Works with any image
"""

import os
import logging
import time
from typing import Optional
from pathlib import Path
import httpx
import base64

logger = logging.getLogger(__name__)


class DIDVideo:
    """
    D-ID Video Generator for talking avatars.
    
    Creates realistic lip-synced videos from image + audio/text.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize D-ID Video Generator
        
        Args:
            api_key: D-ID API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.getenv('DID_API_KEY')
        self.base_url = "https://api.d-id.com"
        
        if not self.api_key:
            logger.warning("⚠️  D-ID API key not found. Video generation will not work.")
            logger.warning("   Set DID_API_KEY in your environment or .env file")
            logger.warning("   Get your API key from: https://studio.d-id.com/")
            self.available = False
        else:
            self.available = True
            logger.info("✅ D-ID Video Generator initialized")
    
    def generate_talking_video(
        self,
        text: str,
        image_path: str,
        audio_url: Optional[str] = None,
        output_path: Optional[str] = None,
        voice: str = 'en-US-JennyNeural',  # Microsoft Azure voice
    ) -> Optional[bytes]:
        """
        Generate a realistic talking avatar video using D-ID.
        
        Process:
        1. Upload image to D-ID (or use URL)
        2. Either provide audio_url OR text for TTS
        3. D-ID generates lip-synced video
        4. Poll for completion
        5. Download and return video
        
        Args:
            text: Text for avatar to speak
            image_path: Path to Luna's image
            audio_url: Optional URL to pre-generated audio
            output_path: Optional path to save video
            voice: Voice ID (D-ID supports Microsoft Azure voices)
        
        Returns:
            Video bytes if successful, None otherwise
        """
        if not self.available:
            logger.error("❌ D-ID not configured")
            return None
        
        try:
            logger.info("🎬 Generating realistic talking video with D-ID...")
            logger.info(f"   Image: {image_path}")
            logger.info(f"   Voice: {voice}")
            logger.info(f"   Text: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            # Read image
            image_path = Path(image_path)
            if not image_path.exists():
                logger.error(f"❌ Image not found: {image_path}")
                return None
            
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Encode image as base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Step 1: Create talk
            talk_id = self._create_talk(
                image_data=image_b64,
                text=text,
                audio_url=audio_url,
                voice=voice
            )
            
            if not talk_id:
                return None
            
            # Step 2: Poll for completion
            video_url = self._poll_for_completion(talk_id)
            
            if not video_url:
                return None
            
            # Step 3: Download video
            video_bytes = self._download_video(video_url)
            
            if not video_bytes:
                return None
            
            # Step 4: Save if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(video_bytes)
                logger.info(f"✅ Video saved to: {output_path}")
            
            logger.info(f"✅ Video generated successfully: {len(video_bytes)} bytes")
            return video_bytes
            
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            logger.exception("Full traceback:")
            return None
    
    def _create_talk(
        self,
        image_data: str,
        text: str,
        audio_url: Optional[str],
        voice: str
    ) -> Optional[str]:
        """Create a talk on D-ID and return the talk ID"""
        try:
            url = f"{self.base_url}/talks"
            
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Build payload
            payload = {
                "source_url": f"data:image/png;base64,{image_data}",
                "script": {}
            }
            
            # Use either audio URL or text-to-speech
            if audio_url:
                payload["script"]["audio_url"] = audio_url
                logger.info(f"📥 Using audio URL: {audio_url}")
            else:
                payload["script"]["type"] = "text"
                payload["script"]["input"] = text
                payload["script"]["provider"] = {
                    "type": "microsoft",
                    "voice_id": voice
                }
                logger.info(f"🎤 Using text-to-speech: {voice}")
            
            logger.info(f"📡 POST {url}")
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    talk_id = data.get('id')
                    logger.info(f"✅ Talk created: {talk_id}")
                    return talk_id
                else:
                    logger.error(f"❌ Create talk error: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Create talk failed: {e}")
            return None
    
    def _poll_for_completion(self, talk_id: str, max_attempts: int = 60) -> Optional[str]:
        """Poll for talk completion and return video URL"""
        try:
            url = f"{self.base_url}/talks/{talk_id}"
            
            headers = {
                "Authorization": f"Basic {self.api_key}"
            }
            
            logger.info(f"⏳ Polling for video completion (ID: {talk_id})...")
            
            with httpx.Client(timeout=30.0) as client:
                for attempt in range(max_attempts):
                    time.sleep(2)  # Wait 2 seconds between polls
                    
                    response = client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get('status')
                        
                        if status == 'done':
                            video_url = data.get('result_url')
                            logger.info(f"✅ Video ready! URL: {video_url}")
                            return video_url
                            
                        elif status == 'error':
                            error_msg = data.get('error', {}).get('description', 'Unknown error')
                            logger.error(f"❌ Generation failed: {error_msg}")
                            return None
                            
                        elif status in ['created', 'processing']:
                            progress = ((attempt + 1) / max_attempts) * 100
                            logger.info(f"⏳ Still processing... {progress:.0f}% ({attempt+1}/{max_attempts})")
                            continue
                            
                        else:
                            logger.warning(f"⚠️  Unknown status: {status}")
                            continue
                    
                    else:
                        logger.error(f"❌ Poll error: {response.status_code}")
                        return None
                
                logger.error("❌ Timeout waiting for video (2 minutes)")
                return None
                
        except Exception as e:
            logger.error(f"❌ Polling failed: {e}")
            return None
    
    def _download_video(self, video_url: str) -> Optional[bytes]:
        """Download the generated video"""
        try:
            logger.info(f"📥 Downloading video from: {video_url}")
            
            with httpx.Client(timeout=60.0) as client:
                response = client.get(video_url)
                
                if response.status_code == 200:
                    video_bytes = response.content
                    logger.info(f"✅ Video downloaded: {len(video_bytes)} bytes")
                    return video_bytes
                else:
                    logger.error(f"❌ Download error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if D-ID video generation is available"""
        return self.available


# Global singleton instance
_did_video = None


def get_did_video() -> DIDVideo:
    """Get the global D-ID Video instance"""
    global _did_video
    if _did_video is None:
        _did_video = DIDVideo()
    return _did_video


def generate_luna_video_did(
    text: str,
    image_path: str,
    audio_url: Optional[str] = None,
    output_path: Optional[str] = None
) -> Optional[bytes]:
    """
    Convenience function to generate Luna's talking video with D-ID
    
    Args:
        text: Text for Luna to speak
        image_path: Path to Luna's image
        audio_url: Optional pre-generated audio URL
        output_path: Optional path to save video
    
    Returns:
        Video bytes if successful, None otherwise
    """
    video_gen = get_did_video()
    return video_gen.generate_talking_video(
        text=text,
        image_path=image_path,
        audio_url=audio_url,
        output_path=output_path,
        voice='en-US-JennyNeural'  # Microsoft Azure voice (similar to Luna)
    )





