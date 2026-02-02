from PIL import Image, ImageDraw, ImageFont
import logging
import os

logger = logging.getLogger(__name__)

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """
    Attempts to load a standard font for diverse OSs.
    """
    candidates = []
    if bold:
        candidates.extend(["arialbd.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf", "Roboto-Bold.ttf"])
    
    candidates.extend([
        "arial.ttf",           # Windows
        "DejaVuSans-Bold.ttf", # Linux 
        "DejaVuSans.ttf",
        "FreeSans.ttf",
        "liberation-sans.ttf"
    ])
    
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
    
    # Create a single watermark stamp
    stamp = Image.new('RGBA', (int(text_w * 1.2), int(text_h * 2)), (255, 255, 255, 0))
    draw_stamp = ImageDraw.Draw(stamp)
    # Changed to black (0,0,0) with opacity (160/255) to be more visible
    draw_stamp.text((0, 0), text, font=font, fill=(0, 0, 0, 160)) 
    
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

def create_gradient_badge(width: int, height: int) -> Image.Image:
    """
    Creates a rounded rectangle badge with a modern fire-orange gradient.
    """
    # 1. Create Linear Gradient
    # Gradient Colors: "Fire" / Modern Orange-Red
    start_color = (255, 140, 0) # Dark Orange
    end_color = (208, 0, 0)     # Deep Red
    
    # Generate 1xHeight gradient strip
    gradient_strip = Image.new('RGB', (1, height))
    for y in range(height):
        # Linear interpolation
        ratio = y / height
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        gradient_strip.putpixel((0, y), (r, g, b))
        
    # Resize to fill
    gradient_rect = gradient_strip.resize((width, height), resample=Image.Resampling.NEAREST)
    
    # 2. Add Alpha Mask for Rounded Rectangle
    mask = Image.new('L', (width, height), 0)
    draw_mask = ImageDraw.Draw(mask)
    # Corner radius ~20% of min dimension
    radius = int(min(width, height) * 0.25)
    draw_mask.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    
    # Apply mask
    badge = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    badge.paste(gradient_rect, (0, 0), mask=mask)
    
    return badge

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
            
            # --- 2. Discount Badge (Top Right) ---
            # Use a rectangular shape now
            # Base height on 15% of image min dim
            badge_h = int(min(width, height) * 0.15)
            badge_h = max(badge_h, 50)
            
            # Width = based on aspect ratio approx 1.8:1
            badge_w = int(badge_h * 1.8)
            
            padding = 15
            x0 = width - badge_w - padding
            y0 = padding
            
            # Create Gradient Badge
            badge = create_gradient_badge(badge_w, badge_h)
            
            # Draw Border on Badge
            draw_badge = ImageDraw.Draw(badge)
            border_width = int(max(2, badge_h * 0.05))
            radius = int(min(badge_w, badge_h) * 0.25)
            draw_badge.rounded_rectangle((0, 0, badge_w-1, badge_h-1), radius=radius, outline="white", width=border_width)
            
            # Draw Text on Badge
            text = f"-{discount_percent}%"
            # Reduced font size slightly for cleaner look
            font_size = int(badge_h * 0.55) 
            font = load_font(font_size, bold=True)
            
            left, top, right, bottom = draw_badge.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top
            
            text_x = (badge_w - text_w) / 2
            text_y = (badge_h - text_h) / 2 - (bottom * 0.12)
            
            draw_badge.text((text_x, text_y), text, fill="white", font=font)
            
            # Paste Badge onto Image
            img.paste(badge, (x0, y0), badge)

            # --- 3. Footer with Logo ---
            draw = ImageDraw.Draw(img)
            
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
