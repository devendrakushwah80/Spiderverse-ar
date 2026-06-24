# SpiderVerse AR

SpiderVerse AR is a webcam-first Computer Vision mini-game built with OpenCV and MediaPipe. The user's room stays as the main background while a small Spider-Man city runs in the bottom 25% of the camera frame.

## Run

```bash
cd C:\MachineLearning\Spidey\spiderverse_ar
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

Press `q` or `Esc` to quit. Press `r` to restart after game over.

## Required Character Assets

Place your custom chibi Spider-Man PNG here before running:

```text
assets/characters/spiderman/spiderman.png
```

This file is the only valid Spider-Man character. It must be a transparent PNG. The game does not generate a fallback Spider-Man, and if the file is missing it prints `Spider-Man asset not found` and displays `ERROR: Spider-Man asset missing`.

Optional custom villain PNGs:

```text
assets/characters/venom/venom.png
assets/characters/goblin/goblin.png
assets/characters/thug/thug.png
```

Venom and Goblin are scaled close to Spider-Man size while preserving each PNG's aspect ratio.

## Gestures

The game is controlled with one hand. Keep your full palm and wrist visible to the camera.

| Gesture | Action |
|---|---|
| Index + pinky up, middle + ring folded | Shoot web |
| Fist | Punch |
| Open palm | Shield |
| Move the same hand left/right on screen | Move Spider-Man left/right |

Movement follows your palm position:

- Hand left side of camera: Spider-Man moves left.
- Hand right side of camera: Spider-Man moves right.
- Hand near center: Spider-Man stops.

Detection is smoothed for short drops, so control should not stop immediately if MediaPipe misses a few frames.

## Hand Tracking Tips

- Keep your palm open and wrist visible when moving.
- Avoid putting your hand too close to the camera.
- Use good lighting; very bright windows or dark hands against a dark background can reduce tracking quality.
- If the HUD shows `Gesture: none`, move your hand slowly into the middle of the frame until landmarks appear.
- For web gesture, raise index and pinky, fold middle and ring.
- For punch, close all four fingers into a fist.

## Structure

```text
assets/
  characters/
  environment/
  effects/
  sounds/
src/
  audio/
  cv/
  engine/
  entities/
  render/
  config.py
  main.py
```

If non-player PNG sprites are missing, `src/assets_bootstrap.py` creates clean transparent placeholders on first run. Spider-Man is excluded from that bootstrap and must be provided manually.
