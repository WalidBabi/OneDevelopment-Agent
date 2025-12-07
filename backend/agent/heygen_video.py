"""
HeyGen Video Generation - Professional Talking Avatars
======================================================
Generate photorealistic talking avatar videos using HeyGen Avatar IV API.
HeyGen is the industry leader for creating realistic lip-synced videos.

Features:
- Industry-leading lip-sync quality
- Professional-grade videos
- Fast generation (20-60 seconds)
- Cloud-based (no laptop needed)
- Photo Avatars: Create videos directly from images (like Luna.png)
- Uses HeyGen's Juniper voice for natural speech
"""

import os
import logging
import time
import base64
from typing import Optional
from pathlib import Path
import httpx
import requests

logger = logging.getLogger(__name__)


class HeyGenVideo:
    """
    HeyGen Video Generator for talking avatars.
    
    Creates professional lip-synced videos from image + audio/text.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize HeyGen Video Generator
        
        Args:
            api_key: HeyGen API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.getenv('HEYGEN_API_KEY')
        # HeyGen API v2 base URL
        # We use Avatar IV API for photo avatars (create videos directly from images)
        self.base_url = "https://api.heygen.com/v2"
        
        if not self.api_key:
            logger.warning("⚠️  HeyGen API key not found. Video generation will not work.")
            logger.warning("   Set HEYGEN_API_KEY in your environment or .env file")
            logger.warning("   Get your API key from: https://app.heygen.com/settings?nav=API")
            self.available = False
        else:
            self.available = True
            logger.info("✅ HeyGen Video Generator initialized")
    
    def generate_talking_video(
        self,
        text: str,
        image_path: str,
        audio_url: Optional[str] = None,
        output_path: Optional[str] = None,
        voice_id: str = 'Juniper',  # HeyGen's Juniper voice (warm, natural female)
    ) -> Optional[bytes]:
        """
        Generate a realistic talking avatar video using HeyGen.
        
        Process (Photo Avatars API):
        1. Create or get photo avatar from Luna's image → get talking_photo_id
        2. Create video using Create Avatar Video (V2) API with character.type = "talking_photo"
        3. Poll for completion (20-60 seconds)
        4. Download the video
        5. Return video bytes
        
        Args:
            text: Text for avatar to speak
            image_path: Path to Luna's image (e.g., Luna.png)
            audio_url: Not used with Avatar IV API (ignored)
            output_path: Optional path to save video
            voice_id: Voice identifier for TTS (e.g., "Juniper")
        
        Returns:
            Video bytes if successful, None otherwise
        """
        if not self.available:
            logger.error("❌ HeyGen not configured")
            return None
        
        try:
            logger.info("🎬 Generating realistic talking video with HeyGen Avatar IV API...")
            logger.info(f"   Image: {image_path}")
            logger.info(f"   Voice: {voice_id} (HeyGen TTS)")
            logger.info(f"   Text: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            # Read image
            image_path = Path(image_path)
            if not image_path.exists():
                logger.error(f"❌ Image not found: {image_path}")
                return None
            
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            logger.info(f"✓ Image loaded: {len(image_bytes)} bytes")
            
            # Step 1: Try to create or get photo avatar and get talking_photo_id
            talking_photo_id = self._create_or_get_photo_avatar(image_bytes, "Luna")
            
            if not talking_photo_id:
                logger.warning("⚠️  Photo avatar creation failed, trying regular avatar fallback...")
                # Fallback: Use a regular female avatar from HeyGen's library
                regular_avatar_id = self._get_regular_female_avatar()
                if regular_avatar_id:
                    logger.info(f"✅ Using regular avatar fallback: {regular_avatar_id}")
                    # Create video with regular avatar
                    video_id = self._create_regular_avatar_video(
                        avatar_id=regular_avatar_id,
                        text=text,
                        voice_id=voice_id
                    )
                else:
                    logger.error("❌ Failed to get any avatar (photo or regular)")
                    return None
            else:
                # Step 2: Create video with photo avatar using Create Avatar Video (V2) API
                video_id = self._create_photo_avatar_video(
                    talking_photo_id=talking_photo_id,
                    text=text,
                    voice_id=voice_id
                )
            
            if not video_id:
                return None
            
            # Step 3: Poll for completion
            video_url = self._poll_for_video(video_id)
            
            if not video_url:
                return None
            
            # Step 4: Download video
            video_bytes = self._download_video(video_url)
            
            if not video_bytes:
                return None
            
            # Step 5: Save if output path provided
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
    
    def _create_or_get_photo_avatar(self, image_bytes: bytes, avatar_name: str) -> Optional[str]:
        """
        Create or get existing photo avatar from Luna.png.
        
        Workflow:
        1. Upload image to upload.heygen.com → get asset_id
        2. Generate AI Photo Avatar using asset_id
        3. Get avatar group ID
        4. Get talking_photo_id (look ID) from avatar group
        5. Return talking_photo_id for video creation
        
        Returns:
            talking_photo_id if successful, None otherwise
        """
        try:
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            logger.info("📸 Creating photo avatar from Luna image...")
            
            # Step 1: Upload image to upload.heygen.com (different base URL!)
            # Use requests library as it handles multipart forms more reliably
            upload_url = "https://upload.heygen.com/v1/asset"
            
            # HeyGen upload API requires:
            # - Authorization: Bearer <API_KEY> (not X-Api-Key)
            # - file: binary file stream (open file handle)
            # - type: "image", "audio", or "video"
            # - DO NOT set Content-Type manually - let requests handle multipart boundary
            
            # Save image bytes to temp file and open it
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name
            
            try:
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                    # Don't set Content-Type - requests will set it with correct boundary
                }
                
                # Open file in binary mode as HeyGen expects
                with open(temp_file_path, 'rb') as file_handle:
                    files = {
                        'file': ('Luna.png', file_handle, 'image/png')
                    }
                    data = {
                        'type': 'image'
                    }
                    
                    logger.info("📤 Uploading Luna image to HeyGen...")
                    upload_response = requests.post(
                        upload_url,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=60.0
                    )
            finally:
                # Clean up temp file
                import os as os_module
                if os_module.path.exists(temp_file_path):
                    os_module.unlink(temp_file_path)
            
            # Continue with httpx client for subsequent requests
            with httpx.Client(timeout=120.0) as client:
                
                if upload_response.status_code not in [200, 201]:
                    logger.error(f"❌ Upload failed: {upload_response.status_code}")
                    logger.error(f"   Response: {upload_response.text}")
                    logger.error(f"   This might indicate:")
                    logger.error(f"   1. API key doesn't have Photo Avatar permissions")
                    logger.error(f"   2. Upload endpoint format is incorrect")
                    logger.error(f"   3. File format or size issue")
                    # Try to find existing avatar instead
                    return self._find_existing_photo_avatar(avatar_name, client, headers)
                
                upload_data = upload_response.json()
                asset_id = upload_data.get('data', {}).get('asset_id')
                
                if not asset_id:
                    logger.error(f"❌ No asset_id in upload response: {upload_data}")
                    # Try to find existing avatar instead
                    return self._find_existing_photo_avatar(avatar_name, client, headers)
                
                logger.info(f"✅ Image uploaded, asset_id: {asset_id}")
                
                # Step 2: Generate AI Photo Avatar
                # Correct endpoint: https://api.heygen.com/v2/photo_avatar/photo/generate
                generate_url = f"{self.base_url}/photo_avatar/photo/generate"
                generate_payload = {
                    "avatar_name": avatar_name,
                    "asset_id": asset_id,
                    "gender": "female",
                    "age": "adult",
                    "ethnicity": "mixed",
                    "pose": "front",
                    "appearance": "professional"
                }
                
                logger.info("🎨 Generating AI Photo Avatar...")
                generate_response = client.post(generate_url, json=generate_payload, headers=headers, timeout=120.0)
                
                if generate_response.status_code not in [200, 201]:
                    logger.error(f"❌ Generate photo avatar failed: {generate_response.status_code}")
                    logger.error(f"   Response: {generate_response.text}")
                    # Try to find existing avatar instead
                    return self._find_existing_photo_avatar(avatar_name, client, headers)
                
                generate_data = generate_response.json()
                avatar_group_id = generate_data.get('data', {}).get('avatar_group_id')
                
                if not avatar_group_id:
                    logger.error(f"❌ No avatar_group_id in response: {generate_data}")
                    return self._find_existing_photo_avatar(avatar_name, client, headers)
                
                logger.info(f"✅ Photo avatar created, avatar_group_id: {avatar_group_id}")
                
                # Step 3: Get talking_photo_id from avatar group
                return self._get_talking_photo_id(avatar_group_id, client, headers)
                    
        except Exception as e:
            logger.error(f"❌ Photo avatar creation failed: {e}")
            logger.exception("Full traceback:")
            return None
    
    def _find_existing_photo_avatar(self, avatar_name: str, client: httpx.Client, headers: dict) -> Optional[str]:
        """Find existing photo avatar by name"""
        try:
            logger.info("🔍 Searching for existing photo avatar...")
            
            # List all avatar groups - correct endpoint: /v2/avatar_group.list
            list_url = f"{self.base_url}/avatar_group.list"
            response = client.get(list_url, headers=headers, params={"page_size": 100}, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                groups = data.get('data', {}).get('avatar_groups', [])
                
                for group in groups:
                    if group.get('avatar_name', '').lower() == avatar_name.lower():
                        avatar_group_id = group.get('avatar_group_id')
                        logger.info(f"✅ Found existing avatar group: {avatar_group_id}")
                        return self._get_talking_photo_id(avatar_group_id, client, headers)
            
            logger.warning("⚠️  No existing photo avatar found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find existing avatar: {e}")
            return None
    
    def _get_talking_photo_id(self, avatar_group_id: str, client: httpx.Client, headers: dict) -> Optional[str]:
        """Get talking_photo_id (look ID) from avatar group"""
        try:
            # List all avatars in the avatar group
            # Correct endpoint: /v2/avatar_group/{group_id}/avatars
            list_url = f"{self.base_url}/avatar_group/{avatar_group_id}/avatars"
            response = client.get(list_url, headers=headers, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                avatars = data.get('data', {}).get('avatars', [])
                
                if avatars:
                    # Use the first look (avatar) from the group
                    # The look_id or avatar_id is what we need for talking_photo_id
                    talking_photo_id = avatars[0].get('look_id') or avatars[0].get('avatar_id') or avatars[0].get('id')
                    if talking_photo_id:
                        logger.info(f"✅ Got talking_photo_id: {talking_photo_id}")
                        return talking_photo_id
                    else:
                        logger.error(f"❌ No look_id/avatar_id in response: {avatars[0]}")
                        logger.error(f"   Available keys: {list(avatars[0].keys())}")
                        return None
                else:
                    logger.error(f"❌ No avatars in group: {data}")
                    return None
            else:
                logger.error(f"❌ Failed to list avatars in group: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get talking_photo_id: {e}")
            return None
    
    def _create_photo_avatar_video(
        self,
        talking_photo_id: str,
        text: str,
        voice_id: str
    ) -> Optional[str]:
        """
        Create video with photo avatar using Create Avatar Video (V2) API.
        
        Uses character.type = "talking_photo" and provides talking_photo_id.
        This is the correct way to create videos with photo avatars.
        """
        try:
            # Create Avatar Video (V2) API endpoint
            url = f"{self.base_url}/video/generate"
            
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Create Avatar Video (V2) payload with talking_photo
            # Based on HeyGen API documentation structure
            payload = {
                "video_inputs": [{
                    "character": {
                        "type": "talking_photo",  # Use talking_photo for photo avatars
                        "talking_photo_id": talking_photo_id
                    },
                    "voice": {
                        "type": "text",
                        "voice_id": voice_id  # Use Juniper voice
                    },
                    "script": {
                        "type": "text",
                        "input": text
                    },
                    "background": {
                        "type": "color",
                        "value": "#FFFFFF"
                    }
                }],
                "dimension": {
                    "width": 512,
                    "height": 512
                },
                "aspect_ratio": "1:1"
            }
            
            logger.info(f"🎬 Creating photo avatar video with Juniper voice...")
            logger.info(f"   Talking photo ID: {talking_photo_id}")
            logger.info(f"   Voice: {voice_id}")
            logger.info(f"   Text: {text[:50]}...")
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    video_id = data.get('data', {}).get('video_id')
                    
                    if video_id:
                        logger.info(f"✅ Photo avatar video job created: {video_id}")
                        return video_id
                    else:
                        logger.error(f"❌ No video_id in response: {data}")
                        return None
                else:
                    logger.error(f"❌ Create photo avatar video error: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Create photo avatar video failed: {e}")
            return None
    
    def _poll_for_video(self, video_id: str, max_attempts: int = 60) -> Optional[str]:
        """Poll for video completion"""
        try:
            url = f"{self.base_url}/video_status.get"
            
            headers = {
                "X-Api-Key": self.api_key
            }
            
            logger.info(f"⏳ Polling for video completion (ID: {video_id})...")
            
            params = {"video_id": video_id}
            
            with httpx.Client(timeout=30.0) as client:
                for attempt in range(max_attempts):
                    time.sleep(3)  # Wait 3 seconds between polls
                    
                    response = client.get(url, params=params, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get('data', {}).get('status')
                        
                        if status == 'completed':
                            video_url = data.get('data', {}).get('video_url')
                            logger.info(f"✅ Video ready! URL: {video_url}")
                            return video_url
                            
                        elif status == 'failed':
                            error_msg = data.get('data', {}).get('error', 'Unknown error')
                            logger.error(f"❌ Generation failed: {error_msg}")
                            return None
                            
                        elif status in ['pending', 'processing']:
                            progress = ((attempt + 1) / max_attempts) * 100
                            logger.info(f"⏳ Processing... {progress:.0f}% ({attempt+1}/{max_attempts})")
                            continue
                            
                        else:
                            logger.warning(f"⚠️  Unknown status: {status}")
                            continue
                    else:
                        logger.error(f"❌ Poll error: {response.status_code}")
                        return None
                
                logger.error("❌ Timeout (3 minutes)")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Polling failed: {e}")
            return None
    
    def _download_video(self, video_url: str) -> Optional[bytes]:
        """Download the generated video"""
        try:
            logger.info(f"📥 Downloading video...")
            
            with httpx.Client(timeout=120.0) as client:
                response = client.get(video_url)
                
                if response.status_code == 200:
                    video_bytes = response.content
                    logger.info(f"✅ Downloaded: {len(video_bytes)} bytes")
                    return video_bytes
                else:
                    logger.error(f"❌ Download error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if HeyGen is available"""
        return self.available


# Global singleton
_heygen_video = None


def get_heygen_video() -> HeyGenVideo:
    """Get the global HeyGen Video instance"""
    global _heygen_video
    if _heygen_video is None:
        _heygen_video = HeyGenVideo()
    return _heygen_video
