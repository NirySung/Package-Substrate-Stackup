# ==============================================================================
# SBT 基準面生成：絕對座標原生版 (支援任意層數與厚度)
# ==============================================================================

# 在這裡輸入你的層厚度數據 (um)
# 你可以隨時改成 9 層、24 層或任何組合
layer_thicknesses = [15, 18, 35, 25, 1280, 25, 35, 18, 15]

def generate_sbt_planes_final():
    doc = DocumentHelper.GetActiveDocument()
    part = doc.MainPart
    
    accumulated_z_um = 0
    num_layers = len(layer_thicknesses)
    
    print(">>> 偵測到 {} 層結構，準備生成 {} 片基準面...".format(num_layers, num_layers - 1))

    for i in range(num_layers - 1):
        thick = layer_thicknesses[i]
        accumulated_z_um -= thick  # 深度累加
        
        try:
            # 1. 直接計算空間中的絕對位置 (um 轉 mm)
            z_mm = float(accumulated_z_um) / 1000.0
            origin = Point.Create(0, 0, z_mm)
            
            # 2. 定義平面的座標框架 (XY 平面，法向量為 Z)
            frame = Frame.Create(origin, Direction.DirX, Direction.DirY)
            geom_plane = Plane.Create(frame)
            
            # 3. 使用原生指令建立基準面 (最穩定的 API 調用)
            name = "L{}_L{}_Z{}um".format(i+1, i+2, abs(accumulated_z_um))
            new_datum = DatumPlane.Create(part, name, geom_plane)
            
            if new_datum:
                print("成功生成: " + name)
            
        except Exception as ex:
            print("第 {} 片面生成出錯: {}".format(i+1, str(ex)))

    print(">>> 基準面全部生成完畢！請手動執行 Split Body。")

# 執行指令
generate_sbt_planes_final()
