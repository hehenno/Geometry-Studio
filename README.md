# PIXEL.MATTER · Display

A mobile-first web tool for generating particle-display style animations — like 3D shapes rendered as low-resolution LED grids. Inspired by the aesthetic of @adamfuhrer's generative work.

Built as a single self-contained `index.html` file. No build step, no dependencies.

## Features

- **9 3D primitives** — cube, sphere, torus, cylinder, cone, pyramid, octahedron, icosahedron, helix
- **Smooth shading** with per-vertex normals on rounded shapes (real Gouraud-style lighting)
- **Orthographic projection** — true isometric, no perspective distortion
- **Dot/pixel grid display** — your 3D shape gets rendered onto an offscreen canvas, then sampled through a configurable resolution grid (16–200 cells per side)
- **4 display modes** — round dots, square pixels, RGB sub-pixels (vertical RGB stripes per cell, like an LCD), ASCII characters
- **9 color palettes** with optional color quantization
- **Curved wireframes** — sphere shows clean great circles, torus shows clean rings, etc.
- **FX effects**:
  - Chromatic aberration (3 levels)
  - Highlight grain (3 levels) — scattered grain around bright areas
  - Pixel emitter — particles fly outward from highlights with their own configurable life, speed, and FPS
- **Light direction control** — manual sliders or live phone tilt
- **Motion sensor support** — tilt the phone to rotate the object or move the light direction in real-time
- **Touch controls** — drag to rotate, pinch to zoom
- **Export** — PNG snapshots, animated GIF, and WebM/MP4 video recording at up to 1920×1920

## Usage

### Local

Just open `index.html` in any modern browser. Works offline.

### GitHub Pages

Push this repo to GitHub, enable Pages in repo settings (Settings → Pages → Source: deploy from `main` branch, root folder). Your tool will be live at `https://<username>.github.io/<repo-name>/`.

### Mobile

Open the deployed URL on your phone, then "Add to Home Screen" in Safari for a fullscreen native-like experience with the custom app icon. Note: device motion access requires HTTPS, which GitHub Pages provides automatically.

## Repo layout

```
index.html         # The whole app
manifest.json      # PWA metadata (name, icon, theme color)
icon-1024.png      # Master app icon
icon-180.png       # iPhone home screen
icon-167.png       # iPad Pro home screen
icon-152.png       # iPad home screen
icon-120.png       # iPhone @2x
icon-512.png       # Large PWA icon
favicon-192.png    # Android / PWA icon
favicon-32.png     # Browser tab favicon
_render_icon.py    # Script that generates all icons (only needed if regenerating)
```

## After Effects / Cinema 4D workflow

1. Tap `⏺ REC` to start recording
2. Tap `⏹ STOP` when done — the video downloads automatically
3. Drop the WebM/MP4 directly into AE 2024+, or convert to ProRes / PNG sequence with `ffmpeg`:

```bash
# WebM → PNG sequence (lossless, perfect for AE)
ffmpeg -i pixeldisplay_*.webm -compression_level 0 frame_%04d.png

# WebM → ProRes (single file, good for editing)
ffmpeg -i pixeldisplay_*.webm -c:v prores_ks -profile:v 3 output.mov
```

## Tech notes

- Pure vanilla JS, no frameworks
- Single HTML file, ~72KB
- 3D math implemented from scratch (rotation matrices, painter's algorithm sort, per-vertex normal shading)
- Source canvas is 512×512 internally; output canvas can scale up to 1920×1920
- Browser support: any modern Chromium / Safari / Firefox. Motion sensors require iOS 13+ or modern Android Chrome
