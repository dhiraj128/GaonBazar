"""
Creates side-by-side comparison images:
1. Actual Light Mode vs Reference 01 Light Mode
2. Actual Dark Mode vs Reference 01 Dark Mode
"""

import os
from PIL import Image, ImageDraw, ImageFont

BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\c8063578-99fe-474e-aa3c-d3b8443185e1"
FINAL_SS_DIR = os.path.join(BRAIN_DIR, "screenshots_final")
REF_DIR = os.path.join(BRAIN_DIR, "design_reference")
OUTPUT_DIR = os.path.join(BRAIN_DIR, "comparisons")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_comparison(actual_path, ref_path, title_actual, title_ref, out_path):
    actual = Image.open(actual_path).convert("RGB")
    ref = Image.open(ref_path).convert("RGB")
    
    # Scale both to target height 800
    target_height = 800
    actual_w = int(actual.width * (target_height / actual.height))
    ref_w = int(ref.width * (target_height / ref.height))
    
    actual_resized = actual.resize((actual_w, target_height), Image.Resampling.LANCZOS)
    ref_resized = ref.resize((ref_w, target_height), Image.Resampling.LANCZOS)
    
    header_h = 50
    total_w = actual_w + ref_w + 30
    total_h = target_height + header_h + 20
    
    comp = Image.new("RGB", (total_w, total_h), (245, 247, 250))
    draw = ImageDraw.Draw(comp)
    
    # Draw headers
    draw.rectangle([0, 0, total_w, header_h], fill=(24, 30, 37))
    draw.text((20, 15), title_actual, fill=(255, 255, 255))
    draw.text((actual_w + 40, 15), title_ref, fill=(74, 222, 128))
    
    # Paste images
    comp.paste(actual_resized, (10, header_h + 10))
    comp.paste(ref_resized, (actual_w + 20, header_h + 10))
    
    comp.save(out_path)
    print(f"Saved comparison to: {out_path}")

def main():
    # 1. Light Mode Home Comparison
    actual_light = os.path.join(FINAL_SS_DIR, "01_home_light_390px.png")
    ref_light = "static/images/ref_phone_light.png" # Cropped reference from 01
    out_light = os.path.join(OUTPUT_DIR, "comparison_home_light.png")
    create_comparison(actual_light, ref_light, "ACTUAL IMPLEMENTATION (Light Mode 390px)", "APPROVED REFERENCE 01 (Light Mode)", out_light)
    
    # 2. Dark Mode Home Comparison
    actual_dark = os.path.join(FINAL_SS_DIR, "06_home_dark_390px.png")
    ref_dark = "static/images/ref_phone_dark.png" # Cropped reference from 01
    out_dark = os.path.join(OUTPUT_DIR, "comparison_home_dark.png")
    create_comparison(actual_dark, ref_dark, "ACTUAL IMPLEMENTATION (Dark Mode 390px)", "APPROVED REFERENCE 01 (Dark Mode)", out_dark)

if __name__ == "__main__":
    main()
