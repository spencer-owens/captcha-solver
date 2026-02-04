#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai-whisper>=20231117",
# ]
# ///
"""
Audio CAPTCHA Solver using Whisper

Solves reCAPTCHA audio challenges by transcribing with OpenAI Whisper.
This is faster and more reliable than image-based solving.

Usage:
    # From URL (reCAPTCHA audio download link)
    uv run solve_audio.py --url "https://www.recaptcha.net/recaptcha/api2/payload/audio.mp3?..."
    
    # From local file
    uv run solve_audio.py --file /tmp/captcha_audio.mp3
    
    # Specify model (tiny is fastest, base/small for accuracy)
    uv run solve_audio.py --file audio.mp3 --model base
    
    # JSON output for scripting
    uv run solve_audio.py --file audio.mp3 --json
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def download_audio(url: str, output_path: Path) -> bool:
    """Download audio file from URL using curl."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", str(output_path), url],
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0 and output_path.exists()
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return False


def transcribe_audio(audio_path: Path, model: str = "tiny") -> dict:
    """Transcribe audio using Whisper."""
    try:
        import whisper
        
        # Load model (downloads on first use)
        whisper_model = whisper.load_model(model)
        
        # Transcribe
        result = whisper_model.transcribe(
            str(audio_path),
            language="en",
            fp16=False  # CPU compatibility
        )
        
        text = result.get("text", "").strip()
        
        return {
            "transcription": text,
            "model": model,
            "success": bool(text)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def solve_audio_captcha(url: str = None, file_path: str = None, model: str = "tiny") -> dict:
    """
    Solve audio CAPTCHA by transcribing with Whisper.
    
    Args:
        url: reCAPTCHA audio download URL
        file_path: Path to local audio file
        model: Whisper model (tiny|base|small|medium|large)
    
    Returns:
        dict with transcription or error
    """
    if not url and not file_path:
        return {"error": "Must provide either --url or --file", "success": False}
    
    audio_path = None
    temp_file = None
    
    try:
        if url:
            # Download to temp file
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            audio_path = Path(temp_file.name)
            temp_file.close()
            
            if not download_audio(url, audio_path):
                return {"error": "Failed to download audio", "success": False}
        else:
            audio_path = Path(file_path)
            if not audio_path.exists():
                return {"error": f"File not found: {file_path}", "success": False}
        
        # Transcribe
        return transcribe_audio(audio_path, model)
        
    finally:
        # Cleanup temp file
        if temp_file and Path(temp_file.name).exists():
            Path(temp_file.name).unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Solve audio CAPTCHA using Whisper transcription"
    )
    parser.add_argument("--url", "-u", help="reCAPTCHA audio download URL")
    parser.add_argument("--file", "-f", help="Path to local audio file")
    parser.add_argument(
        "--model", "-m", 
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: tiny, fastest)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    
    args = parser.parse_args()
    
    if not args.url and not args.file:
        parser.error("Must provide either --url or --file")
    
    result = solve_audio_captcha(
        url=args.url,
        file_path=args.file,
        model=args.model
    )
    
    if args.json:
        print(json.dumps(result))
    else:
        if result.get("success"):
            print(f"Transcription: {result['transcription']}")
            print(f"Model: {result['model']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
