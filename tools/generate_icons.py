"""
Script to generate high-resolution and mipmap app icons for Quad Survivor.
Creates icon.png, icon_round.png, and Android mipmap assets in all resolutions.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFilter

def create_quad_icon(size=512, is_round=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background
    bg = Image.new("RGBA", (size, size), (12, 16, 28, 255))
    bg_draw = ImageDraw.Draw(bg)

    # Subtle radial gradient / vignette
    cx, cy = size / 2, size / 2
    for r in range(int(size * 0.75), 0, -6):
        frac = r / (size * 0.75)
        # Deep space to cyan-indigo core
        col = (
            int(12 + (30 - 12) * (1.0 - frac)),
            int(16 + (48 - 16) * (1.0 - frac)),
            int(28 + (72 - 28) * (1.0 - frac)),
            255
        )
        bg_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # Subtle cyber grid lines
    grid_spacing = size // 10
    grid_col = (0, 240, 220, 28)
    for x in range(0, size, grid_spacing):
        bg_draw.line([(x, 0), (x, size)], fill=grid_col, width=max(1, size // 256))
    for y in range(0, size, grid_spacing):
        bg_draw.line([(0, y), (size, y)], fill=grid_col, width=max(1, size // 256))

    img.paste(bg, (0, 0))

    # 2. Outer border ring/accent
    border_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(border_layer)
    pad = int(size * 0.06)
    corner_r = int(size * 0.22) if not is_round else int(size * 0.5)

    if not is_round:
        b_draw.rounded_rectangle(
            [pad, pad, size - pad, size - pad],
            radius=corner_r,
            outline=(0, 240, 220, 180),
            width=max(2, size // 64)
        )
        # Inner corner brackets
        bracket_len = int(size * 0.08)
        b_w = max(2, size // 50)
        # Top-left
        b_draw.line([(pad + 12, pad + 6), (pad + 12 + bracket_len, pad + 6)], fill=(255, 215, 0, 230), width=b_w)
        b_draw.line([(pad + 6, pad + 12), (pad + 6, pad + 12 + bracket_len)], fill=(255, 215, 0, 230), width=b_w)
        # Bottom-right
        b_draw.line([(size - pad - 12 - bracket_len, size - pad - 6), (size - pad - 12, size - pad - 6)], fill=(255, 215, 0, 230), width=b_w)
        b_draw.line([(size - pad - 6, size - pad - 12 - bracket_len), (size - pad - 6, size - pad - 12)], fill=(255, 215, 0, 230), width=b_w)
    else:
        b_draw.ellipse(
            [pad, pad, size - pad, size - pad],
            outline=(0, 240, 220, 200),
            width=max(2, size // 64)
        )

    # 3. Outer Neon Glow behind the Quad Core
    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow_layer)
    glow_radius = int(size * 0.28)
    g_draw.ellipse(
        [cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius],
        fill=(0, 240, 220, 95)
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=size // 16))
    img.alpha_composite(glow_layer)

    # 4. Central The Quad Character (4 Glowing Squares)
    quad_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    q_draw = ImageDraw.Draw(quad_layer)

    q_box = size * 0.17  # size of each quadrant square
    q_gap = size * 0.055 # gap between squares
    q_offset = (q_box + q_gap) / 2.0

    quadrants = [
        (-1, -1),  # Top-left
        (1, -1),   # Top-right
        (-1, 1),   # Bottom-left
        (1, 1),    # Bottom-right
    ]

    for sx, sy in quadrants:
        qx = cx + sx * q_offset
        qy = cy + sy * q_offset

        # Outer glow border for square
        half = q_box / 2.0
        q_draw.rounded_rectangle(
            [qx - half - 3, qy - half - 3, qx + half + 3, qy + half + 3],
            radius=int(q_box * 0.18),
            fill=(0, 160, 180, 120),
            outline=(0, 255, 230, 240),
            width=max(2, int(size * 0.012))
        )

        # Main Square Body (Cyan gradient fill)
        q_draw.rounded_rectangle(
            [qx - half, qy - half, qx + half, qy + half],
            radius=int(q_box * 0.15),
            fill=(0, 220, 205, 255)
        )

        # Inner white energy core
        inner_half = half * 0.55
        q_draw.rounded_rectangle(
            [qx - inner_half, qy - inner_half, qx + inner_half, qy + inner_half],
            radius=int(q_box * 0.1),
            fill=(255, 255, 255, 255)
        )

    # 5. Golden Hyper Core Energy Sparkles in Center & Crosshairs
    c_line_len = size * 0.22
    q_draw.line([(cx - c_line_len, cy), (cx + c_line_len, cy)], fill=(255, 215, 0, 180), width=max(1, size // 160))
    q_draw.line([(cx, cy - c_line_len), (cx, cy + c_line_len)], fill=(255, 215, 0, 180), width=max(1, size // 160))

    # Central golden diamond spark
    spark_r = size * 0.035
    q_draw.polygon([
        (cx, cy - spark_r * 1.5),
        (cx + spark_r, cy),
        (cx, cy + spark_r * 1.5),
        (cx - spark_r, cy)
    ], fill=(255, 235, 90, 255))
    q_draw.circle((cx, cy), radius=spark_r * 0.45, fill=(255, 255, 255, 255))

    img.alpha_composite(quad_layer)
    img.alpha_composite(border_layer)

    # 6. Apply circular mask if round icon requested
    if is_round:
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([pad - 2, pad - 2, size - pad + 2, size - pad + 2], fill=255)
        output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)
        return output

    return img

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("Project root:", root_dir)

    # 1. Generate master 512x512 icons
    icon_512 = create_quad_icon(512, is_round=False)
    icon_round_512 = create_quad_icon(512, is_round=True)

    # Save to root, Source/, and AndroidApp/
    os.makedirs(os.path.join(root_dir, "Assets"), exist_ok=True)
    os.makedirs(os.path.join(root_dir, "Source"), exist_ok=True)

    icon_512.save(os.path.join(root_dir, "icon.png"), "PNG")
    icon_512.save(os.path.join(root_dir, "Source", "icon.png"), "PNG")
    icon_512.save(os.path.join(root_dir, "Assets", "icon.png"), "PNG")
    icon_round_512.save(os.path.join(root_dir, "Assets", "icon_round.png"), "PNG")
    print("Master 512x512 icons generated.")

    # 2. Generate Android Mipmaps in all required densities
    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    res_dir = os.path.join(root_dir, "AndroidApp", "app", "src", "main", "res")
    for folder, dim in densities.items():
        target_dir = os.path.join(res_dir, folder)
        os.makedirs(target_dir, exist_ok=True)

        # Square icon
        ic_square = create_quad_icon(dim, is_round=False)
        ic_square.save(os.path.join(target_dir, "ic_launcher.webp"), "WEBP")
        ic_square.save(os.path.join(target_dir, "ic_launcher.png"), "PNG")

        # Round icon
        ic_round = create_quad_icon(dim, is_round=True)
        ic_round.save(os.path.join(target_dir, "ic_launcher_round.webp"), "WEBP")
        ic_round.save(os.path.join(target_dir, "ic_launcher_round.png"), "PNG")

        print(f"Generated {folder} ({dim}x{dim})")

    print("All app icons successfully generated!")

if __name__ == "__main__":
    main()
