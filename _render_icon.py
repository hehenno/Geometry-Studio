"""
Render the PIXEL.MATTER app icon at multiple resolutions.
Aesthetic: low-res dot grid showing a half-lit sphere with chromatic edges
on a deep black background — matches the actual tool's output.
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

OUT_DIR = "/home/claude/pixelmatter"
os.makedirs(OUT_DIR, exist_ok=True)

# Master render size — we'll downsample for smaller targets
MASTER = 1024
# Dot grid resolution
GRID = 22
CELL = MASTER / GRID

# Background — pure black (matches iOS dark icon style and the tool itself)
BG = (0, 0, 0)

# Palette — bold sci-fi pop, similar to the tool's "Adam" palette
PAL = [
    (255, 45, 45),     # red
    (255, 212, 0),     # yellow
    (0, 255, 102),     # green
    (0, 212, 255),     # cyan
    (255, 0, 170),     # magenta
    (255, 255, 255),   # white
]


def render_master():
    """Render the 1024x1024 master icon."""
    # Background: subtle radial gradient for depth
    img = Image.new("RGB", (MASTER, MASTER), BG)
    draw = ImageDraw.Draw(img)

    # Add a tiny vignette behind the dots
    for i in range(8):
        radius = MASTER * 0.55 - i * 12
        bright = 18 - i * 2
        draw.ellipse(
            [
                MASTER / 2 - radius,
                MASTER / 2 - radius,
                MASTER / 2 + radius,
                MASTER / 2 + radius,
            ],
            fill=(bright // 3, 0, bright // 4),
        )

    img = Image.new("RGB", (MASTER, MASTER), BG)
    draw = ImageDraw.Draw(img)

    # Sphere parameters in normalized space
    sphere_R = 0.88  # radius as fraction of canvas (fills nearly to edge)
    # Light direction (normalized) — upper right, slightly forward
    lx, ly, lz = 0.5, -0.7, -0.5  # negative y = up in image coords
    llen = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / llen, ly / llen, lz / llen

    # Sample each grid cell
    for gy in range(GRID):
        for gx in range(GRID):
            # Cell center in normalized coords (-1 to 1)
            nx = (gx + 0.5) / GRID * 2 - 1
            ny = (gy + 0.5) / GRID * 2 - 1
            dist = math.sqrt(nx * nx + ny * ny)

            # Inside the sphere?
            r_norm = dist / sphere_R
            if r_norm > 1.05:
                continue

            # If on the edge ring (just outside), make it sparse colored dots
            edge_ring = 1.0 <= r_norm <= 1.05
            if edge_ring:
                # Sparse colored fringe
                # use position to deterministically pick a color so it doesn't blob
                ang = math.atan2(ny, nx)
                idx = int((ang / math.pi + 1) * 3) % len(PAL)
                color = PAL[idx]
                # Skip some randomly for a sparkly edge
                hash_val = (gx * 31 + gy * 17) % 7
                if hash_val < 4:
                    continue
            else:
                # Compute sphere z (going into screen)
                z2 = 1 - r_norm * r_norm
                z = -math.sqrt(max(0, z2))  # z negative = toward viewer

                # Normal at this point on the sphere
                nx3 = nx / sphere_R
                ny3 = ny / sphere_R
                nz3 = z
                # Diffuse lighting
                dot = nx3 * lx + ny3 * ly + nz3 * lz
                if dot < 0:
                    dot = 0
                bri = 0.15 + 0.85 * dot

                # Color selection: quantize to palette based on brightness regions
                if bri > 0.85:
                    color = PAL[5]  # white core
                elif bri > 0.65:
                    color = PAL[3]  # cyan
                elif bri > 0.45:
                    color = PAL[1]  # yellow
                elif bri > 0.25:
                    color = PAL[0]  # red
                else:
                    color = PAL[4]  # magenta in shadow

                # Add some palette variation/noise for texture
                hash_val = (gx * 7 + gy * 13 + gx * gy) % 11
                if hash_val < 2 and bri > 0.3:
                    color = PAL[2]  # green sparkle
                elif hash_val == 9 and bri > 0.5:
                    color = PAL[5]

            # Draw the dot at cell center
            cx = (gx + 0.5) * CELL
            cy = (gy + 0.5) * CELL
            dot_r = CELL * 0.36
            draw.ellipse(
                [cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                fill=color,
            )

    # Apply a subtle chromatic aberration to the whole icon for the techy feel
    img = apply_chromatic(img, amount=4)

    # Save the master 1024
    img.save(os.path.join(OUT_DIR, "icon-1024.png"), "PNG")
    return img


def apply_chromatic(img, amount=4):
    """Shift red channel out and blue channel in toward center for a lens-like fringe."""
    w, h = img.size
    cx, cy = w / 2, h / 2
    r, g, b = img.split()

    # Build offset maps by shifting along radial direction.
    # Easier: shift R by (amount, 0) and B by (-amount, 0) globally;
    # for an icon, that simple horizontal split looks plenty fringe-y.
    new_r = Image.new("L", (w, h), 0)
    new_b = Image.new("L", (w, h), 0)
    new_r.paste(r, (amount, 0))
    new_b.paste(b, (-amount, 0))
    return Image.merge("RGB", (new_r, g, new_b))


def make_ios_sizes(master):
    """Render the common iOS icon sizes from the master.
    iOS uses several sizes for different contexts:
    - 1024 (App Store)
    - 180 (iPhone home screen @3x)
    - 167 (iPad Pro)
    - 152 (iPad @2x)
    - 120 (iPhone @2x)
    """
    sizes = {
        "icon-180.png": 180,   # iPhone home screen
        "icon-167.png": 167,   # iPad Pro
        "icon-152.png": 152,   # iPad
        "icon-120.png": 120,   # iPhone @2x
        "icon-512.png": 512,   # General/PWA
        "favicon-192.png": 192,  # PWA / Android
        "favicon-32.png": 32,    # tab favicon
    }
    for name, size in sizes.items():
        # Use LANCZOS for high-quality downsample
        scaled = master.resize((size, size), Image.LANCZOS)
        scaled.save(os.path.join(OUT_DIR, name), "PNG")
        print(f"  {name} ({size}x{size})")


if __name__ == "__main__":
    print("Rendering master icon...")
    master = render_master()
    print("Generating iOS sizes:")
    make_ios_sizes(master)
    print("\nDone.")
