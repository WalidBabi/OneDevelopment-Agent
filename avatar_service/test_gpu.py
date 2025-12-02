"""
Quick GPU Test Script
Run this to verify your RTX 4050 is detected and working
"""

import sys

def test_gpu():
    print("=" * 50)
    print("Luna Avatar Service - GPU Test")
    print("=" * 50)
    print()
    
    # Test 1: PyTorch
    print("[1/3] Testing PyTorch...")
    try:
        import torch
        print(f"✓ PyTorch installed: {torch.__version__}")
    except ImportError:
        print("✗ PyTorch not installed!")
        print("\nInstall with:")
        print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False
    
    print()
    
    # Test 2: CUDA
    print("[2/3] Testing CUDA...")
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.version.cuda}")
        print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"✓ GPU memory: {props.total_memory / 1024**3:.2f} GB")
        print(f"✓ Compute capability: {props.major}.{props.minor}")
    else:
        print("✗ CUDA not available!")
        print("\nPossible issues:")
        print("1. CUDA Toolkit not installed")
        print("2. PyTorch installed without CUDA support")
        print("3. NVIDIA drivers outdated")
        return False
    
    print()
    
    # Test 3: Simple GPU operation
    print("[3/3] Testing GPU computation...")
    try:
        x = torch.randn(1000, 1000).cuda()
        y = torch.randn(1000, 1000).cuda()
        z = torch.matmul(x, y)
        print(f"✓ GPU computation successful!")
        print(f"✓ Result shape: {z.shape}")
        
        # Memory check
        allocated = torch.cuda.memory_allocated(0) / 1024**2
        reserved = torch.cuda.memory_reserved(0) / 1024**2
        print(f"✓ Memory allocated: {allocated:.2f} MB")
        print(f"✓ Memory reserved: {reserved:.2f} MB")
    except Exception as e:
        print(f"✗ GPU computation failed: {e}")
        return False
    
    print()
    print("=" * 50)
    print("✓ All tests passed! Your GPU is ready.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_gpu()
    sys.exit(0 if success else 1)

