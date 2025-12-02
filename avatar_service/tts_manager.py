"""
TTS Manager - Multiple High-Quality TTS Engines
Supports: edge-tts, Piper, Coqui TTS, with automatic fallback
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional
import tempfile

logger = logging.getLogger(__name__)


class TTSManager:
    """Manages multiple TTS engines with automatic fallback"""
    
    def __init__(self):
        self.engines = []
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize available TTS engines in priority order"""
        
        # 1. Try edge-tts (Microsoft - Best quality/speed balance)
        try:
            import edge_tts
            self.engines.append(('edge-tts', self._generate_edge_tts))
            logger.info("✓ edge-tts available (Microsoft Neural Voices)")
        except ImportError:
            logger.warning("edge-tts not available. Install with: pip install edge-tts")
        
        # 2. Try Piper (Fast, offline)
        try:
            import piper
            self.engines.append(('piper', self._generate_piper))
            logger.info("✓ Piper TTS available")
        except ImportError:
            logger.warning("Piper not available. Install with: pip install piper-tts")
        
        # 3. Try Coqui TTS (Voice cloning)
        try:
            from TTS.api import TTS
            self.engines.append(('coqui', self._generate_coqui))
            logger.info("✓ Coqui TTS available")
        except ImportError:
            logger.warning("Coqui TTS not available. Install with: pip install TTS")
        
        # 4. Fallback to gTTS (Always available)
        try:
            from gtts import gTTS
            self.engines.append(('gtts', self._generate_gtts))
            logger.info("✓ gTTS available (fallback)")
        except ImportError:
            logger.error("No TTS engines available!")
    
    async def generate_speech(self, text: str, output_path: str, voice: str = "default") -> bool:
        """
        Generate speech from text using the best available engine
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice: Voice identifier (engine-specific)
        
        Returns:
            bool: True if successful, False otherwise
        """
        for engine_name, engine_func in self.engines:
            try:
                logger.info(f"Trying {engine_name}...")
                await engine_func(text, output_path, voice)
                logger.info(f"✓ Speech generated successfully with {engine_name}")
                return True
            except Exception as e:
                logger.warning(f"{engine_name} failed: {e}")
                continue
        
        logger.error("All TTS engines failed!")
        return False
    
    # ==================== TTS Engine Implementations ====================
    
    async def _generate_edge_tts(self, text: str, output_path: str, voice: str):
        """Microsoft Edge TTS - High quality, fast"""
        import edge_tts
        
        # Voice selection
        voice_map = {
            "default": "en-US-AriaNeural",  # Young, friendly female
            "professional": "en-US-JennyNeural",  # Professional, warm
            "british": "en-GB-SoniaNeural",  # British, sophisticated
            "casual": "en-US-MichelleNeural",  # Casual, energetic
        }
        
        selected_voice = voice_map.get(voice, "en-US-AriaNeural")
        
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(output_path)
    
    async def _generate_piper(self, text: str, output_path: str, voice: str):
        """Piper TTS - Fast, offline"""
        # Note: Piper requires model files to be downloaded
        # This is a placeholder - actual implementation depends on your Piper setup
        import subprocess
        
        # Assuming piper is installed and in PATH
        cmd = [
            "piper",
            "--model", "en_US-lessac-medium",  # High-quality English model
            "--output_file", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate(input=text.encode())
        
        if process.returncode != 0:
            raise Exception(f"Piper failed with code {process.returncode}")
    
    async def _generate_coqui(self, text: str, output_path: str, voice: str):
        """Coqui TTS - Voice cloning capable"""
        from TTS.api import TTS
        
        # Initialize TTS model (do this once in __init__ for production)
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        
        # Generate speech
        tts.tts_to_file(text=text, file_path=output_path)
    
    async def _generate_gtts(self, text: str, output_path: str, voice: str):
        """Google TTS - Fallback option"""
        from gtts import gTTS
        
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)


# Singleton instance
_tts_manager = None

def get_tts_manager() -> TTSManager:
    """Get the global TTS manager instance"""
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager

