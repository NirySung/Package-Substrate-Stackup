# ==============================================================================
# SBT 9層全自動化：自定義命名、分組與顏色 (修正順序版)
# ==============================================================================

# 1. 依照你指定的名稱與厚度順序 (L1 -> L9)
# 格式: (名稱, R, G, B)
layer_configs = [
    ("SR1", 0, 128, 64),     # 深綠 (L1)
    ("CuL1", 255, 255, 0),   # 黃色 (L2)
    ("PP1", 0, 0, 255),      # 藍色 (L3)
    ("CuL2", 255, 255, 0),   # 黃色 (L4)
    ("Core", 255, 0, 255),   # 洋紅 (L5)
    ("CuL3", 255, 255, 0),   # 黃色 (L6)
    ("PP2", 0, 0, 255),      # 藍色 (L7)
    ("Cu4", 255, 255, 0),    # 黃色 (L8)
    ("SR2", 0, 128, 64)      # 深綠 (L9)
]

def finalize_9layers_custom_naming():
    doc = DocumentHelper.GetActiveDocument()
    part = doc.MainPart
    
    # 2. 取得實體並修正索引順序 (由底向上翻轉)
    all_bodies = list(part.Bodies)
    if len(all_bodies) < len(layer_configs):
        print("!!! 錯誤：實體數量不足 9 塊，請確認切割是否成功 !!!")
        return
    
    all_bodies.reverse()

    print(">>> 正在套用自定義命名、Groups 與辨識顏色...")

    for i in range(len(layer_configs)):
        target_body = all_bodies[i]
        name, r, g, b = layer_configs[i]
        
        # A. 重新命名實體
        target_body.Name = name
        
        # B. 建立 Named Selection Group
        body_sel = Selection.Create(target_body)
        NamedSelection.Create(body_sel, Selection.Empty(), name)
        
        # C. 修改 Body 顏色 (ARGB)
        options = SetColorOptions()
        options.FaceColorTarget = FaceColorTarget.Body
        ColorHelper.SetColor(body_sel, options, Color.FromArgb(255, r, g, b))
        
        print("完成: {} (已分組並上色)".format(name))

    print(">>> 9 層自動化處理完成！")

# 執行
finalize_9layers_custom_naming()
