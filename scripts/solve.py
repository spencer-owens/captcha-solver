#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
CAPTCHA Solver using Gemini 3 Pro Vision

Usage:
    uv run solve.py --image screenshot.png --target "bicycles"
    uv run solve.py -i captcha.png -t "traffic lights" --json
    uv run solve.py -i fullpage.png -t "buses" --crop  # Auto-crop to CAPTCHA
"""

import argparse
import base64
import io
import json
import os
from pathlib import Path

from google import genai
from PIL import Image


def find_captcha_region(img: Image.Image) -> tuple[int, int, int, int] | None:
    """
    Find the reCAPTCHA grid region in a screenshot.
    Returns (left, top, right, bottom) or None if not found.
    """
    width, height = img.size
    
    # reCAPTCHA grid typically has a distinctive blue header bar
    # and is roughly 400x580 pixels for the challenge dialog
    # Look for the dialog by scanning for the characteristic layout
    
    # Strategy: Look for a rectangular region with the CAPTCHA characteristics
    # The CAPTCHA dialog is usually in the left portion of the screen
    # and has specific dimensions
    
    # For a typical reCAPTCHA v2 challenge:
    # - Dialog width: ~400px
    # - Dialog height: ~580px (with header and footer)
    # - Grid area: ~400x400px
    
    # Scan for potential CAPTCHA regions
    # Look in the left half of the image, middle vertically
    
    # Simple heuristic: CAPTCHA is usually in the left-center area
    # Let's look for it in a reasonable search area
    
    # For full-page screenshots, the CAPTCHA popup is typically:
    # - Left side of screen (around x=50-500)
    # - Vertically centered or slightly above center
    
    # Try to find the blue header bar (RGB around 66, 133, 244 for Google blue)
    pixels = img.load()
    
    # Search for the CAPTCHA by looking for a concentrated rectangular region
    # that could contain the grid
    
    # Fallback: use a reasonable crop region for typical CAPTCHA placement
    # Based on observation, the CAPTCHA dialog usually appears at:
    # - x: 30-450 (left side)
    # - y: 300-900 (middle-ish)
    
    # Let's try a smarter approach: find the largest square-ish region
    # with varied content (the image grid)
    
    # For now, use a heuristic based on typical CAPTCHA placement
    # in browser screenshots (usually lower-left quadrant)
    
    search_left = 0
    search_right = min(500, width)
    search_top = int(height * 0.3)
    search_bottom = int(height * 0.85)
    
    # Return the search region - this captures most CAPTCHA dialogs
    return (search_left, search_top, search_right, search_bottom)


def auto_crop_captcha(img: Image.Image) -> Image.Image:
    """
    Auto-crop a full-page screenshot to just the CAPTCHA region.
    """
    region = find_captcha_region(img)
    if region:
        cropped = img.crop(region)
        return cropped
    return img


def solve_captcha(image_path: str, target: str, auto_crop: bool = False, model: str = "gemini-3-pro-preview") -> dict:
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
    
    img = Image.open(image_path)
    
    # Auto-crop if requested
    if auto_crop:
        img = auto_crop_captcha(img)
    
    # Convert to bytes
    buffer = io.BytesIO()
    img_format = "PNG" if image_path.suffix.lower() == ".png" else "JPEG"
    img.save(buffer, format=img_format)
    image_data = buffer.getvalue()
    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")
    
    # Determine mime type
    mime_type = "image/png" if img_format == "PNG" else "image/jpeg"
    
    # Create client and generate
    client = genai.Client(api_key=api_key)
    
    prompt = f"""You are looking at a reCAPTCHA image challenge. 
    
Find the grid of image tiles and identify all squares containing "{target}".

The grid is typically 3x3 (9 squares) or 4x4 (16 squares).
Grid positions are numbered left-to-right, top-to-bottom:

3x3 grid:
[1][2][3]
[4][5][6]
[7][8][9]

4x4 grid:
[1][2][3][4]
[5][6][7][8]
[9][10][11][12]
[13][14][15][16]

Look carefully at each tile. Include tiles where the object is even partially visible.

If you cannot find any {target} in the grid, return empty positions.

Respond with ONLY this JSON (no other text):
{{"positions": [list of numbers], "grid_size": "3x3" or "4x4", "confidence": "high" or "medium" or "low"}}"""

    try:
        response = client.models.generate_content(
            model=model,
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
    parser.add_argument("--crop", "-c", action="store_true", help="Auto-crop to CAPTCHA region")
    parser.add_argument("--model", "-m", default="gemini-3-pro-preview", 
                        help="Gemini model (default: gemini-3-pro-preview, alt: gemini-3-flash-preview)")
    
    args = parser.parse_args()
    result = solve_captcha(args.image, args.target, auto_crop=args.crop, model=args.model)
    
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
