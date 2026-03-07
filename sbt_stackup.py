# ==============================================================================

# SBT Substrate Stackup 參數化幾何建立腳本 (含自動上色)

# 適用於：ANSYS SpaceClaim Scripting

# 使用方式：File > Scripting > Run Script File

# 

# 前置條件：

# - SpaceClaim 內部單位設定為 µm

# - 已在 Z = 0 平面手動建立多個 Surface（封裝外型輪廓）

# - 所有 Surface 黏在一起（Shared Topology）

# 

# 流程：

# 1. 第一層 SR：每個 Surface 各自往 -Z extrude → 多個獨立 body

# 2. 第二層開始：outline_ref 每層重新 Copy → 移動到 z_current → extrude → 一個獨立 body

# 3. 每層自動上色（依層名稱關鍵字）

# 4. 最後：套用 Share Topology

# 

# 顏色規則：

# sr   → 綠色  (Forest Green)

# cu   → 銅色  (Copper)

# pp   → 藍色  (Dodger Blue)

# core → 粉色  (Hot Pink)

# 

# 單位：µm（SpaceClaim 顯示單位需設定為 µm）

# ==============================================================================

# ==============================================================================

# 使用者參數設定區（只需修改這裡）

# ==============================================================================

# === Stackup 定義 ===

# 順序從上到下（第一筆 = 最頂層 SR）

# name     : 層的名稱（會顯示在 Structure Tree 和 Mechanical Named Selection）

# thickness: 層的厚度 (µm)

stackup = [
{“name”: “sr_top”,  “thickness”: 25 },   # Solder Resist Top
{“name”: “cu_1”,    “thickness”: 35 },   # Copper Layer 1
{“name”: “pp_1”,    “thickness”: 100},   # Prepreg 1
{“name”: “cu_2”,    “thickness”: 35 },   # Copper Layer 2
{“name”: “core_1”,  “thickness”: 200},   # Core
{“name”: “cu_3”,    “thickness”: 35 },   # Copper Layer 3
{“name”: “pp_2”,    “thickness”: 100},   # Prepreg 2
{“name”: “cu_4”,    “thickness”: 35 },   # Copper Layer 4
{“name”: “sr_bot”,  “thickness”: 25 },   # Solder Resist Bot
]

# ==============================================================================

# 以下請勿修改

# ==============================================================================

def get_all_surfaces(part):
“””
取得目前 Part 內所有 Surface Bodies
“””
surfaces = []
for body in part.Bodies:
if body.Shape.BodyType == BodyType.Sheet:
surfaces.append(body)
return surfaces

def apply_layer_color(body, layer_name):
“””
根據層名稱關鍵字設定顏色
sr   → 綠色  (Forest Green)
cu   → 銅色  (Copper)
pp   → 藍色  (Dodger Blue)
core → 粉色  (Hot Pink)
“””
name = layer_name.lower()
if “sr” in name:
body.SetColor(None, Color.FromArgb(255, 34,  139, 34 ))  # Forest Green
elif “core” in name:
body.SetColor(None, Color.FromArgb(255, 255, 105, 180))  # Hot Pink
elif “pp” in name:
body.SetColor(None, Color.FromArgb(255, 30,  144, 255))  # Dodger Blue
elif “cu” in name:
body.SetColor(None, Color.FromArgb(255, 184, 115, 51 ))  # Copper

def create_sbt_stackup(stackup):
“””
主函式：
1. 第一層：每個 Surface 各自 extrude → 多個獨立 body
2. 第二層開始：每層從 outline_ref Copy → 移動到 z_current → extrude → 一個獨立 body
3. 每層自動上色
4. 最後：套用 Share Topology
“””

```
doc  = DocumentHelper.GetActiveDocument()
part = doc.MainPart

print("=" * 55)
print("SBT Substrate Stackup 建立開始")
print("=" * 55)

# --- 取得所有 Surface ---
surfaces = get_all_surfaces(part)
if not surfaces:
    print("錯誤：找不到任何 Surface Body！請先在 Z = 0 建立 2D 輪廓。")
    return

print("找到 {} 個 Surface".format(len(surfaces)))
print("-" * 55)

z_current    = 0.0
outline_face = None   # 外框參考面（永久保留，每層 Copy 使用）
all_bodies   = []     # 收集所有建立的 body，最後套用 Share Topology

for i, layer in enumerate(stackup):
    name      = layer["name"]
    thickness = layer["thickness"]
    z_start   = z_current
    z_end     = z_current - thickness  # 往 -Z 方向

    # 建立 Component
    comp = part.Components.Create(name)

    # -------------------------------------------------------
    # 第一層（SR Top）：每個 Surface 各自 extrude → 多個獨立 body
    # -------------------------------------------------------
    if i == 0:
        print("  [第一層 - 多 body]")

        for j, surface in enumerate(surfaces):
            # 複製 Surface
            copied = surface.Copy()

            # 移動到正確的 Z 位置（第一層 z_current = 0，不需移動）
            if z_current != 0.0:
                Move.Translate(
                    Selection.Create(copied),
                    Direction.DirZ.Negate(),
                    z_current
                )

            # Extrude → 獨立 body
            extrude_result = ExtrudeCreator.Create(
                Selection.Create(copied),
                Direction.DirZ.Negate(),
                thickness,
                ExtrudeType.NewBody
            )

            body = extrude_result.CreatedBodies[0]
            body_name = "{}_{}".format(name, j + 1)
            body.SetName(body_name)
            body.Parent = comp

            # 上色
            apply_layer_color(body, name)

            # Named Group
            named_group = NamedSelection.Create(
                Selection.Create(body),
                SelectionType.GeomBody
            )
            named_group.Name = body_name

            all_bodies.append(body)
            print("    建立：{}".format(body_name))

        print("  {} 共 {} 個 body".format(name, len(surfaces)))

    # -------------------------------------------------------
    # 第二層開始：每層從 outline_ref Copy → 移動 → extrude → 一個獨立 body
    # -------------------------------------------------------
    else:
        # 第二層時建立 outline_ref（永久保留在 Z=0，不移動）
        if i == 1:
            print("-" * 55)
            print("  [建立外框參考面 outline_ref]")

            copied_surfaces = [s.Copy() for s in surfaces]

            if len(copied_surfaces) > 1:
                unite_result = BooleanUnite.Create(
                    Selection.Create(copied_surfaces[0]),
                    Selection.Create(copied_surfaces[1:])
                )
                outline_face = unite_result.CreatedBodies[0]
            else:
                outline_face = copied_surfaces[0]

            outline_face.SetName("outline_ref")
            print("  outline_ref 建立完成（位於 Z = 0）")
            print("-" * 55)

        # 每層重新從 outline_ref Copy 一個新的面
        layer_face = outline_face.Copy()

        # 移動到該層的 z_start（累積的 z_current）
        Move.Translate(
            Selection.Create(layer_face),
            Direction.DirZ.Negate(),
            z_current
        )

        # Extrude → 獨立 body
        extrude_result = ExtrudeCreator.Create(
            Selection.Create(layer_face),
            Direction.DirZ.Negate(),
            thickness,
            ExtrudeType.NewBody
        )

        body = extrude_result.CreatedBodies[0]
        body.SetName(name)
        body.Parent = comp

        # 上色
        apply_layer_color(body, name)

        # Named Group
        named_group = NamedSelection.Create(
            Selection.Create(body),
            SelectionType.GeomBody
        )
        named_group.Name = name

        all_bodies.append(body)
        print("  [單一 body]  {:12s}  厚度: {:6.0f} µm  Z: {:.0f} ~ {:.0f} µm".format(
            name, thickness, z_start, z_end))

    z_current -= thickness

# --- 隱藏 outline_ref 參考面 ---
try:
    outline_face.SetVisibility(False)
except:
    pass

# -------------------------------------------------------
# 最後：套用 Share Topology
# 讓所有 body 在相鄰面共享結點，匯入 Mechanical 後網格共結點
# -------------------------------------------------------
print("-" * 55)
print("  [套用 Share Topology]")
try:
    part.ShareTopology = ShareTopologyType.Share
    ShareTopology.FindAndFix(Selection.Create(all_bodies))
    print("  Share Topology 套用完成！")
except Exception as e:
    print("  Share Topology 錯誤：{}".format(str(e)))

print("-" * 55)
print("總厚度：{:.0f} µm".format(abs(z_current)))
print("SBT Substrate Stackup 建立完成！")
print("=" * 55)
```

# ==============================================================================

# 執行

# ==============================================================================

create_sbt_stackup(stackup)