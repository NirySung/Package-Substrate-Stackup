# ==============================================================================
# SBT 基準面生成：支援 24 層 (或任意層數)
# ==============================================================================

# 在這裡填入你的 24 層厚度數值 (um)
# 範例：[L1_thick, L2_thick, ..., L24_thick]
layer_thicknesses = [
    25, 35, 10, 15, 20, 25, 30, 35, # 1-8 層
    10, 15, 20, 25, 30, 35, 10, 15, # 9-16 層
    20, 25, 30, 35, 10, 15, 20, 25  # 17-24 層
]

def generate_multi_layer_planes():
    doc = DocumentHelper.GetActiveDocument()
    
    # 取得起始選取 (請點選總高實體的頂面)
    current_sel = Window.ActiveWindow.ActiveContext.Selection
    if current_sel.Count == 0:
        base_ref = Selection.Create(doc.MainPart)
    else:
        base_ref = Selection.Create(current_sel[0])

    accumulated_z_um = 0
    print(">>> 開始為 {} 層結構生成基準面...".format(len(layer_thicknesses)))

    # 生成 (N-1) 個基準面
    for i in range(len(layer_thicknesses) - 1):
        thick = layer_thicknesses[i]
        accumulated_z_um -= thick
        
        try:
            plane_result = DatumPlaneCreator.Create(base_ref, False)
            if plane_result.CreatedPlanes.Count > 0:
                new_plane = plane_result.CreatedPlanes[0]
                
                # 移動位置 (除以 1000 修正 V241 API 的 mm/um 誤差)
                options = MoveOptions()
                move_dist = float(accumulated_z_um) / 1000.0
                Move.Translate(Selection.Create(new_plane), Direction.DirZ, move_dist, options)
                
                new_plane.Name = "Cutter_L{}_L{}_Z{}um".format(i+1, i+2, accumulated_z_um)
            else:
                print("警告：第 {} 片面建立失敗".format(i+1))
                
        except Exception as ex:
            print("錯誤: {}".format(str(ex)))
            break

    print(">>> 24 層切割面全部生成完畢！")

# 執行
generate_multi_layer_planes()
