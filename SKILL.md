---
name: captcha-solver
description: Solve image-based CAPTCHAs (reCAPTCHA, hCaptcha) using Gemini 3 vision. Use when browser automation encounters a CAPTCHA challenge requiring image selection (e.g., "select all squares with bicycles/traffic lights/bridges").
---

# CAPTCHA Solver

Solve grid-based image CAPTCHAs using Gemini 3 Pro vision.

## Quick Start

```bash
uv run {baseDir}/scripts/solve.py --image <screenshot.png> --target "<object>"
```

Example:
```bash
uv run {baseDir}/scripts/solve.py -i captcha.png -t "traffic lights"
# Output: {"positions": [2, 5, 8], "grid_size": "3x3", "confidence": "high"}
```

## Workflow

1. **Screenshot** the CAPTCHA when it appears
2. **Run solver** with the target object from the prompt
3. **Map positions** to DOM refs (buttons are ordered left-to-right, top-to-bottom)
4. **Click** the identified positions
5. **Verify** and repeat if needed

## Position Mapping

Grid positions are numbered left-to-right, top-to-bottom:

```
3x3 grid:        4x4 grid:
[1][2][3]        [1][2][3][4]
[4][5][6]        [5][6][7][8]
[7][8][9]        [9][10][11][12]
                 [13][14][15][16]
```

From a browser snapshot, extract button refs in row order:
```python
# Row 1: refs[0], refs[1], refs[2] → positions 1, 2, 3
# Row 2: refs[3], refs[4], refs[5] → positions 4, 5, 6
# etc.
```

## API Key

Uses `GEMINI_API_KEY` env var or `skills."nano-banana-pro".apiKey` from OpenClaw config.

## Notes

- Always use `gemini-3-pro-preview` — it significantly outperforms 2.x models on CAPTCHAs
- If CAPTCHA fails, screenshot again (images refresh) and retry
- Some CAPTCHAs have fading tiles that refresh after selection — wait briefly between clicks
