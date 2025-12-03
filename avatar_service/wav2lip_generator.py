"""
Wav2Lip Video Generator - Fast Production Integration
Ultra-fast talking head videos (15-20 seconds)
"""
import subprocess
import sys
import time
import shutil
from pathlib import Path
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class Wav2LipGenerator:
    """Fast video generation using Wav2Lip (15-20 seconds)"""
    
    def __init__(self, wav2lip_path=r"C:\Users\Walid\Downloads\Wav2Lip"):
        """
        Initialize Wav2Lip generator
        
        Args:
            wav2lip_path: Path to Wav2Lip installation
        """
        self.wav2lip_path = Path(wav2lip_path)
        self.python_exe = self.wav2lip_path / "venv" / "Scripts" / "python.exe"
        self.inference_script = self.wav2lip_path / "inference.py"
        self.checkpoint = self.wav2lip_path / "checkpoints" / "wav2lip_gan.pth"
        
        # Verify installation
        if not self.python_exe.exists():
            raise FileNotFoundError(f"Wav2Lip Python not found: {self.python_exe}")
        
        if not self.inference_script.exists():
            raise FileNotFoundError(f"Wav2Lip inference.py not found: {self.inference_script}")
        
        if not self.checkpoint.exists():
            raise FileNotFoundError(f"Wav2Lip model not found: {self.checkpoint}")
        
        logger.info("✓ Wav2Lip initialized (fast mode: 15-20s per video)")
    
    def generate_video(self, 
                      audio_path: str, 
                      image_path: str, 
                      output_path: str,
                      quality='high') -> Tuple[bool, Optional[str], float]:
        """
        Generate talking head video with Wav2Lip
        
        Args:
            audio_path: Path to audio file (MP3/WAV)
            image_path: Path to source image (PNG/JPG)
            output_path: Path for output video
            quality: 'fast' (8-12s, lower res) or 'high' (15-20s, full res)
            
        Returns:
            tuple: (success: bool, video_path: Optional[str], duration: float)
        """
        logger.info(f"⚡ Generating video with Wav2Lip ({quality} quality)...")
        logger.info(f"   Expected time: ~15-20 seconds")
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            str(self.python_exe),
            str(self.inference_script),
            "--checkpoint_path", str(self.checkpoint),
            "--face", str(image_path),
            "--audio", str(audio_path),
            "--outfile", str(output_path),
        ]
        
        # Quality settings
        if quality == 'fast':
            cmd.extend(["--resize_factor", "2"])  # Half resolution for speed
            cmd.append("--nosmooth")
        else:  # high quality
            cmd.extend(["--resize_factor", "1"])  # Full resolution
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.wav2lip_path),
                capture_output=True,
                text=True,
                timeout=60  # 1 minute max
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0 and Path(output_path).exists():
                size_mb = Path(output_path).stat().st_size / (1024 * 1024)
                
                logger.info(f"✓ Video generated successfully!")
                logger.info(f"   Time: {elapsed:.1f}s")
                logger.info(f"   Size: {size_mb:.2f}MB")
                logger.info(f"   Path: {output_path}")
                
                return True, str(output_path), elapsed
            else:
                logger.error(f"Wav2Lip failed with return code {result.returncode}")
                logger.error(f"Error: {result.stderr[:500]}")
                return False, None, elapsed
                
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            logger.error(f"Wav2Lip timed out after {elapsed:.1f}s")
            return False, None, elapsed
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Wav2Lip error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False, None, elapsed


# Singleton instance
_generator = None

def get_wav2lip_generator():
    """Get or create Wav2Lip generator instance"""
    global _generator
    if _generator is None:
        _generator = Wav2LipGenerator()
    return _generator


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("Testing Wav2Lip Generator")
    print("=" * 70)
    print()
    
    # Test initialization
    try:
        generator = Wav2LipGenerator()
        print("✓ Wav2Lip initialized successfully")
        print()
        
        # Test generation
        test_audio = r"C:\Users\Walid\Downloads\Wav2Lip\test_luna_audio.mp3"
        test_image = r"C:\Users\Walid\Downloads\Wav2Lip\luna_base.png"
        test_output = r"C:\Users\Walid\Downloads\Wav2Lip\results\test_output.mp4"
        
        if Path(test_audio).exists() and Path(test_image).exists():
            print("Running test generation...")
            print()
            
            success, video, duration = generator.generate_video(
                audio_path=test_audio,
                image_path=test_image,
                output_path=test_output,
                quality='high'
            )
            
            if success:
                print()
                print("=" * 70)
                print("✅ TEST PASSED!")
                print("=" * 70)
                print(f"   Video: {video}")
                print(f"   Time: {duration:.1f}s")
                print()
                print("Opening video...")
                subprocess.run(["start", video], shell=True)
            else:
                print("\n❌ TEST FAILED")
        else:
            print("⚠️  Test files not found, skipping test")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

