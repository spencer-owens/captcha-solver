---
name: captcha-solver
description: Solve reCAPTCHA challenges using audio transcription (Whisper) or image vision (Gemini). Audio method is faster and more reliable. Use when browser automation encounters a CAPTCHA challenge.
---

# CAPTCHA Solver

Two methods for solving reCAPTCHA:
1. **Audio + Whisper** ⭐ (recommended) - 4 seconds, more reliable
2. **Image + Gemini Vision** - 20-30 seconds, grid detection issues

## Method 1: Audio CAPTCHA (Recommended)

```bash
# Download audio and transcribe
uv run {baseDir}/scripts/solve_audio.py --file <audio.mp3>

# Or directly from URL
uv run {baseDir}/scripts/solve_audio.py --url "<recaptcha_audio_url>"
```

### Workflow

1. Click "Get an audio challenge" button in reCAPTCHA
2. Download MP3 or copy audio URL from "download audio" link
3. Run solver to get transcription
4. Type transcription into text field
5. Click Verify ✓

### Example

```bash
# Download audio
curl -o /tmp/audio.mp3 "https://www.recaptcha.net/recaptcha/api2/payload/audio.mp3?..."

# Transcribe
uv run {baseDir}/scripts/solve_audio.py -f /tmp/audio.mp3
# Output: Transcription: if those users global group

# Type into CAPTCHA and verify
```

## Method 2: Image CAPTCHA (Fallback)

```bash
uv run {baseDir}/scripts/solve.py --image <screenshot.png> --target "<object>"
```

### Options

```bash
# Use flash model for speed (less accurate)
uv run {baseDir}/scripts/solve.py -i captcha.png -t "bicycles" -m gemini-3-flash-preview

# Auto-crop full page screenshot
uv run {baseDir}/scripts/solve.py -i fullpage.png -t "buses" --crop
```

### Position Mapping

```
3x3 grid:        4x4 grid:
[1][2][3]        [1][2][3][4]
[4][5][6]        [5][6][7][8]
[7][8][9]        [9][10][11][12]
                 [13][14][15][16]
```

## Requirements

- Audio: Whisper (auto-installs via uv)
- Image: `GEMINI_API_KEY` env var

## Tips

- **Prefer audio**: Much faster and more reliable than image
- **Whisper tiny is enough**: reCAPTCHA audio is simple
- **Retry on failure**: CAPTCHAs regenerate, just try again
