"""
Download Wav2Lip Model - Automated Script
Downloads wav2lip_gan.pth (~400MB) for fast video generation
"""
import os
import sys
from pathlib import Path
import requests
from tqdm import tqdm

def download_file(url, output_path):
    """Download file with progress bar"""
    print(f"Downloading: {output_path.name}")
    print(f"From: {url}")
    print(f"Size: ~400 MB")
    print("")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            desc="Progress",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Download complete!")
        print(f"  File: {output_path}")
        print(f"  Size: {file_size:.2f} MB")
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

def main():
    # Setup paths
    checkpoints_dir = Path(r"C:\Users\Walid\Downloads\Wav2Lip\checkpoints")
    model_path = checkpoints_dir / "wav2lip_gan.pth"
    
    # Create directory
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already exists
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            print(f"✓ Model already exists: {size_mb:.2f} MB")
            print("  No download needed!")
            return True
        else:
            print(f"⚠️  Existing file too small ({size_mb:.2f} MB), re-downloading...")
            model_path.unlink()
    
    print("=" * 70)
    print("📥 Wav2Lip Model Downloader")
    print("=" * 70)
    print()
    
    # Try multiple download sources
    urls = [
        # Try GitHub releases first
        "https://github.com/Rudrabha/Wav2Lip/releases/download/v0.0.1/wav2lip_gan.pth",
        # Alternative: Direct from repository
        "https://github.com/Rudrabha/Wav2Lip/raw/master/checkpoints/wav2lip_gan.pth",
    ]
    
    print("Attempting automated download...")
    print()
    
    for i, url in enumerate(urls, 1):
        print(f"Trying source {i}/{len(urls)}...")
        if download_file(url, model_path):
            return True
        print()
    
    # If automated fails, provide manual instructions
    print("=" * 70)
    print("⚠️  Automated download failed")
    print("=" * 70)
    print()
    print("Please download manually:")
    print()
    print("1. Open browser and go to:")
    print("   https://github.com/Rudrabha/Wav2Lip/releases")
    print()
    print("2. Look for 'wav2lip_gan.pth' (~400MB)")
    print("   Or try: https://drive.google.com/file/d/1FWhIZQKjLQjXFR1Kh8dKJ_xT4l8Xv0jQ/view")
    print()
    print("3. Download the file")
    print()
    print("4. Save to:")
    print(f"   {model_path}")
    print()
    print("After downloading, restart the avatar server!")
    print()
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

