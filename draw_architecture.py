import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_diagram():
    # Canvas size
    width, height = 1000, 920
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Font paths on Windows
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"      # Microsoft JhengHei
    font_bold_path = "C:\\Windows\\Fonts\\msjhbd.ttc"  # Microsoft JhengHei Bold

    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        font_bold_path = "arial.ttf"

    # Load fonts
    title_font = ImageFont.truetype(font_bold_path, 20)
    sub_title_font = ImageFont.truetype(font_path, 14)
    body_font = ImageFont.truetype(font_path, 13)
    body_bold_font = ImageFont.truetype(font_bold_path, 13)
    label_font = ImageFont.truetype(font_bold_path, 12)
    label_bold_font = ImageFont.truetype(font_bold_path, 13)

    # Draw diagram header
    draw.text((width//2, 35), "FormosaFit AI 系統架構圖 (System Architecture)", fill="#0F172A", font=ImageFont.truetype(font_bold_path, 26), anchor="mm")
    draw.text((width//2, 65), "基於 VLM 與 LLM 協作之隱私優先台灣在地化穿搭推薦系統", fill="#475569", font=ImageFont.truetype(font_path, 14), anchor="mm")
    draw.line([(100, 85), (900, 85)], fill="#E2E8F0", width=1)

    # Helper function to draw rounded boxes
    def draw_card(cx, cy, w, h, title, lines, border_color="#CBD5E1", fill_color="#FFFFFF", title_color="#1E293B"):
        x0 = cx - w // 2
        y0 = cy - h // 2
        x1 = cx + w // 2
        y1 = cy + h // 2
        
        # Soft shadow
        draw.rounded_rectangle([x0+3, y0+3, x1+3, y1+3], radius=10, fill="#F8FAFC")
        # Main box
        draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=fill_color, outline=border_color, width=2)
        # Title
        draw.text((cx, y0 + 22), title, fill=title_color, font=title_font, anchor="mm")
        
        # Body text lines
        curr_y = y0 + 44
        for line in lines:
            if isinstance(line, tuple):
                text, is_bold, color = line
                f = body_bold_font if is_bold else body_font
                draw.text((cx, curr_y), text, fill=color, font=f, anchor="mm")
            else:
                draw.text((cx, curr_y), line, fill="#475569", font=body_font, anchor="mm")
            curr_y += 18

    # Helper function to draw arrow lines
    def draw_arrow(x0, y0, x1, y1, color="#64748B", width=2, text="", text_pos="side", is_dashed=False, dash_len=6):
        if is_dashed:
            # Draw dashed line
            dx = x1 - x0
            dy = y1 - y0
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                steps = int(dist / (dash_len * 2))
                for i in range(steps):
                    start_t = float(i) / steps
                    end_t = (float(i) + 0.5) / steps
                    draw.line([
                        (x0 + dx * start_t, y0 + dy * start_t),
                        (x0 + dx * end_t, y0 + dy * end_t)
                    ], fill=color, width=width)
        else:
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
                draw.text((tx + 10, ty), text, fill="#475569", font=label_bold_font, anchor="lm")
            elif text_pos == "above":
                draw.text((tx, ty - 8), text, fill="#475569", font=label_bold_font, anchor="mm")
            elif text_pos == "below":
                draw.text((tx, ty + 10), text, fill="#475569", font=label_bold_font, anchor="mm")

    # Helper function to draw curved step arrows
    def draw_step_arrow(pts, color="#94A3B8", width=2, text="", text_pt=None):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i+1]
            if i == len(pts) - 2:
                # Last segment gets the arrowhead
                draw_arrow(x0, y0, x1, y1, color=color, width=width)
            else:
                draw.line([x0, y0, x1, y1], fill=color, width=width)
        
        if text and text_pt:
            draw.text(text_pt, text, fill="#64748B", font=label_font, anchor="mm")

    # --- Draw Cards ---
    
    # 1. User Input Box (cx=500, cy=140)
    draw_card(
        cx=500, cy=140, w=350, h=90,
        title="使用者與輸入端 User Input",
        lines=[
            "全身照 / 局部照 (Body Photo Upload)",
            "參數設定: 場景 Occasion、城市 City、風格、預算、性別"
        ],
        border_color="#4F46E5", fill_color="#EEF2F6", title_color="#4F46E5"
    )

    # 2. VLM Analyzer Box (cx=500, cy=285)
    draw_card(
        cx=500, cy=285, w=350, h=100,
        title="1. VLM 圖像特徵分析",
        lines=[
            ("本地模型: Moondream / LLaVA (Ollama 執行)", True, "#1E1B4B"),
            "解析身型 Proportions、現有穿衣特徵與顏色色系",
            "輸出高度結構化的 VLM Features (JSON Schema)"
        ],
        border_color="#4F46E5", fill_color="#FFFFFF", title_color="#1E1B4B"
    )

    # 3. Weather Service Box (cx=240, cy=445)
    draw_card(
        cx=240, cy=445, w=280, h=90,
        title="2. 即時天氣資訊整合",
        lines=[
            ("資料來源: wttr.in API (備用本地常數)", True, "#0369A1"),
            "獲取指定城市之溫度、濕度與降雨機率",
            "提供下游 LLM 之材質厚度與防曬雨具決策依據"
        ],
        border_color="#0EA5E9", fill_color="#FFFFFF", title_color="#0369A1"
    )

    # 4. Vector Product DB Box (cx=760, cy=445)
    draw_card(
        cx=760, cy=445, w=280, h=90,
        title="3. 本地商品資料庫檢索",
        lines=[
            ("向量引擎: ChromaDB (MiniLM-L6-v2)", True, "#047857"),
            "依場景與風格相似度檢索服裝 Catalog (35件單品)",
            ("強制後置過濾 (Hard Filter): 依性別設定篩選商品", True, "#DC2626")
        ],
        border_color="#10B981", fill_color="#FFFFFF", title_color="#047857"
    )

    # 5. LLM Advisor Box (cx=500, cy=600)
    draw_card(
        cx=500, cy=600, w=350, h=100,
        title="4. LLM 顧問推薦推理",
        lines=[
            ("本地模型: Llama 3.2 3B (Ollama 離線推論)", True, "#1E1B4B"),
            "結合 VLM 視覺特徵、即時天氣數據與匹配的商品候選",
            "撰寫 3 套客製化穿搭報告 (具備身型修飾與色系理由)"
        ],
        border_color="#4F46E5", fill_color="#FFFFFF", title_color="#1E1B4B"
    )

    # 6. DDG Search & Scoring Box (cx=500, cy=745)
    draw_card(
        cx=500, cy=745, w=350, h=90,
        title="5. 即時搜尋與連結評分",
        lines=[
            ("技術: DuckDuckGo Search (ddgs) + 排序規則", True, "#334155"),
            "針對前三項推薦單品，自動搜尋官方旗艦與知名電商連結",
            "評分權重算法: 提升品牌官網權重，扣減論壇/無效頁面"
        ],
        border_color="#64748B", fill_color="#FFFFFF", title_color="#334155"
    )

    # 7. Frontend UI Box (cx=500, cy=855)
    draw_card(
        cx=500, cy=855, w=350, h=60,
        title="部署介面：Gradio Standalone",
        lines=[
            "展示最終穿搭報告與經篩選排序後的電商購買連結"
        ],
        border_color="#334155", fill_color="#0F172A", title_color="#F8FAFC"
    )

    # --- Draw Connecting Arrows ---
    
    # User Input -> VLM Analyzer
    draw_arrow(500, 185, 500, 235, color="#4F46E5", width=3)

    # User Input (City selection) -> Weather API
    draw_step_arrow([(325, 140), (240, 140), (240, 400)], color="#94A3B8", width=2, text="城市參數 (City)", text_pt=(240, 210))

    # User Input (Scene/Style selection) -> Vector DB
    draw_step_arrow([(675, 140), (760, 140), (760, 400)], color="#94A3B8", width=2, text="風格/場景", text_pt=(760, 210))

    # VLM Analyzer -> Weather API
    draw_arrow(440, 335, 280, 400, color="#64748B", width=2, text="觸發解析", text_pos="side")

    # VLM Analyzer -> Vector DB
    draw_arrow(560, 335, 720, 400, color="#64748B", width=2, text="特徵查詢", text_pos="side")

    # VLM Analyzer -> LLM Advisor (Direct down dashed center line)
    draw_arrow(500, 335, 500, 550, color="#4F46E5", width=2, text="VLM JSON 特徵", text_pos="side", is_dashed=True)

    # Weather API -> LLM Advisor
    draw_arrow(280, 490, 430, 550, color="#64748B", width=2, text="天氣 Context", text_pos="above")

    # Vector DB -> LLM Advisor
    draw_arrow(720, 490, 570, 550, color="#64748B", width=2, text="商品清單 (15件)", text_pos="above")

    # LLM Advisor -> Scoring Engine
    draw_arrow(500, 650, 500, 700, color="#4F46E5", width=3)

    # Scoring Engine -> Gradio UI
    draw_arrow(500, 790, 500, 825, color="#4F46E5", width=3)

    # Footer Metadata
    draw.text((width//2, 905), "FormosaFit AI · On-Device Privacy-First System Architecture Diagram · 2026", fill="#94A3B8", font=ImageFont.truetype(font_path, 11), anchor="mm")

    # Save to file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture_diagram.png")
    image.save(output_path, "PNG")
    print(f"Diagram successfully saved to {output_path}")

if __name__ == "__main__":
    create_diagram()
