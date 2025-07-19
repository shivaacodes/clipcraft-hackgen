#!/usr/bin/env python3
"""
Simple script to start the video processing server with proper setup.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import fastapi
        import uvicorn
        import anthropic
        import moviepy
        print("✓ Python requirements satisfied")
        return True
    except ImportError as e:
        print(f"✗ Missing Python package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_whisper_cpp():
    """Check if whisper.cpp is available."""
    whisper_paths = [
        "whisper",  # In PATH
        "/usr/local/bin/whisper",
        "/opt/homebrew/bin/whisper",
        "~/whisper.cpp/main"  # Common build location
    ]
    
    for path in whisper_paths:
        try:
            expanded_path = os.path.expanduser(path)
            result = subprocess.run([expanded_path, "--help"], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ Found whisper.cpp at: {expanded_path}")
                return expanded_path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("✗ whisper.cpp not found")
    print("Install instructions:")
    print("1. git clone https://github.com/ggerganov/whisper.cpp.git")
    print("2. cd whisper.cpp && make")
    print("3. Add to PATH or set WHISPER_EXECUTABLE=/path/to/whisper.cpp/main")
    return None

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if not env_path.exists():
        if env_example_path.exists():
            print("✗ .env file not found")
            print("Copy .env.example to .env and configure your API keys:")
            print(f"cp {env_example_path} {env_path}")
        else:
            print("✗ No .env file found")
        return False
    
    # Check for required variables
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = []
    
    with open(env_path) as f:
        env_content = f.read()
        for var in required_vars:
            if f"{var}=" not in env_content or f"{var}=your_" in env_content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing or placeholder values in .env: {missing_vars}")
        return False
    
    print("✓ .env file configured")
    return True

def main():
    """Main setup and startup function."""
    print("🎬 Video Processing Server Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check whisper.cpp
    whisper_path = check_whisper_cpp()
    if whisper_path is None:
        print("\n⚠️  Server will start but video processing may fail without whisper.cpp")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    print("\n✓ All checks passed!")
    print("Starting server...")
    print("=" * 40)
    
    # Set whisper path if found
    if whisper_path and whisper_path != "whisper":
        os.environ["WHISPER_EXECUTABLE"] = whisper_path
    
    # Unset conflicting Google environment variables
    if "GOOGLE_CLIENT_ID" in os.environ:
        del os.environ["GOOGLE_CLIENT_ID"]
    if "GOOGLE_CLIENT_SECRET" in os.environ:
        del os.environ["GOOGLE_CLIENT_SECRET"]

    # Start server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()