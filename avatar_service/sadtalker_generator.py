"""
SadTalker Generator - High-Quality Talking Avatar Videos
=========================================================
Generates photorealistic talking-head videos using SadTalker.
Supports both TTS generation and pre-generated audio.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict
import asyncio

logger = logging.getLogger(__name__)


class SadTalkerGenerator:
    """
    Wrapper for SadTalker video generation.
    Supports both audio file input and text-to-speech generation.
    """
    
    def __init__(self, sadtalker_path: Optional[Path] = None):
        """
        Initialize SadTalker generator.
        
        Args:
            sadtalker_path: Path to SadTalker installation (auto-detected if None)
        """
        self.sadtalker_path = sadtalker_path or self._find_sadtalker()
        self.tts_manager = None
        
        if not self.sadtalker_path or not self.sadtalker_path.exists():
            raise Exception(f"SadTalker not found at: {self.sadtalker_path}")
        
        logger.info(f"SadTalker found at: {self.sadtalker_path}")
        
        # Initialize TTS manager for fallback
        try:
            from tts_manager import get_tts_manager
            self.tts_manager = get_tts_manager()
            logger.info("✓ TTS Manager initialized")
        except Exception as e:
            logger.warning(f"TTS Manager not available: {e}")
    
    def _find_sadtalker(self) -> Optional[Path]:
        """Auto-detect SadTalker installation"""
        possible_paths = [
            Path("C:/Users/Walid/Downloads/SadTalker"),
            Path("C:/SadTalker"),
            Path.home() / "SadTalker",
            Path("../SadTalker"),
            Path("./SadTalker"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "inference.py").exists():
                return path
        
        return None
    
    def generate(
        self,
        text: Optional[str] = None,
        audio_path: Optional[str] = None,
        source_image: str = None,
        video_id: str = None,
        quality: str = "fast",
        output_dir: str = None,
        audio_dir: str = None,
        temp_dir: str = None,
    ) -> Dict:
        """
        Generate talking avatar video.
        
        Args:
            text: Text to convert to speech (if no audio_path provided)
            audio_path: Path to pre-generated audio file (takes priority over text)
            source_image: Path to source avatar image
            video_id: Unique identifier for this video
            quality: 'fast', 'standard', or 'high'
            output_dir: Where to save final video
            audio_dir: Where to save generated audio
            temp_dir: Temporary working directory
        
        Returns:
            dict with 'video_path', 'audio_path', 'duration'
        """
        
        output_dir = Path(output_dir)
        audio_dir = Path(audio_dir)
        temp_dir = Path(temp_dir) / video_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("============================================================")
        logger.info("🎙️  TTS Progress:")
        logger.info(f"   Text length: {len(text) if text else 'N/A (using audio_path)'} characters")
        
        # Step 1: Get audio file
        if audio_path and Path(audio_path).exists():
            # Use provided audio file
            logger.info(f"✓ Using provided audio: {audio_path}")
            final_audio_path = Path(audio_path)
        elif text:
            # Generate audio with TTS
            logger.info("🎤 Generating audio with TTS...")
            final_audio_path = audio_dir / f"{video_id}.mp3"
            
            # Use TTS manager if available
            if self.tts_manager:
                success = asyncio.run(self.tts_manager.generate_speech(
                    text=text,
                    output_path=str(final_audio_path),
                    voice="default"
                ))
                if not success:
                    raise Exception("TTS generation failed")
            else:
                # Fallback to gTTS
                from gtts import gTTS
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(str(final_audio_path))
            
            logger.info(f"✓ Audio generated: {final_audio_path}")
        else:
            raise ValueError("Either 'text' or 'audio_path' must be provided")
        
        # Get audio duration
        try:
            from mutagen.mp3 import MP3
            audio_info = MP3(str(final_audio_path))
            duration = audio_info.info.length
            logger.info(f"   Estimated duration: ~{duration:.1f}s")
        except:
            # Fallback: estimate from text
            if text:
                words = len(text.split())
                duration = (words / 150) * 60  # 150 words per minute
            else:
                duration = 5.0
        
        logger.info("============================================================")
        logger.info(f"🎬 Generating {quality} quality video...")
        
        # Step 2: Generate video with SadTalker
        video_path = self._run_sadtalker(
            audio_path=final_audio_path,
            source_image=Path(source_image),
            temp_dir=temp_dir,
            output_dir=output_dir,
            video_id=video_id,
            quality=quality
        )
        
        logger.info("============================================================")
        logger.info(f"✓ Video ready: {video_id}.mp4")
        
        return {
            'video_path': str(video_path),
            'audio_path': str(final_audio_path),
            'duration': duration,
            'status': 'success'
        }
    
    def _run_sadtalker(
        self,
        audio_path: Path,
        source_image: Path,
        temp_dir: Path,
        output_dir: Path,
        video_id: str,
        quality: str
    ) -> Path:
        """
        Run SadTalker inference.
        """
        
        logger.info("============================================================")
        logger.info("📊 SadTalker Progress (live):")
        logger.info("============================================================")
        logger.info("GPU Configuration for SadTalker:")
        logger.info(f"  CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', '0')}")
        logger.info(f"  Device: cuda")
        
        # Quality settings
        quality_settings = {
            "fast": {
                "size": 256,
                "preprocess": "crop",
                "still": True,
                "enhancer": None
            },
            "standard": {
                "size": 256,
                "preprocess": "full",
                "still": False,
                "enhancer": "gfpgan"
            },
            "high": {
                "size": 512,
                "preprocess": "full",
                "still": False,
                "enhancer": "gfpgan"
            }
        }
        
        settings = quality_settings.get(quality, quality_settings["fast"])
        
        # Build command
        python_exe = sys.executable
        
        # Try to use SadTalker's venv if it exists
        venv_python = self.sadtalker_path / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_exe = str(venv_python)
        
        cmd = [
            python_exe,
            "inference.py",
            "--driven_audio", str(audio_path.absolute()),
            "--source_image", str(source_image.absolute()),
            "--result_dir", str(temp_dir.absolute()),
            "--size", str(settings["size"]),
            "--preprocess", settings["preprocess"],
        ]
        
        if settings["still"]:
            cmd.append("--still")
        
        if settings["enhancer"]:
            cmd.extend(["--enhancer", settings["enhancer"]])
        
        # Run SadTalker
        logger.info(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=str(self.sadtalker_path),
            capture_output=False,  # Let output stream to console
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"SadTalker failed with exit code {result.returncode}")
        
        # Find the generated video
        generated_videos = list(temp_dir.rglob("*.mp4"))
        if not generated_videos:
            raise Exception("SadTalker did not generate any video")
        
        # Get the most recent video
        latest_video = max(generated_videos, key=lambda p: p.stat().st_mtime)
        
        # Move to output directory with correct name
        final_path = output_dir / f"{video_id}.mp4"
        
        if latest_video != final_path:
            import shutil
            shutil.copy2(latest_video, final_path)
        
        logger.info(f"The generated video is named: {latest_video}")
        logger.info(f"The generated video is named: {final_path}")
        
        return final_path


# Singleton instance
_generator = None

def get_sadtalker_generator() -> SadTalkerGenerator:
    """Get global SadTalker generator instance"""
    global _generator
    if _generator is None:
        _generator = SadTalkerGenerator()
    return _generator

