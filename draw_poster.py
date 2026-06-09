import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_poster():
    width, height = 1080, 1920
    
    # 1. Background Gradient (Dark Theme - Simple and Clean)
    image = Image.new("RGBA", (width, height), "#0B1120")
    draw = ImageDraw.Draw(image)
    
    for y in range(height):
        # Subtle clean gradient from #0B1120 to #0F172A
        r = int(11 + (15 - 11) * (y / height))
        g = int(17 + (23 - 17) * (y / height))
        b = int(32 + (42 - 32) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Removed glowing orbs for a simpler design

    # 2. Setup Overlay for Glassmorphism Cards
    overlay = Image.new("RGBA", (width, height), (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    def draw_glass_card(x0, y0, x1, y1, radius=24):
        # Card shadow
        overlay_draw.rounded_rectangle([x0+12, y0+12, x1+12, y1+12], radius=radius, fill=(0,0,0,60))
        # Card background
        overlay_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(30, 41, 59, 190), outline=(71, 85, 105, 255), width=2)
        
    def draw_glass_pill(x0, y0, x1, y1):
        radius = (y1 - y0) // 2
        draw_glass_card(x0, y0, x1, y1, radius=radius)

    # Fonts
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    font_bold_path = "C:\\Windows\\Fonts\\msjhbd.ttc"
    
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        font_bold_path = "arial.ttf"

    title_font = ImageFont.truetype(font_bold_path, 80)
    subtitle_font = ImageFont.truetype(font_bold_path, 40)
    h2_font = ImageFont.truetype(font_bold_path, 36)
    h3_font = ImageFont.truetype(font_bold_path, 28)
    body_font = ImageFont.truetype(font_path, 24)
    body_bold_font = ImageFont.truetype(font_bold_path, 24)
    small_font = ImageFont.truetype(font_path, 20)

    # 3. Draw Layout

    # Header
    overlay_draw.text((width//2, 100), "FormosaFit AI", font=title_font, fill="#A5B4FC", anchor="mt")
    overlay_draw.text((width//2, 195), "智慧穿搭推薦系統", font=subtitle_font, fill="#F8FAFC", anchor="mt")
    overlay_draw.text((width//2, 250), "Taiwan-localized Smart Fashion Recommendation System", font=small_font, fill="#94A3B8", anchor="mt")

    # Privacy Highlight
    draw_glass_card(80, 320, 1000, 500)
    overlay_draw.text((width//2, 370), "隱私優先 ‧ 邊緣運算 (Privacy-First Edge)", font=h2_font, fill="#34D399", anchor="mm")
    overlay_draw.text((width//2, 430), "全離線運行您的照片與數據。您的隱私，永遠留在您的設備上。", font=body_bold_font, fill="#F8FAFC", anchor="mm")

    # Feature Grid
    # Card 1
    draw_glass_card(80, 540, 520, 760)
    overlay_draw.text((300, 600), "VLM 圖像分析", font=h3_font, fill="#60A5FA", anchor="mm")
    overlay_draw.text((300, 680), "深入解析身型比例、\n衣著特徵與個人色系。", font=body_font, fill="#CBD5E1", anchor="mm", align="center")

    # Card 2
    draw_glass_card(560, 540, 1000, 760)
    overlay_draw.text((780, 600), "即時天氣整合", font=h3_font, fill="#FBBF24", anchor="mm")
    overlay_draw.text((780, 680), "完美應對台灣氣候，\n包含午後雷陣雨與濕熱。", font=body_font, fill="#CBD5E1", anchor="mm", align="center")

    # Card 3
    draw_glass_card(80, 800, 520, 1020)
    overlay_draw.text((300, 860), "商品向量檢索", font=h3_font, fill="#F472B6", anchor="mm")
    overlay_draw.text((300, 940), "基於場景與風格，\n精準匹配在地服飾商品庫。", font=body_font, fill="#CBD5E1", anchor="mm", align="center")

    # Card 4
    draw_glass_card(560, 800, 1000, 1020)
    overlay_draw.text((780, 860), "LLM 推薦推理", font=h3_font, fill="#A78BFA", anchor="mm")
    overlay_draw.text((780, 940), "生成客製化穿搭報告，\n提供完整的身型修飾建議。", font=body_font, fill="#CBD5E1", anchor="mm", align="center")

    # Architecture Card
    draw_glass_card(80, 1080, 1000, 1660)
    overlay_draw.text((width//2, 1140), "彈性且強大的模型架構 (Flexible Architecture)", font=h2_font, fill="#F8FAFC", anchor="mm")
    overlay_draw.line([(140, 1190), (940, 1190)], fill="#475569", width=2)
    overlay_draw.line([(540, 1220), (540, 1600)], fill="#475569", width=2)

    # Left Column
    overlay_draw.text((310, 1250), "核心主力：本地邊緣模型", font=h3_font, fill="#34D399", anchor="mm")
    overlay_draw.text((310, 1290), "Core Focus: Local Edge Models", font=small_font, fill="#94A3B8", anchor="mm")
    
    left_y = 1350
    overlay_draw.text((120, left_y), "確保絕對隱私與低網路延遲", font=body_bold_font, fill="#F8FAFC", anchor="lm")
    overlay_draw.text((120, left_y+50), "• VLM: Moondream2 / LLaVA", font=body_font, fill="#E2E8F0", anchor="lm")
    overlay_draw.text((120, left_y+100), "• LLM: Llama 3.2 3B", font=body_font, fill="#E2E8F0", anchor="lm")
    overlay_draw.text((120, left_y+150), "• 支援任何 Ollama 相容模型", font=body_font, fill="#E2E8F0", anchor="lm")
    overlay_draw.text((120, left_y+200), "• 適合一般日常使用，完全免費", font=body_font, fill="#E2E8F0", anchor="lm")

    # Right Column
    overlay_draw.text((770, 1250), "可選擴充：雲端強大模型", font=h3_font, fill="#F472B6", anchor="mm")
    overlay_draw.text((770, 1290), "Optional: Cloud API Models", font=small_font, fill="#94A3B8", anchor="mm")

    right_y = 1350
    overlay_draw.text((580, right_y), "賦予您最高品質的推理彈性", font=body_bold_font, fill="#F8FAFC", anchor="lm")
    overlay_draw.text((580, right_y+50), "• 支援 OpenAI (GPT-4o 等)", font=body_font, fill="#E2E8F0", anchor="lm")
    overlay_draw.text((580, right_y+100), "• 支援 Gemini (1.5 Pro / Flash)", font=body_font, fill="#E2E8F0", anchor="lm")
    overlay_draw.text((580, right_y+150), "• 作為高難度穿搭的進階選擇", font=body_font, fill="#E2E8F0", anchor="lm")
    overlay_draw.text((580, right_y+210), "(僅在主動提供 API Key 時才會啟用)", font=small_font, fill="#94A3B8", anchor="lm")

    # Bottom Tagline
    draw_glass_pill(260, 1710, 820, 1790)
    overlay_draw.text((width//2, 1750), "專為台灣人打造的專屬穿搭管家", font=body_bold_font, fill="#F8FAFC", anchor="mm")

    # Combine background and overlay
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    # Footer
    draw.text((width//2, 1850), "FormosaFit AI 2026", font=small_font, fill="#64748B", anchor="mm")

    # Save image
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster_portrait.png")
    image.save(output_path, "PNG")
    print(f"Poster successfully saved to {output_path}")

if __name__ == "__main__":
    create_poster()
