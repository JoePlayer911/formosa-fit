import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_flowchart():
    # Canvas size: vertical flowchart
    width, height = 900, 1650
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Font paths on Windows
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"      # Microsoft JhengHei
    font_bold_path = "C:\\Windows\\Fonts\\msjhbd.ttc"  # Microsoft JhengHei Bold

    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        font_bold_path = "arial.ttf"

    # Load fonts
    title_font = ImageFont.truetype(font_bold_path, 24)
    sub_title_font = ImageFont.truetype(font_path, 14)
    node_font = ImageFont.truetype(font_bold_path, 14)
    label_font = ImageFont.truetype(font_bold_path, 12)
    footer_font = ImageFont.truetype(font_path, 12)

    # Draw header
    draw.text((width//2, 35), "FormosaFit AI 智慧穿搭推薦系統 流程圖", fill="#1A202C", font=title_font, anchor="mm")
    draw.text((width//2, 65), "系統核心推薦與檢索管線執行流程 (Core Recommendation & Search Pipeline)", fill="#718096", font=sub_title_font, anchor="mm")
    draw.line([(80, 85), (820, 85)], fill="#E2E8F0", width=1)

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
        total_h = len(lines) * 18
        start_y = cy - total_h // 2 + 9
        for i, line in enumerate(lines):
            draw.text((cx, start_y + i * 18), line, fill=TEXT_COLOR, font=node_font, anchor="mm")

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
        total_h = len(lines) * 18
        start_y = cy - total_h // 2 + 9
        for i, line in enumerate(lines):
            draw.text((cx, start_y + i * 18), line, fill=TEXT_COLOR, font=node_font, anchor="mm")

    # Helper function to draw arrow line
    def draw_arrow(x0, y0, x1, y1, color=LINE_COLOR, width=2, text="", text_pos="side"):
        draw.line([x0, y0, x1, y1], fill=color, width=width)
        
        # Draw arrowhead pointing to (x1, y1)
        angle = math.atan2(y1 - y0, x1 - x0)
        arrow_len = 8
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
                draw.text((tx + 10, ty), text, fill=LINE_COLOR, font=label_font, anchor="lm")
            elif text_pos == "above":
                draw.text((tx, ty - 10), text, fill=LINE_COLOR, font=label_font, anchor="mm")
            elif text_pos == "below":
                draw.text((tx, ty + 12), text, fill=LINE_COLOR, font=label_font, anchor="mm")

    # Helper function for stepped line arrows
    def draw_step_arrow(pts, color=LINE_COLOR, width=2, text="", text_pt=None):
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
    def draw_step_line(pts, color=LINE_COLOR, width=2):
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=color, width=width)

    # --- Draw Nodes ---
    
    # 1. Start Pill
    draw_pill(450, 130, 220, 50, "開始 (輸入穿搭條件)", GREEN)
    
    # 2. Check Photo Diamond
    draw_diamond(450, 260, 240, 90, "是否已上傳照片？", ORANGE)
    
    # 3. Prompt Upload (Failure / Red Box)
    draw_process(730, 260, 180, 60, "提示上傳照片\n並返回等待", RED)
    
    # 4. VLM Analyzer (Process)
    draw_process(450, 400, 260, 70, "VLM 圖像特徵分析\n(解析身型、現有衣服與色系)", BLUE)
    
    # 5. Weather API (Process)
    draw_process(450, 520, 260, 70, "取得指定城市天氣資訊\n(溫度、濕度、降雨機率)", BLUE)
    
    # 6. Gender Mode Selection (Decision)
    draw_diamond(450, 660, 240, 90, "是否手動設定性別？", ORANGE)
    
    # 7. Manual Gender Selection (Process)
    draw_process(250, 790, 200, 65, "採用手動設定性別\n(男性 / 女性)", BLUE)
    
    # 8. Auto Gender Detection (Process)
    draw_process(650, 790, 200, 65, "依 VLM 分析結果\n自動判定性別", BLUE)
    
    # 9. Product Search DB (Process)
    draw_process(450, 930, 280, 70, "ChromaDB 向量商品檢索\n(特徵與風格語意匹配 Top 15)", BLUE)
    
    # 10. Gender Post-Filter (Process)
    draw_process(450, 1050, 280, 70, "商品性別硬性過濾 (Hard Filter)\n(排除非目標性別商品)", BLUE)
    
    # 11. LLM Recommendation (Process)
    draw_process(450, 1170, 280, 70, "LLM 穿搭推薦推理\n(生成 3 套穿搭報告與理由)", BLUE)
    
    # 12. Shopping Link Search (Process)
    draw_process(450, 1290, 280, 70, "DuckDuckGo 搜尋商品連結\n(依官網與電商權重排序評分)", BLUE)
    
    # 13. UI Result Presentation (Process)
    draw_process(450, 1410, 280, 70, "呈現最終推薦結果\n(穿搭報告 + 購買連結)", BLUE)
    
    # 14. End Pill
    draw_pill(450, 1530, 220, 50, "結束 (完成推薦)", GREEN)

    # --- Draw Connecting Lines & Arrows ---
    
    # Start -> Check Photo
    draw_arrow(450, 155, 450, 215)
    
    # Check Photo -> Prompt Upload (No)
    draw_arrow(570, 260, 640, 260, text="否", text_pos="above")
    
    # Prompt Upload -> Back to input/Start loop
    draw_step_arrow([(730, 230), (730, 130), (560, 130)])
    
    # Check Photo -> VLM Analyzer (Yes)
    draw_arrow(450, 305, 450, 365, text="是", text_pos="side")
    
    # VLM Analyzer -> Weather API
    draw_arrow(450, 435, 450, 485)
    
    # Weather API -> Gender Mode
    draw_arrow(450, 555, 450, 615)
    
    # Gender Mode -> Manual Branch (Yes)
    draw_step_arrow([(330, 660), (250, 660), (250, 757)], text="是", text_pt=(290, 645))
    
    # Gender Mode -> Auto Branch (No)
    draw_step_arrow([(570, 660), (650, 660), (650, 757)], text="否", text_pt=(610, 645))
    
    # Branches -> Product Search DB
    draw_step_line([(250, 822), (250, 875), (450, 875)])
    draw_step_line([(650, 822), (650, 875), (450, 875)])
    draw_arrow(450, 875, 450, 895)
    
    # Product Search -> Gender Post-Filter
    draw_arrow(450, 965, 450, 1015)
    
    # Gender Post-Filter -> LLM Recommendation
    draw_arrow(450, 1085, 450, 1135)
    
    # LLM Recommendation -> Shopping Link Search
    draw_arrow(450, 1205, 450, 1255)
    
    # Shopping Link Search -> UI Result Presentation
    draw_arrow(450, 1325, 450, 1375)
    
    # UI Result Presentation -> End
    draw_arrow(450, 1445, 450, 1505)

    # --- Draw Legend ---
    # We can draw a small legend in the bottom left
    legend_x = 100
    legend_y = 1530
    draw.rounded_rectangle([legend_x - 45, legend_y - 45, legend_x + 160, legend_y + 45], radius=6, outline="#CBD5E1", width=1)
    draw.text((legend_x + 55, legend_y - 30), "圖例說明 (Legend)", fill="#1A202C", font=ImageFont.truetype(font_bold_path, 11), anchor="mm")
    
    # Legend Start/End
    draw.rounded_rectangle([legend_x - 35, legend_y - 15, legend_x - 15, legend_y - 5], radius=5, fill=GREEN)
    draw.text((legend_x + 20, legend_y - 10), "開始 / 結束", fill="#4A5568", font=footer_font, anchor="lm")
    
    # Legend Process
    draw.rounded_rectangle([legend_x - 35, legend_y + 5, legend_x - 15, legend_y + 15], radius=2, fill=BLUE)
    draw.text((legend_x + 20, legend_y + 10), "一般處理工序", fill="#4A5568", font=footer_font, anchor="lm")
    
    # Legend Decision
    draw.polygon([(legend_x - 25, legend_y + 22), (legend_x - 17, legend_y + 27), (legend_x - 25, legend_y + 32), (legend_x - 33, legend_y + 27)], fill=ORANGE)
    draw.text((legend_x + 20, legend_y + 27), "條件判定 / 決策", fill="#4A5568", font=footer_font, anchor="lm")

    # Draw Footer
    draw.text((width//2, 1610), "FormosaFit AI · Pipeline Execution Flowchart · 2026", fill="#A0AEC0", font=footer_font, anchor="mm")

    # Save image
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flowchart.png")
    image.save(output_path, "PNG")
    print(f"Flowchart successfully saved to {output_path}")

if __name__ == "__main__":
    create_flowchart()
