# CAPTCHA Solver

Solve reCAPTCHA and hCaptcha challenges using AI. Two methods available:

1. **Audio CAPTCHA + Whisper** ⭐ (recommended) - faster and more reliable
2. **Image CAPTCHA + Gemini Vision** - for when audio isn't available

## Why?

Because paying humans to solve CAPTCHAs is lame. Let the robots handle it.

---

## Method 1: Audio CAPTCHA (Recommended)

Uses OpenAI Whisper to transcribe reCAPTCHA audio challenges. Faster and more reliable than image-based solving.

### Quick Start

```bash
# From downloaded audio file
uv run scripts/solve_audio.py --file captcha_audio.mp3

# From reCAPTCHA audio URL  
uv run scripts/solve_audio.py --url "https://www.recaptcha.net/recaptcha/api2/payload/audio.mp3?..."
```

Output:
```
Transcription: if those users global group
Model: tiny
```

### Workflow

1. Click "Get an audio challenge" button on reCAPTCHA
2. Download the MP3 (or grab the audio URL)
3. Run solver to get transcription
4. Type transcription into the text field
5. Click Verify ✓

### Model Selection

```bash
# Fastest (recommended for CAPTCHAs)
uv run scripts/solve_audio.py -f audio.mp3 -m tiny

# More accurate if tiny fails
uv run scripts/solve_audio.py -f audio.mp3 -m base
```

| Model | Speed | Accuracy | Size |
|-------|-------|----------|------|
| tiny | ~4s | Good | 39MB |
| base | ~10s | Better | 74MB |
| small | ~30s | Best | 244MB |

---

## Method 2: Image CAPTCHA (Gemini Vision)

Uses Gemini 3 Pro vision to identify objects in grid-based image CAPTCHAs.

### Quick Start

```bash
uv run scripts/solve.py --image screenshot.png --target "bicycles"
```

Output:
```json
{"positions": [2, 5, 8], "grid_size": "3x3", "confidence": "high"}
```

### Options

```bash
# Use faster flash model (less accurate)
uv run scripts/solve.py -i captcha.png -t "traffic lights" -m gemini-3-flash-preview

# Auto-crop full page screenshot to CAPTCHA region
uv run scripts/solve.py -i fullpage.png -t "buses" --crop

# JSON output
uv run scripts/solve.py -i captcha.png -t "bicycles" --json
```

### Position Mapping

Grid positions are numbered left-to-right, top-to-bottom:

```
3x3 grid:        4x4 grid:
[1][2][3]        [1] [2] [3] [4]
[4][5][6]        [5] [6] [7] [8]
[7][8][9]        [9] [10][11][12]
                 [13][14][15][16]
```

---

## Requirements

- Python 3.10+
- For audio: Whisper (auto-installs via uv)
- For image: `GEMINI_API_KEY` environment variable

### Install

**uv (recommended)** - zero setup, deps auto-install:
```bash
uv run scripts/solve_audio.py -f audio.mp3
uv run scripts/solve.py -i captcha.png -t "bicycles"
```

**pip:**
```bash
pip install -r requirements.txt
pip install openai-whisper  # for audio
```

---

## Tips

- **Audio is faster**: Image API calls take ~20-30s vs ~4s for Whisper
- **Audio is more reliable**: No grid size detection issues
- **Whisper tiny is enough**: reCAPTCHA audio is simple digits/words
- **Screenshot full page**: Use `--crop` flag to auto-find CAPTCHA region
- **Retry on failure**: CAPTCHAs refresh images, just screenshot again

## License

MIT
