"""
Download Wav2Lip Model from HuggingFace
This script downloads the model with proper authentication handling
"""
import os
import sys
from pathlib import Path
import requests
from tqdm import tqdm

def download_with_progress(url, output_path, headers=None):
    """Download file with progress bar"""
    print(f"Downloading: {output_path.name}")
    print(f"From: {url}")
    print(f"Size: ~400 MB")
    print("")
    
    try:
        response = requests.get(url, stream=True, timeout=30, headers=headers)
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
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"\n⚠️  Authentication required")
            print(f"   Please download manually from: {url}")
            print(f"   Or create free HuggingFace account and try again")
            return False
        else:
            print(f"\n❌ Download failed: {e}")
            return False
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
    
    # Try multiple sources
    sources = [
        {
            "name": "HuggingFace (numz/wav2lip)",
            "url": "https://huggingface.co/numz/wav2lip/resolve/main/wav2lip_gan.pth",
            "headers": None
        },
        {
            "name": "HuggingFace (alternative)",
            "url": "https://huggingface.co/numz/wav2lip/resolve/main/wav2lip_gan.pth",
            "headers": {"User-Agent": "Mozilla/5.0"}
        },
    ]
    
    print("Attempting automated download from multiple sources...")
    print()
    
    for i, source in enumerate(sources, 1):
        print(f"Trying source {i}/{len(sources)}: {source['name']}")
        if download_with_progress(source['url'], model_path, source['headers']):
            return True
        print()
    
    # If automated fails, provide manual instructions
    print("=" * 70)
    print("⚠️  Automated download failed")
    print("=" * 70)
    print()
    print("MANUAL DOWNLOAD OPTIONS:")
    print()
    print("Option 1: HuggingFace (Free account required)")
    print("  1. Create account: https://huggingface.co/join")
    print("  2. Go to: https://huggingface.co/numz/wav2lip")
    print("  3. Click 'Files and versions' tab")
    print("  4. Download: wav2lip_gan.pth")
    print("  5. Save to:", model_path)
    print()
    print("Option 2: GitHub Releases")
    print("  1. Go to: https://github.com/Rudrabha/Wav2Lip/releases")
    print("  2. Check ALL releases (scroll down)")
    print("  3. Look for .pth files in Assets")
    print("  4. Download checkpoint file")
    print("  5. Rename to: wav2lip_gan.pth")
    print("  6. Save to:", model_path)
    print()
    print("Option 3: Search for mirrors")
    print("  Search: 'wav2lip_gan.pth download mirror'")
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

