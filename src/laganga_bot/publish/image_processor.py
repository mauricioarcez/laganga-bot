from PIL import Image, ImageDraw, ImageFont
import logging
import os
import math

logger = logging.getLogger(__name__)

def load_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Attempts to load a standard font for diverse OSs.
    """
    candidates = [
        "arial.ttf",           # Windows
        "DejaVuSans-Bold.ttf", # Linux 
        "DejaVuSans.ttf",
        "FreeSans.ttf",
        "liberation-sans.ttf"
    ]
    
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    
    logger.warning("No TrueType font found, using default bitmap font.")
    return ImageFont.load_default()

def add_watermark(img: Image.Image, text: str) -> Image.Image:
    """
    Adds a diagonal watermark pattern to the image.
    """
    # Create a transparent layer for the watermark
    txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    width, height = img.size
    
    # Calculate font size relative to image
    font_size = int(min(width, height) * 0.05)
    font_size = max(font_size, 20)
    font = load_font(font_size)
    
    # Measure text
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_w = right - left
    text_h = bottom - top
    
    # Define spacing
    x_gap = text_w * 1.5
    y_gap = text_h * 4
    
    # Rotate context? No, simpler to draw usually, but for diagonal 
    # we usually draw on a separate temp image, rotate it, and paste.
    # Or just write rotated text? Pillow doesn't draw text rotated directly.
    # We must draw text on a small image, rotate it, and paste it.
    
    # Efficient way: Create one tile and repeat? 
    # Or simpler: Just simple diagonal placement.
    
    # Create a single watermark stamp
    stamp = Image.new('RGBA', (int(text_w * 1.2), int(text_h * 2)), (255, 255, 255, 0))
    draw_stamp = ImageDraw.Draw(stamp)
    # Changed to black (0,0,0) with low opacity (40/255) to be visible on white backgrounds
    draw_stamp.text((0, 0), text, font=font, fill=(0, 0, 0, 40)) 
    
    # Rotate the stamp
    rotated_stamp = stamp.rotate(30, expand=True, resample=Image.BICUBIC)
    stamp_w, stamp_h = rotated_stamp.size
    
    # Tile the rotated stamp across the image
    for y in range(-stamp_h, height, int(stamp_h * 1.5)):
        for x in range(-stamp_w, width, int(stamp_w * 1.2)):
            txt_layer.paste(rotated_stamp, (x, y), rotated_stamp)
            
    # Composite
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        
    return Image.alpha_composite(img, txt_layer)

def process_deal_image(image_path: str, discount_percent: int) -> str:
    """
    Adds overlays to the image: watermark, discount badge, and logo footer.
    """
    if not image_path or not os.path.exists(image_path):
        return image_path

    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            width, height = img.size
            
            # --- 1. Watermark ---
            img = add_watermark(img, "lagangaofertas.com")
            
            # Prepare to draw on top
            draw = ImageDraw.Draw(img)
            
            # --- 2. Discount Badge (Top Right) ---
            # Adjusted size: 28% of min dimension, min 90px to prevent overpowering small images
            badge_diameter = int(min(width, height) * 0.28)
            badge_diameter = max(badge_diameter, 90)
            
            padding = 15
            x0 = width - badge_diameter - padding
            y0 = padding
            x1 = width - padding
            y1 = badge_diameter + padding
            
            # Draw red circle
            draw.ellipse([x0, y0, x1, y1], fill="#E02424", outline="white", width=4)
            
            # Text
            text = f"-{discount_percent}%"
            # Adjust font size to fit well (approx 35% of diameter is usually safe)
            font_size = int(badge_diameter * 0.35) 
            font = load_font(font_size)
            
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top
            
            text_x = x0 + (badge_diameter - text_w) / 2
            text_y = y0 + (badge_diameter - text_h) / 2
            
            # Offset Y slightly if needed to visual center
            text_y -= bottom * 0.1 

            draw.text((text_x, text_y), text, fill="white", font=font)
            
            # --- 3. Footer with Logo ---
            # Bar height 8% of image height
            bar_height = max(50, int(height * 0.08))
            draw.rectangle([0, height - bar_height, width, height], fill=(2, 8, 23))
            
            # Load Logo
            logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                
                # Resize logo to fit in bar with padding
                logo_padding = 8
                target_h = bar_height - (logo_padding * 2)
                
                # Keep aspect ratio
                aspect = logo.width / logo.height
                target_w = int(target_h * aspect)
                
                logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                # Position: Centered
                logo_x = (width - target_w) // 2
                logo_y = height - bar_height + logo_padding
                
                # Paste logo (using itself as mask for transparency)
                img.paste(logo, (logo_x, logo_y), logo)
                
            else:
                # Fallback text if logo missing
                footer_text = "Encontrado por La Ganga Bot"
                footer_font = load_font(int(bar_height * 0.4))
                
                # Center text
                left, top, right, bottom = draw.textbbox((0, 0), footer_text, font=footer_font)
                f_w = right - left
                f_h = bottom - top
                f_x = (width - f_w) // 2
                f_y = height - bar_height + (bar_height - f_h)/2 - 2
                
                draw.text((f_x, f_y), footer_text, fill="white", font=footer_font)

            # Convert back to RGB to save as JPG (stripping alpha)
            final_img = img.convert("RGB")
            final_img.save(image_path)
            
            logger.info(f"Image processed with overlays: {image_path}")
            return image_path
            
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
        return image_path
