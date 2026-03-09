# ==============================================================================
# SBT 9層全自動化：順序修正版 (由底向上對齊 SR2 -> SR1)
# ==============================================================================

# [名稱, 厚度, 顏色] 
# 注意：這裡我們維持由頂部到底部的邏輯清單，但在命名時會根據你的模型位置調整
layer_configs = [
    ["SR1",  15,   "DarkGreen"],
    ["CuL1", 18,   "Yellow"],
    ["PP1",  35,   "Magenta"],
    ["CuL2", 25,   "Yellow"],
    ["Core", 1280, "Blue"],
    ["CuL3", 25,   "Yellow"],
    ["PP2",  35,   "Magenta"],
    ["CuL4", 18,   "Yellow"],
    ["SR2",  15,   "DarkGreen"]
]

def finalize_9layers_correct_order():
    doc = DocumentHelper.GetActiveDocument()
    part = doc.MainPart
    
    # 1. 取得所有 Body
    all_bodies = list(part.Bodies)
    
    if len(all_bodies) != len(layer_configs):
        print("數量不符：模型有 {} 塊，清單有 {} 層".format(len(all_bodies), len(layer_configs)))
        return

    # 2. 順序對調修正：
    # 如果剛才 SR2 變成了 SR1，代表我們不應該 reverse()，或者應該反過來處理
    # 我們這裡直接移除 reverse() 或是根據結果調整
    # 測試建議：先註解掉下面這行看看
    # all_bodies.reverse() 

    print(">>> 正在修正命名順序...")

    for i in range(len(layer_configs)):
        target_body = all_bodies[i]
        # 這裡我們讀取設定檔，確保對應關係正確
        name, thick, color_str = layer_configs[i]
        
        # 執行命名
        target_body.Name = name
        
        # 執行上色與分組
        body_sel = Selection.Create(target_body)
        NamedSelection.Create(body_sel, Selection.Empty(), name)
        
        try:
            options = SetColorOptions()
            options.FaceColorTarget = FaceColorTarget.Body
            ColorHelper.SetColor(body_sel, options, Color.FromName(color_str))
        except:
            pass
        
        print("已完成: " + name)

# 執行
finalize_9layers_correct_order()
