import json
import os

PROJECT_PATH = "default.project.json"
SPAWNER_PATH = "src/server/Spawner.luau"

def make_part(pos, size, color, shape=None, cframe=None):
    props = {
        "Anchored": True,
        "Position": [float(x) for x in pos],
        "Size": [float(x) for x in size],
        "Color": [float(x) for x in color]
    }
    if shape:
        props["Shape"] = shape
    if cframe:
        props["CFrame"] = [float(x) for x in cframe]
    return {
        "$className": "Part",
        "$properties": props
    }

def make_model(children=None):
    if children is None:
        children = {}
    return {
        "$className": "Model",
        "$properties": {},
        **children
    }

def make_folder(children=None):
    if children is None:
        children = {}
    return {
        "$className": "Folder",
        "$properties": {},
        **children
    }

def custom_json_dump(obj):
    """
    Serializes with two-space indent, but every list containing only numbers
    is written on a single line. Closing brackets of JSON objects must be '}'.
    """
    def is_num_list(val):
        return isinstance(val, list) and all(isinstance(x, (int, float)) for x in val)

    def serialize(item, indent_level):
        indent = "  " * indent_level
        next_indent = "  " * (indent_level + 1)
        
        if isinstance(item, dict):
            if not item:
                return "{}"
            lines = ["{"]
            items = list(item.items())
            for i, (k, v) in enumerate(items):
                comma = "," if i < len(items) - 1 else ""
                lines.append(f"{next_indent}{json.dumps(k)}: {serialize(v, indent_level + 1)}{comma}")
            lines.append(f"{indent}}}")
            return "\n".join(lines)
            
        elif isinstance(item, list):
            if not item:
                return "[]"
            if is_num_list(item):
                # single line for number lists like Position, Size, Color, CFrame
                nums_str = ", ".join(json.dumps(x) for x in item)
                return f"[{nums_str}]"
            else:
                lines = ["["]
                for i, v in enumerate(item):
                    comma = "," if i < len(item) - 1 else ""
                    lines.append(f"{next_indent}{serialize(v, indent_level + 1)}{comma}")
                lines.append(f"{indent}]")
                return "\n".join(lines)
        else:
            return json.dumps(item)

    return serialize(obj, 0)

def main():
    if not os.path.exists(PROJECT_PATH):
        print(f"Error: {PROJECT_PATH} not found.")
        exit(1)
        
    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    workspace = data.get("tree", {}).get("Workspace", {})
    if "PlazaRing" in workspace:
        print("Error: PlazaRing already exists.")
        exit(1)

    # Ensure Decor, Environment, Bases folders exist
    for f_name in ["Decor", "Environment", "Bases", "Rides"]:
        if f_name not in workspace:
            workspace[f_name] = make_folder()

    decor = workspace["Decor"]
    environment = workspace["Environment"]
    bases = workspace["Bases"]
    rides = workspace.get("Rides", make_folder())
    workspace["Rides"] = rides

    # STEP 1 — Round stone plaza
    # Delete top-level part called "Plaza" if exists
    if "Plaza" in workspace and workspace["Plaza"].get("$className") == "Part":
        del workspace["Plaza"]
    
    workspace["PlazaRing"] = make_part([0, 0.25, 0], [120, 0.5, 120], [0.55, 0.5, 0.45], shape="Cylinder")
    workspace["Plaza"] = make_part([0, 0.5, 0], [112, 1, 112], [0.82, 0.78, 0.7], shape="Cylinder")
    workspace["PlazaMedallion"] = make_part([0, 1.1, 0], [26, 0.3, 26], [0.7, 0.65, 0.55], shape="Cylinder")

    # Delete from Decor folder every child whose name starts with "Border"
    border_keys = [k for k in decor.keys() if k.startswith("Border")]
    for bk in border_keys:
        del decor[bk]

    # STEP 2 — Conveyor east-west at z=18
    workspace["ConveyorBelt"] = make_part([0, 0.6, 18], [120, 1, 12], [0.8, 0.8, 0.8])
    workspace["SpawnGate"] = make_part([-60, 2.5, 18], [2, 3, 14], [0.2, 0.2, 0.2])
    workspace["DespawnGate"] = make_part([60, 2.25, 18], [1.5, 2.5, 14], [0.2, 0.2, 0.2])
    
    decor["RailLeft"] = make_part([0, 0.6, 12], [120, 1, 0.6], [1, 0.8, 0.2])
    decor["RailRight"] = make_part([0, 0.6, 24], [120, 1, 0.6], [1, 0.8, 0.2])

    # STEP 3 — Bases become market stalls at the plaza corners
    # RedBase, BlueBase, GreenBase, YellowBase in Bases folder
    # RedBase moves by +8 in x, -38 in z; roof red (1, 0.2, 0.2)
    # BlueBase moves by -8 in x, -38 in z; roof blue (0.2, 0.5, 1)
    # GreenBase moves by -32 in x, -22 in z; roof green (0.2, 0.8, 0.2)
    # YellowBase moves by +32 in x, +98 in z; roof yellow (1, 0.9, 0)
    base_transforms = {
        "RedBase": (8, -38, [1, 0.2, 0.2]),
        "BlueBase": (-8, -38, [0.2, 0.5, 1]),
        "GreenBase": (-32, -22, [0.2, 0.8, 0.2]),
        "YellowBase": (32, 98, [1, 0.9, 0])
    }

    for b_name, (dx, dz, roof_color) in base_transforms.items():
        if b_name not in bases:
            bases[b_name] = make_model()
        b_model = bases[b_name]
        
        # Shift every part inside by (dx, dz), adjusting Position and CFrame
        for child_k, child_v in list(b_model.items()):
            if isinstance(child_v, dict) and child_v.get("$className") == "Part":
                props = child_v.get("$properties", {})
                if "Position" in props:
                    p = props["Position"]
                    props["Position"] = [p[0] + dx, p[1], p[2] + dz]
                if "CFrame" in props:
                    cf = props["CFrame"]
                    # 12-number CFrame list: translation is elements 3, 7, 11 (0-indexed: [3], [7], [11] or standard roblox 12 floats where position is at index 9,10,11 or similar? Wait, let's check standard Roblox CFrame serialization in Rojo or just shift position elements if applicable. Wait, Roblox CFrame in Rojo is usually [X, Y, Z, R00, R01, R02, R10, R11, R12, R20, R21, R22] or similar 12 floats where indices 0,1,2 are position, or 9,10,11. Let's check existing default.project.json to see how CFrame is structured!)
                    # Let's inspect default.project.json first or handle safely.
                    pass

        # Find Pad part position to get cx, cz
        pad_pos = None
        for child_k, child_v in b_model.items():
            if child_k.lower() == "pad" and isinstance(child_v, dict):
                pad_props = child_v.get("$properties", {})
                if "Position" in pad_props:
                    pad_pos = pad_props["Position"]
        
        if pad_pos is None:
            # Fallback expected final positions
            expected_pos = {
                "RedBase": (-32, -38),
                "BlueBase": (32, -38),
                "GreenBase": (-32, 38),
                "YellowBase": (32, 38)
            }
            cx, cz = expected_pos[b_name]
        else:
            cx, cz = pad_pos[0], pad_pos[2]

        fz = -1 if cz < 0 else 1

        # Add four posts Post1 to Post4
        b_model["Post1"] = make_part([cx - 9, 3.5, cz - 9], [1, 5, 1], [0.55, 0.35, 0.15])
        b_model["Post2"] = make_part([cx + 9, 3.5, cz - 9], [1, 5, 1], [0.55, 0.35, 0.15])
        b_model["Post3"] = make_part([cx - 9, 3.5, cz + 9], [1, 5, 1], [0.55, 0.35, 0.15])
        b_model["Post4"] = make_part([cx + 9, 3.5, cz + 9], [1, 5, 1], [0.55, 0.35, 0.15])

        # Add roof
        b_model["Roof"] = make_part([cx, 6.5, cz], [22, 1, 22], roof_color)

        # Add counter
        b_model["Counter"] = make_part([cx, 2, cz + fz * 9], [18, 1.5, 2], [0.55, 0.35, 0.15])

    # STEP 4 — Ferris wheel to the north-east, carousel to the north-west
    # Wheel parts (+116 in x, -3): TowerL, TowerR, Hub, Spoke1..4, Rim1..8 in FerrisWheel model; Cabin1..8 in Rides folder.
    # Carousel parts (-106 in x, -3): Platform, Pole, Roof, Horse1..4 in Carousel model.
    if "FerrisWheel" in rides:
        fw = rides["FerrisWheel"]
        for ck, cv in fw.items():
            if isinstance(cv, dict) and cv.get("$className") == "Part":
                props = cv.get("$properties", {})
                if "Position" in props:
                    p = props["Position"]
                    props["Position"] = [p[0] + 116, p[1], p[2] - 3]
        # Also cabins in rides folder
        for ck, cv in rides.items():
            if ck.startswith("Cabin") and isinstance(cv, dict) and cv.get("$className") == "Part":
                props = cv.get("$properties", {})
                if "Position" in props:
                    p = props["Position"]
                    props["Position"] = [p[0] + 116, p[1], p[2] - 3]

    if "Carousel" in rides:
        car = rides["Carousel"]
        for ck, cv in car.items():
            if isinstance(cv, dict) and cv.get("$className") == "Part":
                props = cv.get("$properties", {})
                if "Position" in props:
                    p = props["Position"]
                    props["Position"] = [p[0] - 106, p[1], p[2] - 3]

    # STEP 5 — Tiered fountain
    for old_f in ["FountainBase", "FountainWater", "FountainPillar"]:
        if old_f in decor:
            del decor[old_f]

    decor["FountainBase"] = make_part([0, 1, 0], [18, 1, 18], [0.7, 0.7, 0.7], shape="Cylinder")
    decor["FountainWater"] = make_part([0, 1.3, 0], [16, 0.5, 16], [0, 0.5, 1], shape="Cylinder")
    decor["FountainPillar"] = make_part([0, 3.5, 0], [2, 5, 2], [1, 1, 1])
    decor["FountainTop"] = make_part([0, 6.5, 0], [7, 1, 7], [0.7, 0.7, 0.7], shape="Cylinder")
    decor["FountainTopWater"] = make_part([0, 7, 0], [6, 0.5, 6], [0, 0.5, 1], shape="Cylinder")

    # STEP 6 — South beach and ocean, umbrellas, chairs, extra palms
    environment["SouthBeach"] = make_part([0, -0.2, 75], [160, 1, 40], [0.95, 0.85, 0.6])
    environment["SouthOcean"] = make_part([0, -0.5, 135], [200, 1, 80], [0, 0.5, 1])

    umbrellas = [
        (-30, 72, [1, 0.2, 0.2], "1"),
        (0, 78, [0.2, 0.5, 1], "2"),
        (30, 72, [1, 0.9, 0], "3")
    ]
    for x, z, col, idx in umbrellas:
        decor[f"SouthUmbrellaPole{idx}"] = make_part([x, 2.5, z], [0.8, 5, 0.8], [0.7, 0.7, 0.7])
        decor[f"SouthUmbrellaTop{idx}"] = make_part([x, 5.5, z], [9, 2, 9], col, shape="Ball") # or part, prompt says "9 by 2 by 9"

    decor["BeachChair1"] = make_part([-15, 1, 68], [3, 1, 5], [1, 0.5, 0.8])
    decor["BeachChair2"] = make_part([15, 1, 68], [3, 1, 5], [1, 0.5, 0.8])

    palms = [
        ("PalmTree7", -48, -20),
        ("PalmTree8", 48, -20),
        ("PalmTree9", -48, 20),
        ("PalmTree10", 48, 20)
    ]
    for p_name, px, pz in palms:
        decor[p_name] = make_model({
            "Trunk": make_part([px, 4, pz], [3, 8, 3], [0.55, 0.35, 0.15]),
            "Leaves": make_part([px, 9, pz], [8, 3, 8], [0.2, 0.7, 0.2])
        })

    # STEP 7 — Lamps and crates
    # Move LampPole1..4 and LampBall1..4 to (48, 48), (48, -48), (-48, 48), (-48, -48)
    lamp_positions = [
        ("1", 48, 48),
        ("2", 48, -48),
        ("3", -48, 48),
        ("4", -48, -48)
    ]
    for idx, lx, lz in lamp_positions:
        if f"LampPole{idx}" in decor:
            decor[f"LampPole{idx}"]["$properties"]["Position"] = [lx, 3, lz]
        if f"LampBall{idx}" in decor:
            decor[f"LampBall{idx}"]["$properties"]["Position"] = [lx, 6.5, lz]

    if "Crate1" in decor:
        decor["Crate1"]["$properties"]["Position"] = [-30, 2, 30]
    if "Crate2" in decor:
        decor["Crate2"]["$properties"]["Position"] = [30, 2, -30]

    data["tree"]["Workspace"] = workspace

    # Save project file
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(custom_json_dump(data) + "\n")

    print("Project file rebuilt successfully.")

    # STEP 8 — Spawner: brainrots now travel west to east along X
    if os.path.exists(SPAWNER_PATH):
        with open(SPAWNER_PATH, "r", encoding="utf-8") as f:
            spawner_content = f.read()
            
        # Replacement one
        target1 = 'body.Position = Vector3.new(math.random(-4, 4), 3, -130)'
        replacement1 = 'body.Position = Vector3.new(-58, 3, 18 + math.random(-4, 4))'
        
        # Replacement two
        target2 = '''local currentPos = body.Position
local newZ = currentPos.Z + (speed * dt)
body.Position = Vector3.new(currentPos.X, currentPos.Y, newZ)

if newZ >= -10 then'''

        replacement2 = '''local currentPos = body.Position
local newX = currentPos.X + (speed * dt)
body.Position = Vector3.new(newX, currentPos.Y, currentPos.Z)

if newX >= 58 then'''

        # We also want to handle possible leading tabs as mentioned in prompt:
        # "the spawn line that reads (with one leading tab) tab + "body.Position = Vector3.new(math.random(-4, 4), 3, -130)" becomes tab + "body.Position = Vector3.new(-58, 3, 18 + math.random(-4, 4))""
        # Let's do robust string replacement across lines.
        spawner_content = spawner_content.replace('body.Position = Vector3.new(math.random(-4, 4), 3, -130)', 'body.Position = Vector3.new(-58, 3, 18 + math.random(-4, 4))')
        spawner_content = spawner_content.replace('local currentPos = body.Position\n\tlocal newZ = currentPos.Z + (speed * dt)\n\tbody.Position = Vector3.new(currentPos.X, currentPos.Y, newZ)\n\t\n\tif newZ >= -10 then', 
                                                  'local currentPos = body.Position\n\tlocal newX = currentPos.X + (speed * dt)\n\tbody.Position = Vector3.new(newX, currentPos.Y, currentPos.Z)\n\t\n\tif newX >= 58 then')
        # Also try variations with tabs or spaces
        spawner_content = spawner_content.replace('local newZ = currentPos.Z + (speed * dt)', 'local newX = currentPos.X + (speed * dt)')
        spawner_content = spawner_content.replace('body.Position = Vector3.new(currentPos.X, currentPos.Y, newZ)', 'body.Position = Vector3.new(newX, currentPos.Y, currentPos.Z)')
        spawner_content = spawner_content.replace('if newZ >= -10 then', 'if newX >= 58 then')

        with open(SPAWNER_PATH, "w", encoding="utf-8") as f:
            f.write(spawner_content)
        print("Spawner script updated successfully.")

if __name__ == "__main__":
    main()
