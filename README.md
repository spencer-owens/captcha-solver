# CAPTCHA Solver

Solve grid-based image CAPTCHAs (reCAPTCHA, hCaptcha) using Gemini 3 Pro vision.

## Why?

Because paying humans to solve CAPTCHAs is lame. Let the robots handle it.

## Quick Start

```bash
uv run scripts/solve.py --image screenshot.png --target "bicycles"
```

Output:
```json
{"positions": [2, 5, 8], "grid_size": "3x3", "confidence": "high"}
```

## Requirements

- Python 3.10+
- `GEMINI_API_KEY` environment variable (get one at [aistudio.google.com](https://aistudio.google.com))

### Install

**Option A: uv (recommended)** - zero setup, deps auto-install:
```bash
uv run scripts/solve.py -i captcha.png -t "bicycles"
```

**Option B: pip**
```bash
pip install -r requirements.txt
python scripts/solve.py -i captcha.png -t "bicycles"
```

## Usage

1. **Screenshot** the CAPTCHA when it appears
2. **Run solver** with the target object from the prompt
3. **Map positions** to your automation framework's element refs
4. **Click** the identified positions
5. **Verify** and repeat if needed (some CAPTCHAs have fading/refreshing tiles)

### Position Mapping

Grid positions are numbered left-to-right, top-to-bottom:

```
3x3 grid:        4x4 grid:
[1][2][3]        [1] [2] [3] [4]
[4][5][6]        [5] [6] [7] [8]
[7][8][9]        [9] [10][11][12]
                 [13][14][15][16]
```

## Notes

- Uses `gemini-3-pro-preview` — significantly outperforms older models on visual recognition
- Works with partial object visibility (e.g., half a bicycle counts)
- If verification fails, screenshot again (images refresh) and retry

## License

MIT
