#!/usr/bin/env python3
"""
HeyGen Avatar Video API Client

This module provides a Python interface for the HeyGen Avatar Video API v2.
It supports creating videos with avatars, talking photos, AI voices, and dynamic backgrounds.

API Documentation: https://api.heygen.com/v2/video/generate
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class VideoDimension:
    """Video dimensions configuration"""
    width: int = 1280
    height: int = 720


@dataclass
class VideoInput:
    """Video input configuration for a scene"""
    # Avatar settings
    avatar: Optional[str] = None  # Avatar name or ID
    avatar_url: Optional[str] = None  # Avatar image URL
    avatar_image_asset_id: Optional[str] = None  # Avatar image asset ID
    
    # Background settings
    background: Optional[str] = None  # Background URL or color
    background_image_asset_id: Optional[str] = None  # Background image asset ID
    circle_background_color: Optional[str] = None  # Hex color for circle background
    
    # Voice settings
    voice: Optional[str] = None  # Voice name or ID
    voice_url: Optional[str] = None  # Voice audio URL
    audio_url: Optional[str] = None  # Audio URL (alternative to voice_url)
    audio_asset_id: Optional[str] = None  # Audio asset ID
    
    # Script/content
    script: Optional[str] = None  # Text script for the avatar to speak
    title: Optional[str] = None  # Scene title
    
    # Timing
    start_time: Optional[float] = None  # Scene start time in seconds
    duration: Optional[float] = None  # Scene duration in seconds


class HeyGenAvatarVideoClient:
    """Client for HeyGen Avatar Video API v2"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.heygen.com"):
        """
        Initialize the HeyGen Avatar Video client
        
        Args:
            api_key: Your HeyGen API key
            base_url: Base URL for the API (default: https://api.heygen.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-api-key': api_key
        })
    
    def create_video(
        self,
        video_inputs: List[VideoInput],
        caption: bool = False,
        title: Optional[str] = None,
        dimension: Optional[VideoDimension] = None,
        folder_id: Optional[str] = None,
        callback_id: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a video using the HeyGen Avatar Video API
        
        Args:
            video_inputs: List of video input configurations (1-50 scenes)
            caption: Whether to enable captions (text-based input only)
            title: Title of the video
            dimension: Custom video dimensions
            folder_id: Folder ID where video will be stored
            callback_id: Custom ID for callback tracking
            callback_url: URL for completion notification
            
        Returns:
            API response dictionary
            
        Raises:
            ValueError: If parameters are invalid
            requests.RequestException: If API request fails
        """
        # Validate inputs
        if not video_inputs or len(video_inputs) == 0:
            raise ValueError("At least one video input is required")
        
        if len(video_inputs) > 50:
            raise ValueError("Maximum 50 video inputs allowed")
        
        # Build video inputs for API
        api_video_inputs = []
        for i, video_input in enumerate(video_inputs):
            api_input = {}
            
            # Avatar settings
            if video_input.avatar:
                api_input['avatar'] = video_input.avatar
            if video_input.avatar_url:
                api_input['avatar_url'] = video_input.avatar_url
            if video_input.avatar_image_asset_id:
                api_input['avatar_image_asset_id'] = video_input.avatar_image_asset_id
            
            # Background settings
            if video_input.background:
                api_input['background'] = video_input.background
            if video_input.background_image_asset_id:
                api_input['background_image_asset_id'] = video_input.background_image_asset_id
            if video_input.circle_background_color:
                # Validate hex color format
                if not video_input.circle_background_color.startswith('#') or len(video_input.circle_background_color) != 7:
                    raise ValueError(f"Invalid circle_background_color format: {video_input.circle_background_color}. Must be in hex format (#RRGGBB)")
                api_input['circle_background_color'] = video_input.circle_background_color
            
            # Audio/voice settings
            if video_input.voice:
                api_input['voice'] = video_input.voice
            if video_input.voice_url:
                api_input['voice_url'] = video_input.voice_url
            if video_input.audio_url:
                api_input['audio_url'] = video_input.audio_url
            if video_input.audio_asset_id:
                api_input['audio_asset_id'] = video_input.audio_asset_id
            
            # Validate audio requirements
            if not any([video_input.voice, video_input.voice_url, video_input.audio_url, video_input.audio_asset_id]):
                raise ValueError(f"Video input {i+1}: Either voice, voice_url, audio_url, or audio_asset_id must be provided")
            
            # Script/content
            if video_input.script:
                api_input['script'] = video_input.script
            if video_input.title:
                api_input['title'] = video_input.title
            
            # Timing
            if video_input.start_time is not None:
                api_input['start_time'] = video_input.start_time
            if video_input.duration is not None:
                api_input['duration'] = video_input.duration
            
            api_video_inputs.append(api_input)
        
        # Build request payload
        payload = {
            'video_inputs': api_video_inputs,
            'caption': caption
        }
        
        # Add optional parameters
        if title:
            payload['title'] = title
        if dimension:
            payload['dimension'] = {
                'width': dimension.width,
                'height': dimension.height
            }
        if folder_id:
            payload['folder_id'] = folder_id
        if callback_id:
            payload['callback_id'] = callback_id
        if callback_url:
            payload['callback_url'] = callback_url
        
        # Make API request
        url = f"{self.base_url}/v2/video/generate"
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - Status: {e.response.status_code}"
            raise requests.RequestException(error_msg)
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status and details of a video
        
        Args:
            video_id: The ID of the video to check
            
        Returns:
            API response with video status and details
        """
        url = f"{self.base_url}/v1/video_status.get"
        params = {'video_id': video_id}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get video status: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - Status: {e.response.status_code}"
            raise requests.RequestException(error_msg)
    
    def wait_for_video_completion(
        self,
        video_id: str,
        timeout: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for video completion with polling
        
        Args:
            video_id: The ID of the video to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Final video status and details
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_video_status(video_id)
                
                if status.get('status') == 'completed':
                    return status
                elif status.get('status') == 'failed':
                    raise Exception(f"Video generation failed: {status.get('error', 'Unknown error')}")
                
                time.sleep(poll_interval)
                
            except requests.RequestException as e:
                print(f"Error checking video status: {e}")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Video generation timed out after {timeout} seconds")


def main():
    """Example usage of the HeyGen Avatar Video client"""
    
    # Example configuration - replace with your actual API key
    API_KEY = "your-api-key-here"
    
    # Initialize client
    client = HeyGenAvatarVideoClient(api_key=API_KEY)
    
    # Example video input
    video_input = VideoInput(
        avatar="default_avatar",  # Replace with actual avatar name
        script="Hello! This is a test video generated using the HeyGen Avatar Video API.",
        voice="en-US-JennyNeural",  # Replace with actual voice name
        background="#4A90E2"  # Blue background
    )
    
    try:
        # Create video
        print("Creating video...")
        response = client.create_video(
            video_inputs=[video_input],
            title="Test Avatar Video",
            caption=True,
            dimension=VideoDimension(width=1280, height=720)
        )
        
        video_id = response.get('data', {}).get('video_id')
        print(f"Video created with ID: {video_id}")
        
        # Wait for completion
        print("Waiting for video completion...")
        final_status = client.wait_for_video_completion(video_id)
        print(f"Video completed! Status: {final_status.get('status')}")
        
        if final_status.get('video_url'):
            print(f"Video URL: {final_status.get('video_url')}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
