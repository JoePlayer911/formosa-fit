import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_flowchart_16_9():
    # Canvas size: 1920x1080 (Horizontal 16:9)
    width, height = 1920, 1080
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Font paths on Windows
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"      # Microsoft JhengHei
    font_bold_path = "C:\\Windows\\Fonts\\msjhbd.ttc"  # Microsoft JhengHei Bold

    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        font_bold_path = "arial.ttf"

    # Load fonts (Large size for presentation/slide view)
    title_font = ImageFont.truetype(font_bold_path, 36)
    sub_title_font = ImageFont.truetype(font_path, 18)
    node_font = ImageFont.truetype(font_bold_path, 18)
    label_font = ImageFont.truetype(font_bold_path, 16)
    footer_font = ImageFont.truetype(font_path, 14)

    # Draw header
    draw.text((width//2, 55), "FormosaFit AI 智慧穿搭推薦系統 流程圖", fill="#1A202C", font=title_font, anchor="mm")
    draw.text((width//2, 100), "系統核心推薦與檢索管線執行流程 (Core Recommendation & Search Pipeline)", fill="#718096", font=sub_title_font, anchor="mm")
    draw.line([(100, 130), (1820, 130)], fill="#E2E8F0", width=2)

    # Color Palette (Simple flat colors, no gradients)
    GREEN = "#48BB78"    # Start / End
    ORANGE = "#ED8936"   # Decision
    BLUE = "#3182CE"     # Process
    RED = "#E53E3E"      # Failure / Abort
    LINE_COLOR = "#4A5568"
    TEXT_COLOR = "#FFFFFF"

    # Helper function to draw rounded pill (Start/End)
    def draw_pill(cx, cy, w, h, text, fill_color):
        x0, y0 = cx - w//2, cy - h//2
        x1, y1 = cx + w//2, cy + h//2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=h//2, fill=fill_color)
        draw.text((cx, cy), text, fill=TEXT_COLOR, font=node_font, anchor="mm")

    # Helper function to draw process box (Rectangle)
    def draw_process(cx, cy, w, h, text, fill_color):
        x0, y0 = cx - w//2, cy - h//2
        x1, y1 = cx + w//2, cy + h//2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=fill_color)
        
        # Split text into lines to center vertically
        lines = text.split("\n")
        total_h = len(lines) * 26
        start_y = cy - total_h // 2 + 13
        for i, line in enumerate(lines):
            draw.text((cx, start_y + i * 26), line, fill=TEXT_COLOR, font=node_font, anchor="mm")

    # Helper function to draw decision diamond
    def draw_diamond(cx, cy, w, h, text, fill_color):
        points = [
            (cx, cy - h//2),  # Top
            (cx + w//2, cy),  # Right
            (cx, cy + h//2),  # Bottom
            (cx - w//2, cy)   # Left
        ]
        draw.polygon(points, fill=fill_color)
        
        # Split text
        lines = text.split("\n")
        total_h = len(lines) * 26
        start_y = cy - total_h // 2 + 13
        for i, line in enumerate(lines):
            draw.text((cx, start_y + i * 26), line, fill=TEXT_COLOR, font=node_font, anchor="mm")

    # Helper function to draw arrow line
    def draw_arrow(x0, y0, x1, y1, color=LINE_COLOR, width=3, text="", text_pos="side"):
        draw.line([x0, y0, x1, y1], fill=color, width=width)
        
        # Draw arrowhead pointing to (x1, y1)
        angle = math.atan2(y1 - y0, x1 - x0)
        arrow_len = 12
        arrow_angle = math.pi / 6
        
        tx1 = x1 - arrow_len * math.cos(angle - arrow_angle)
        ty1 = y1 - arrow_len * math.sin(angle - arrow_angle)
        tx2 = x1 - arrow_len * math.cos(angle + arrow_angle)
        ty2 = y1 - arrow_len * math.sin(angle + arrow_angle)
        
        draw.polygon([x1, y1, tx1, ty1, tx2, ty2], fill=color)
        
        if text:
            tx = (x0 + x1) / 2
            ty = (y0 + y1) / 2
            if text_pos == "side":
                draw.text((tx + 15, ty), text, fill=LINE_COLOR, font=label_font, anchor="lm")
            elif text_pos == "above":
                draw.text((tx, ty - 15), text, fill=LINE_COLOR, font=label_font, anchor="mm")
            elif text_pos == "below":
                draw.text((tx, ty + 18), text, fill=LINE_COLOR, font=label_font, anchor="mm")

    # Helper function for stepped line arrows
    def draw_step_arrow(pts, color=LINE_COLOR, width=3, text="", text_pt=None):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i+1]
            if i == len(pts) - 2:
                # Add arrowhead to final segment
                draw_arrow(x0, y0, x1, y1, color=color, width=width)
            else:
                draw.line([x0, y0, x1, y1], fill=color, width=width)
        
        if text and text_pt:
            draw.text(text_pt, text, fill=LINE_COLOR, font=label_font, anchor="mm")

    # Helper function for stepped line without arrows
    def draw_step_line(pts, color=LINE_COLOR, width=3):
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=color, width=width)

    # --- Coordinates Design (Horizontal flow) ---
    # Column centers: Col 1-5 centered in 1920 width
    # Col 1: 280, Col 2: 590, Col 3: 900, Col 4: 1210, Col 5: 1520
    # Row heights: Row 1 = 260, Row 1.5 = 440, Row 2 = 680, Row 3 = 880
    
    # --- Row 1 (Left to Right) ---
    
    # 1. Start Pill
    draw_pill(280, 260, 240, 70, "開始 (輸入穿搭條件)", GREEN)
    
    # 2. Check Photo Diamond
    draw_diamond(590, 260, 240, 100, "是否已上傳照片？", ORANGE)
    
    # 3. Prompt Upload (Failure / Red Box)
    draw_process(590, 440, 220, 80, "提示上傳照片\n並返回等待", RED)
    
    # 4. VLM Analyzer (Process)
    draw_process(900, 260, 250, 90, "VLM 圖像特徵分析\n(解析身型、衣服、色系)", BLUE)
    
    # 5. Weather API (Process)
    draw_process(1210, 260, 250, 90, "取得指定城市天氣\n(溫度、濕度、降雨)", BLUE)
    
    # 6. Gender Mode Selection (Decision)
    draw_diamond(1520, 260, 240, 100, "是否手動設定性別？", ORANGE)
    
    # --- Row 1.5 (Gender split) ---
    
    # 7. Manual Gender Selection (Process)
    draw_process(1350, 440, 200, 80, "採用手動設定性別\n(男性 / 女性)", BLUE)
    
    # 8. Auto Gender Detection (Process)
    draw_process(1690, 440, 200, 80, "依 VLM 分析結果\n自動判定性別", BLUE)
    
    # --- Row 2 (Right to Left) ---
    
    # 9. Product Search DB (Process)
    draw_process(1520, 680, 260, 90, "ChromaDB 商品檢索\n(特徵風格匹配 Top 15)", BLUE)
    
    # 10. Gender Post-Filter (Process)
    draw_process(1210, 680, 260, 90, "商品性別硬性過濾\n(排除非目標性別單品)", BLUE)
    
    # 11. LLM Recommendation (Process)
    draw_process(900, 680, 260, 90, "LLM 穿搭推薦推理\n(生成 3 套穿搭報告)", BLUE)
    
    # 12. Shopping Link Search (Process)
    draw_process(590, 680, 260, 90, "搜尋商品購買連結\n(依官網電商權重排序)", BLUE)
    
    # 13. UI Result Presentation (Process)
    draw_process(280, 680, 260, 90, "呈現最終推薦結果\n(報告與排序購買連結)", BLUE)
    
    # --- Row 3 ---
    
    # 14. End Pill
    draw_pill(280, 880, 240, 70, "結束 (完成推薦)", GREEN)

    # --- Draw Connecting Lines & Arrows ---
    
    # Start -> Check Photo
    draw_arrow(400, 260, 470, 260)
    
    # Check Photo -> Prompt Upload (No)
    draw_arrow(590, 310, 590, 400, text="否", text_pos="side")
    
    # Prompt Upload -> Back to input/Start loop
    # From bottom of red box (590, 480) to (590, 520) to (280, 520) to bottom of start pill (280, 295)
    draw_step_arrow([(590, 480), (590, 520), (280, 520), (280, 295)])
    
    # Check Photo -> VLM Analyzer (Yes)
    draw_arrow(710, 260, 775, 260, text="是", text_pos="above")
    
    # VLM Analyzer -> Weather API
    draw_arrow(1025, 260, 1085, 260)
    
    # Weather API -> Gender Mode
    draw_arrow(1335, 260, 1400, 260)
    
    # Gender Mode -> Manual Branch (Yes)
    # split down-left to Manual Gender top (1350, 400)
    draw_step_arrow([(1520, 310), (1520, 350), (1350, 350), (1350, 400)], text="是", text_pt=(1435, 335))
    
    # Gender Mode -> Auto Branch (No)
    # split down-right to Auto Gender top (1690, 400)
    draw_step_arrow([(1520, 310), (1520, 350), (1690, 350), (1690, 400)], text="否", text_pt=(1605, 335))
    
    # Branches -> Product Search DB (merge lines without arrowheads at merge point)
    # Manual Gender bottom (1350, 480) down to 560, right to 1520
    draw_step_line([(1350, 480), (1350, 560), (1520, 560)])
    # Auto Gender bottom (1690, 480) down to 560, left to 1520
    draw_step_line([(1690, 480), (1690, 560), (1520, 560)])
    # Merged line down to ChromaDB search top (1520, 635)
    draw_arrow(1520, 560, 1520, 635)
    
    # ChromaDB Search -> Gender Hard Filter
    draw_arrow(1390, 680, 1340, 680)
    
    # Gender Hard Filter -> LLM Recommendation
    draw_arrow(1080, 680, 1030, 680)
    
    # LLM Recommendation -> Shopping Link Search
    draw_arrow(770, 680, 720, 680)
    
    # Shopping Link Search -> UI Result Presentation
    draw_arrow(460, 680, 410, 680)
    
    # UI Result Presentation -> End
    draw_arrow(280, 725, 280, 845)

    # --- Draw Legend ---
    legend_x = width - 420
    legend_y = height - 120
    draw.rounded_rectangle([legend_x - 10, legend_y - 10, legend_x + 360, legend_y + 80], radius=8, outline="#CBD5E1", width=2)
    draw.text((legend_x + 175, legend_y + 10), "圖例說明 (Legend)", fill="#1A202C", font=ImageFont.truetype(font_bold_path, 14), anchor="mm")
    
    # Legend Start/End
    draw.rounded_rectangle([legend_x + 15, legend_y + 30, legend_x + 45, legend_y + 45], radius=7, fill=GREEN)
    draw.text((legend_x + 60, legend_y + 38), "開始 / 結束", fill="#4A5568", font=footer_font, anchor="lm")
    
    # Legend Process
    draw.rounded_rectangle([legend_x + 185, legend_y + 30, legend_x + 215, legend_y + 45], radius=3, fill=BLUE)
    draw.text((legend_x + 230, legend_y + 38), "核心處理步驟", fill="#4A5568", font=footer_font, anchor="lm")
    
    # Legend Decision
    draw.polygon([(legend_x + 30, legend_y + 63), (legend_x + 40, legend_y + 57), (legend_x + 30, legend_y + 51), (legend_x + 20, legend_y + 57)], fill=ORANGE)
    draw.text((legend_x + 60, legend_y + 57), "條件判定 / 決策", fill="#4A5568", font=footer_font, anchor="lm")

    # Legend Abort/Error
    draw.rounded_rectangle([legend_x + 185, legend_y + 50, legend_x + 215, legend_y + 65], radius=3, fill=RED)
    draw.text((legend_x + 230, legend_y + 58), "例外阻斷提示", fill="#4A5568", font=footer_font, anchor="lm")

    # Draw Footer
    draw.text((100, height - 60), "FormosaFit AI · Pipeline Execution Flowchart · 2026", fill="#A0AEC0", font=footer_font, anchor="lm")

    # Save image
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flowchart_16_9.png")
    image.save(output_path, "PNG")
    print(f"Flowchart successfully saved to {output_path}")

if __name__ == "__main__":
    create_flowchart_16_9()
