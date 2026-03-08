# ==============================================================================
# SBT 9層自動化：實體命名 + Named Selection (修正順序版)
# ==============================================================================

# 1. 依照你原本「視覺上」從頂到低的順序定義
# 如果執行後發現 SR_Top 跑到最下面，程式會自動處理
layer_names = [
    "SR1",  # 15um (L1)
    "CuL1",   # 18um (L2)
    "PP1",      # 35um (L3)
    "CuL2",    # 25um (L4)
    "Core",   # 1280um (L5)
    "CuL3",    # 25um (L6)
    "PP2",      # 35um (L7)
    "Cu4",   # 18um (L8)
    "SR2"       # 15um (L9)
]

def rename_and_group_9layers_fixed():
    doc = DocumentHelper.GetActiveDocument()
    part = doc.MainPart
    
    # 2. 取得目前所有的實體 (Bodies)
    all_bodies = list(part.Bodies) # 轉成 list 方便操作
    
    if len(all_bodies) < len(layer_names):
        print("!!! 錯誤：實體數量不足 9 塊 !!!")
        return

    # 關鍵修正：將實體清單反轉，以符合結構樹由底向上的索引邏輯
    all_bodies.reverse() 

    print(">>> 正在以修正後的順序執行命名與分組...")

    for i in range(len(layer_names)):
        target_body = all_bodies[i]
        new_name = layer_names[i]
        
        # A. 重新命名實體
        target_body.Name = new_name
        
        # B. 建立 Named Selection Group
        body_selection = Selection.Create(target_body)
        NamedSelection.Create(body_selection, Selection.Empty(), new_name)
        
        print("完成: {} -> Group: {}".format(new_name, new_name))

    print(">>> 順序修正完成！請確認結構樹與 Groups。")

# 執行
rename_and_group_9layers_fixed()
