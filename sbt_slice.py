# ==============================================================================
# SBT 基準面生成：正向座標修正版 (從最底層 SR2 開始向上堆疊)
# ==============================================================================

layer_info = [
    ["SR1", 15],
    ["Cu1", 18],
    ["PP1", 35],
    ["Cu2", 25],
    ["Core", 1280],
    ["Cu3", 25],
    ["PP2", 35],
    ["Cu4", 18],
    ["SR2", 15]
]

def generate_sbt_planes_from_bottom():
    doc = DocumentHelper.GetActiveDocument()
    part = doc.MainPart
    
    # 總厚度檢查
    total_thickness_um = sum(item[1] for item in layer_info)
    print("--------------------------------------------------")
    print(">>> SBT 結構資訊總覽 (由下往上生成)：")
    print(">>> 總層數: {} 層 / 總厚度: {} um".format(len(layer_info), total_thickness_um))
    print("--------------------------------------------------")

    accumulated_z_um = 0
    
    # 使用 [::-1] 將清單反轉，這樣會從 SR2 開始讀取
    reversed_layers = layer_info[::-1]
    num_layers = len(reversed_layers)
    
    # 只需要生成 (層數-1) 片面
    for i in range(num_layers - 1):
        name_label = reversed_layers[i][0] # 這一層的名稱
        thick = reversed_layers[i][1]      # 這一層的厚度
        
        accumulated_z_um += thick
        
        try:
            z_mm = float(accumulated_z_um) / 1000.0
            origin = Point.Create(0, 0, z_mm)
            frame = Frame.Create(origin, Direction.DirX, Direction.DirY)
            geom_plane = Plane.Create(frame)
            
            # 命名顯示：現在 L1 就會是靠近 Z=0 的那片面（SR2 與 PP2 的交界）
            name = "Datum_Above_{}_Z{}um".format(name_label, int(accumulated_z_um))
            new_datum = DatumPlane.Create(part, name, geom_plane)
            
            if new_datum:
                print("成功生成基準面: " + name + " (位於 {} 上方)".format(name_label))
            
        except Exception as ex:
            print("生成出錯: " + str(ex))

    print(">>> 基準面全部生成完畢！")

generate_sbt_planes_from_bottom()
