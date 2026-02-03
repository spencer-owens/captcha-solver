#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
# ]
# ///
"""
CAPTCHA Solver using Gemini 3 Pro Vision

Usage:
    uv run solve.py --image screenshot.png --target "bicycles"
    uv run solve.py -i captcha.png -t "traffic lights" --json
"""

import argparse
import base64
import json
import os
from pathlib import Path

from google import genai


def solve_captcha(image_path: str, target: str) -> dict:
    """Analyze CAPTCHA image and return positions containing target."""
    
    # Get API key from env or OpenClaw config
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            api_key = config.get("skills", {}).get("nano-banana-pro", {}).get("apiKey")
    
    if not api_key:
        return {"error": "No GEMINI_API_KEY found"}
    
    # Load image
    image_path = Path(image_path)
    if not image_path.exists():
        return {"error": f"Image not found: {image_path}"}
    
    image_data = image_path.read_bytes()
    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")
    
    # Determine mime type
    suffix = image_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    
    # Create client and generate
    client = genai.Client(api_key=api_key)
    
    prompt = f"""Analyze this CAPTCHA image. Find all grid squares containing "{target}".

Grid positions (left-to-right, top-to-bottom):
3x3: [1][2][3] / [4][5][6] / [7][8][9]
4x4: [1][2][3][4] / [5][6][7][8] / [9][10][11][12] / [13][14][15][16]

Examine each square carefully. Include squares where the object is partially visible.

Respond with ONLY this JSON (no other text):
{{"positions": [numbers], "grid_size": "3x3" or "4x4", "confidence": "high" or "medium" or "low"}}"""

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                prompt,
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_b64,
                    }
                }
            ],
        )
        
        text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": text, "error": "Could not parse JSON"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Solve CAPTCHA using Gemini 3 Vision")
    parser.add_argument("--image", "-i", required=True, help="Path to CAPTCHA screenshot")
    parser.add_argument("--target", "-t", required=True, help="Object to find (e.g., 'bicycles')")
    parser.add_argument("--json", action="store_true", help="Output raw JSON only")
    
    args = parser.parse_args()
    result = solve_captcha(args.image, args.target)
    
    if args.json:
        print(json.dumps(result))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            if "raw_response" in result:
                print(f"Raw: {result['raw_response']}")
        else:
            positions = result.get("positions", [])
            grid = result.get("grid_size", "unknown")
            confidence = result.get("confidence", "unknown")
            print(f"Target: {args.target}")
            print(f"Grid: {grid}")
            print(f"Positions: {positions}")
            print(f"Confidence: {confidence}")


if __name__ == "__main__":
    main()
