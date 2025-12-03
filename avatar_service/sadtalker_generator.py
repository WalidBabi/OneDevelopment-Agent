"""
SadTalker Video Generator - High Quality Integration
"""
import subprocess
import sys
import os
import time
import shutil
from pathlib import Path
import logging
import threading
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class SadTalkerGenerator:
    """High-quality video generation using SadTalker"""
    
    def __init__(self, sadtalker_path=r"C:\Users\Walid\Downloads\SadTalker", quality="fast"):
        """
        Initialize SadTalker generator
        
        Args:
            sadtalker_path: Path to SadTalker installation
            quality: 'fast' | 'standard' (default) | 'high' | 'ultra'
        """
        self.sadtalker_path = Path(sadtalker_path)
        self.python_exe = self.sadtalker_path / "venv310" / "Scripts" / "python.exe"
        self.inference_script = self.sadtalker_path / "inference.py"
        self.quality = quality
        
        # Quality presets - optimized for speed
        self.quality_settings = {
            'fast': {
                'size': '256',
                'enhancer': None,
                'bg_upsampler': None,
                'preprocess': 'crop',  # Fastest preprocessing
                'batch_size': '4',  # Higher batch size for GPU efficiency
                'expected_time': 10,  # Optimized for 10 seconds with GPU
                'description': '256px, no enhancement (fastest - 10s target)'
            },
            'standard': {
                'size': '256',
                'enhancer': 'gfpgan',
                'bg_upsampler': None,
                'expected_time': 30,
                'description': '256px with GFPGAN'
            },
            'high': {
                'size': '512',
                'enhancer': 'gfpgan',
                'bg_upsampler': None,
                'expected_time': 40,
                'description': '512px with GFPGAN (recommended)'
            },
            'ultra': {
                'size': '512',
                'enhancer': 'gfpgan',
                'bg_upsampler': 'realesrgan',
                'expected_time': 60,
                'description': '512px with GFPGAN + RealESRGAN'
            }
        }
        
        if quality not in self.quality_settings:
            raise ValueError(f"Invalid quality: {quality}. Choose from: {list(self.quality_settings.keys())}")
        
        # Verify SadTalker is set up
        if not self.python_exe.exists():
            raise FileNotFoundError(f"SadTalker Python not found: {self.python_exe}")
        
        if not self.inference_script.exists():
            raise FileNotFoundError(f"SadTalker inference.py not found: {self.inference_script}")
        
        logger.info(f"✓ SadTalker initialized: {self.quality_settings[quality]['description']}")
    
    def generate_video(self, 
                      audio_path: str, 
                      image_path: str, 
                      output_dir: str) -> Tuple[bool, Optional[str], float]:
        """
        Generate talking head video
        
        Args:
            audio_path: Path to audio file (MP3/WAV)
            image_path: Path to source image (PNG/JPG)
            output_dir: Directory for output video
            
        Returns:
            tuple: (success: bool, video_path: Optional[str], duration: float)
        """
        settings = self.quality_settings[self.quality]
        
        logger.info(f"🎬 Generating {self.quality} quality video...")
        logger.info(f"   Expected time: ~{settings['expected_time']}s")
        
        # Resolve all paths to absolute, so they work correctly from the SadTalker cwd
        audio_path = Path(audio_path).expanduser().resolve()
        image_path = Path(image_path).expanduser().resolve()
        output_dir = Path(output_dir).expanduser().resolve()
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build command - optimized for maximum speed (10 second target)
        cmd = [
            str(self.python_exe),
            str(self.inference_script),
            "--driven_audio", str(audio_path),
            "--source_image", str(image_path),
            "--result_dir", str(output_dir),
            "--still",  # Less head movement = faster
            "--preprocess", settings.get('preprocess', 'crop'),  # Use crop for speed
            "--size", settings['size'],
            "--batch_size", settings.get('batch_size', '4'),  # Use setting or default to 4
            "--verbose"  # Show detailed output for debugging
            # GPU is controlled via CUDA_VISIBLE_DEVICES env var, not --device flag
        ]
        
        # Only add enhancer if specified (skip for fast mode)
        if settings.get('enhancer'):
            cmd.extend(["--enhancer", settings['enhancer']])
        # For fast mode, explicitly skip enhancer
        elif self.quality == 'fast':
            # Don't add enhancer flag at all - fastest option
            pass
        
        if settings['enhancer']:
            cmd.extend(["--enhancer", settings['enhancer']])
        
        if settings['bg_upsampler']:
            cmd.extend(["--bg_upsampler", settings['bg_upsampler']])
        
        start_time = time.time()
        
        # Parse SadTalker output in real-time to show actual progress
        # SadTalker outputs: "landmark Det:: 100%", "Face Renderer:: 50%", etc.
        current_progress = {'step': 'Initializing', 'percent': 0}
        
        def update_progress(line: str):
            """Parse SadTalker output and extract progress percentage"""
            import re
            line_lower = line.lower()
            
            # Parse Face Renderer progress (the main bottleneck)
            if 'face renderer' in line_lower:
                match = re.search(r'(\d+)%', line)
                if match:
                    percent = int(match.group(1))
                    current_progress['step'] = 'Rendering video frames'
                    current_progress['percent'] = percent
                    return
            
            # Parse other steps
            if 'landmark' in line_lower:
                if '100%' in line:
                    current_progress['step'] = 'Face landmarks detected'
                    current_progress['percent'] = 10
                else:
                    current_progress['step'] = 'Detecting face landmarks'
                    current_progress['percent'] = 5
            elif '3dmm' in line_lower:
                if '100%' in line:
                    current_progress['step'] = '3D motion extracted'
                    current_progress['percent'] = 20
                else:
                    current_progress['step'] = 'Extracting 3D motion'
                    current_progress['percent'] = 15
            elif 'mel' in line_lower and '100%' in line:
                current_progress['step'] = 'Processing audio features'
                current_progress['percent'] = 30
            elif 'audio2exp' in line_lower:
                if '100%' in line:
                    current_progress['step'] = 'Mapping audio to expressions'
                    current_progress['percent'] = 40
                else:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        percent = int(match.group(1))
                        current_progress['step'] = 'Mapping audio to expressions'
                        current_progress['percent'] = 30 + (percent * 0.1)  # 30-40%
        
        def print_progress():
            """Print current progress status"""
            elapsed = time.time() - start_time
            bar_len = 30
            percent = current_progress['percent']
            filled = int(bar_len * percent / 100)
            bar = "█" * filled + "-" * (bar_len - filled)
            sys.stdout.write(
                f"\r[ {bar} ] {current_progress['step']}... {percent:.0f}% ({elapsed:.1f}s)"
            )
            sys.stdout.flush()

        try:
            # Set environment variables to force GPU and FFmpeg
            env = os.environ.copy()
            env['CUDA_VISIBLE_DEVICES'] = '0'  # Force GPU 0 (NVIDIA)
            env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
            env['TORCH_CUDA_ARCH_LIST'] = '8.9'  # RTX 4050 architecture
            env['FORCE_CUDA'] = '1'  # Force CUDA usage
            
            # Set FFmpeg path for pydub (found via search)
            ffmpeg_bin = r"C:\Users\Walid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
            if Path(ffmpeg_bin).exists():
                env['PATH'] = ffmpeg_bin + os.pathsep + env.get('PATH', '')
                # Also set explicit paths for pydub
                env['FFMPEG_BINARY'] = str(Path(ffmpeg_bin) / 'ffmpeg.exe')
                env['FFPROBE_BINARY'] = str(Path(ffmpeg_bin) / 'ffprobe.exe')
            
            # Use Popen to read output in real-time
            process = subprocess.Popen(
                cmd,
                cwd=str(self.sadtalker_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr into stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                env=env  # Pass environment with GPU and FFmpeg settings
            )
            
            # Read output line by line and update progress
            stdout_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stdout_lines.append(output.strip())
                    update_progress(output)
                    print_progress()
            
            # Get return code
            return_code = process.poll()
            stdout_text = '\n'.join(stdout_lines)
            stderr_text = ''  # Already combined with stdout
            
            elapsed = time.time() - start_time
            
            # Clear progress line and show completion
            sys.stdout.write("\r" + " " * 80 + "\r")  # Clear line
            sys.stdout.flush()
            
            if return_code == 0:
            
                # Find generated video
                videos = list(output_dir.glob("**/*.mp4"))
                main_videos = [v for v in videos if "temp" not in v.name.lower()]
                
                if main_videos:
                    video_path = str(main_videos[0].absolute())
                    size_mb = main_videos[0].stat().st_size / (1024 * 1024)
                    
                    logger.info(f"✓ Video generated successfully!")
                    logger.info(f"   Time: {elapsed:.1f}s")
                    logger.info(f"   Size: {size_mb:.2f}MB")
                    logger.info(f"   Path: {video_path}")
                    
                    return True, video_path, elapsed
                else:
                    logger.error("Video generation completed but no video found")
                    logger.debug(f"Stdout: {stdout_text}")
                    return False, None, elapsed
            else:
                # Log full stdout/stderr to make debugging easier
                logger.error(f"SadTalker failed with return code {return_code}")
                logger.error("SadTalker OUTPUT:")
                logger.error(stdout_text)
                return False, None, elapsed

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            logger.error(f"SadTalker timed out after {elapsed:.1f}s (timeout is 600s)")
            return False, None, elapsed

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"SadTalker error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False, None, elapsed

        finally:
            # Ensure progress line is cleared
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test initialization
    generator = SadTalkerGenerator(quality='high')
    
    print(f"✓ SadTalker initialized")
    print(f"  Quality: {generator.quality}")
    print(f"  Expected time: ~{generator.quality_settings[generator.quality]['expected_time']}s")
    
    # Test generation
    success, video, duration = generator.generate_video(
        audio_path="test_luna_audio.mp3",
        image_path="luna_base.png",
        output_dir="test_output"
    )
    
    if success:
        print(f"\n✅ SUCCESS!")
        print(f"   Video: {video}")
        print(f"   Time: {duration:.1f}s")
    else:
        print(f"\n❌ FAILED")

