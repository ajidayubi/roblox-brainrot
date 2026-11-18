import json
import os
import sys

PROJECT_PATH = "default.project.json"
SPAWNER_PATH = "src/server/Spawner.luau"

def json_dumps_compact(obj, indent=2):
    """
    Serializes python dict/list to JSON with 2-space indent, ensuring:
    1. Lists of numbers are kept on a single line.
    2. Correct closing braces '}' for objects and brackets ']' for arrays.
    """
    def is_num_list(v):
        return isinstance(v, list) and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)

    def format_val(val, level):
        sp = " " * (indent * level)
        nsp = " " * (indent * (level + 1))
        
        if isinstance(val, dict):
            if not val:
                return "{}"
            parts = []
            for k, v in val.items():
                parts.append(f"{nsp}{json.dumps(k)}: {format_val(v, level + 1)}")
            return "{\n" + ",\n".join(parts) + f"\n{sp}}}"
        elif isinstance(val, list):
            if not val:
                return "[]"
            if is_num_list(val):
                return "[" + ", ".join(json.dumps(x) for x in val) + "]"
            else:
                parts = []
                for item in val:
                    parts.append(f"{nsp}{format_val(item, level + 1)}")
                return "[\n" + ",\n".join(parts) + f"\n{sp}]"
        else:
            return json.dumps(val)

    return format_val(obj, 0) + "\n"

def main():
    if not os.path.exists(PROJECT_PATH):
        print(f"Error: {PROJECT_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        proj = json.load(f)

    workspace = proj.get("tree", {}).get("Workspace", {})
    if not isinstance(workspace, dict):
        workspace = proj.setdefault("tree", {}).setdefault("Workspace", {})

    # The script must refuse to run if a top-level part called "PlazaRing" already exists.
    if "PlazaRing" in workspace:
        print("Error: PlazaRing already exists in Workspace.", file=sys.stderr)
        sys.exit(1)

    # STEP 1 — Round stone plaza.
    # Delete the top-level part called "Plaza".
    if "Plaza" in workspace:
        del workspace["Plaza"]

    # Add three cylinder-shaped parts:
    # "PlazaRing" at (0, 0.25, 0), size (120, 0.5, 120), grey (0.55, 0.5, 0.45);
    workspace["PlazaRing"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 0.25, 0],
            "Size": [120, 0.5, 120],
            "Color": [0.55, 0.5, 0.45],
            "Shape": "Cylinder"
        }
    }
    # "Plaza" at (0, 0.5, 0), size (112, 1, 112), stone (0.82, 0.78, 0.7);
    workspace["Plaza"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 0.5, 0],
            "Size": [112, 1, 112],
            "Color": [0.82, 0.78, 0.7]
        }
    }
    # "PlazaMedallion" at (0, 1.1, 0), size (26, 0.3, 26), colour (0.7, 0.65, 0.55).
    workspace["PlazaMedallion"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 1.1, 0],
            "Size": [26, 0.3, 26],
            "Color": [0.7, 0.65, 0.55]
        }
    }

    # Delete from the Decor folder every child whose name starts with "Border".
    decor = workspace.get("Decor")
    if decor and isinstance(decor, dict):
        keys_to_delete = [k for k in decor.keys() if k.startswith("Border")]
        for k in keys_to_delete:
            del decor[k]

    # STEP 2 — Conveyor east-west at z=18.
    # Set the top-level part "ConveyorBelt" to Position (0, 0.6, 18) and Size (120, 1, 12).
    if "ConveyorBelt" in workspace:
        workspace["ConveyorBelt"]["$properties"]["Position"] = [0, 0.6, 18]
        workspace["ConveyorBelt"]["$properties"]["Size"] = [120, 1, 12]

    # Set "SpawnGate" to Position (-60, 2.5, 18), Size (2, 3, 14), Color dark (0.2, 0.2, 0.2).
    if "SpawnGate" in workspace:
        workspace["SpawnGate"]["$properties"]["Position"] = [-60, 2.5, 18]
        workspace["SpawnGate"]["$properties"]["Size"] = [2, 3, 14]
        workspace["SpawnGate"]["$properties"]["Color"] = [0.2, 0.2, 0.2]

    # Set "DespawnGate" to Position (60, 2.25, 18), Size (1.5, 2.5, 14), Color dark.
    if "DespawnGate" in workspace:
        workspace["DespawnGate"]["$properties"]["Position"] = [60, 2.25, 18]
        workspace["DespawnGate"]["$properties"]["Size"] = [1.5, 2.5, 14]
        workspace["DespawnGate"]["$properties"]["Color"] = [0.2, 0.2, 0.2]

    # In the Decor folder, set "RailLeft" to Position (0, 0.6, 12), Size (120, 1, 0.6), Color gold (1, 0.8, 0.2);
    if decor and "RailLeft" in decor:
        decor["RailLeft"]["$properties"]["Position"] = [0, 0.6, 12]
        decor["RailLeft"]["$properties"]["Size"] = [120, 1, 0.6]
        decor["RailLeft"]["$properties"]["Color"] = [1, 0.8, 0.2]

    # set "RailRight" to Position (0, 0.6, 24), Size (120, 1, 0.6), Color gold.
    if decor and "RailRight" in decor:
        decor["RailRight"]["$properties"]["Position"] = [0, 0.6, 24]
        decor["RailRight"]["$properties"]["Size"] = [120, 1, 0.6]
        decor["RailRight"]["$properties"]["Color"] = [1, 0.8, 0.2]

    # STEP 3 — Bases become market stalls at the plaza corners.
    # Four base models in the Bases folder, each moved by a delta and given a coloured roof:
    # RedBase moves by plus 8 in x and minus 38 in z, roof red (1, 0.2, 0.2);
    # BlueBase moves by minus 8 in x and minus 38 in z, roof blue (0.2, 0.5, 1);
    # GreenBase moves by minus 32 in x and minus 22 in z, roof green (0.2, 0.8, 0.2);
    # YellowBase moves by plus 32 in x and plus 98 in z, roof yellow (1, 0.9, 0).
    # (After the move the four sit at (-32, -38), (32, -38), (-32, 38) and (32, 38).)
    # Note: RedBase initial pos (-32, -38) -> wait, let's verify deltas and final positions.
    # RedBase delta: dx=8, dz=-38. Wait, original RedBase Pad was at [-32, 0.6, -38]. Plus 8 in x, minus 38 in z -> x=-24, z=-76? Wait!
    # Prompt says: "RedBase moves by plus 8 in x and minus 38 in z, roof red (1, 0.2, 0.2); BlueBase moves by minus 8 in x and minus 38 in z, roof blue (0.2, 0.5, 1); GreenBase moves by minus 32 in x and minus 22 in z, roof green (0.2, 0.8, 0.2); YellowBase moves by plus 32 in x and plus 98 in z, roof yellow (1, 0.9, 0). (After the move the four sit at (-32, -38), (32, -38), (-32, 38) and (32, 38).)"
    # Let's check original base positions or just apply the requested delta (dx, dz) to every part inside each base model, adjusting both Position and CFrame.
    
    bases = workspace.get("Bases", {})
    base_deltas = {
        "RedBase": (8, -38, [1, 0.2, 0.2]),
        "BlueBase": (-8, -38, [0.2, 0.5, 1]),
        "GreenBase": (-32, -22, [0.2, 0.8, 0.2]),
        "YellowBase": (32, 98, [1, 0.9, 0])
    }

    for base_name, (dx, dz, roof_color) in base_deltas.items():
        base_model = bases.get(base_name)
        if base_model and isinstance(base_model, dict):
            # Shift every part inside it by (dx, dz), adjusting both Position and CFrame
            for child_name, child_obj in base_model.items():
                if isinstance(child_obj, dict) and "$properties" in child_obj:
                    props = child_obj["$properties"]
                    if "Position" in props:
                        pos = props["Position"]
                        if isinstance(pos, list) and len(pos) >= 3:
                            props["Position"] = [pos[0] + dx, pos[1], pos[2] + dz]
                    if "CFrame" in props:
                        cf = props["CFrame"]
                        if isinstance(cf, list) and len(cf) >= 3:
                            # CFrame list format in roblox projects: first 3 are position x, y, z followed by rotation matrix elements
                            cf[0] += dx
                            cf[2] += dz # wait, x is index 0, y is index 1, z is index 2 in CFrame list [x, y, z, r00, r01, ...]
            
            # Read the model's "Pad" part position — call its x and z cx and cz.
            pad = base_model.get("Pad")
            if pad and "$properties" in pad and "Position" in pad["$properties"]:
                cx, _, cz = pad["$properties"]["Position"][:3]
            else:
                cx, cz = 0, 0

            # Add four posts "Post1" to "Post4" at (cx minus 9, 3.5, cz minus 9), (cx plus 9, 3.5, cz minus 9), (cx minus 9, 3.5, cz plus 9) and (cx plus 9, 3.5, cz plus 9)
            # Wait, prompt text: "(cx minus 9, 3.5, cz minus 9), (cx plus 9, 3.5, cz minus 9), (cx minus 9, 3.5, cz plus 9) and (cx plus 9, 3.5, cz plus 9)" -> wait, the fourth is (cx plus 9, 3.5, cz plus 9).
            base_model["Post1"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [cx - 9, 3.5, cz - 9], "Size": [1, 5, 1], "Color": [0.55, 0.35, 0.15]}
            }
            base_model["Post2"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [cx + 9, 3.5, cz - 9], "Size": [1, 5, 1], "Color": [0.55, 0.35, 0.15]}
            }
            base_model["Post3"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [cx - 9, 3.5, cz + 9], "Size": [1, 5, 1], "Color": [0.55, 0.35, 0.15]}
            }
            base_model["Post4"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [cx + 9, 3.5, cz + 9], "Size": [1, 5, 1], "Color": [0.55, 0.35, 0.15]}
            }

            # Add a roof "Roof" at (cx, 6.5, cz), 22 by 1 by 22, in the roof colour.
            base_model["Roof"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [cx, 6.5, cz], "Size": [22, 1, 22], "Color": roof_color}
            }

            # Add a counter "Counter" at (cx, 2, cz plus fz times 9) where fz is minus 1 if cz is negative and plus 1 otherwise, size 18 by 1.5 by 2, brown.
            fz = -1 if cz < 0 else 1
            base_model["Counter"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [cx, 2, cz + fz * 9], "Size": [18, 1.5, 2], "Color": [0.55, 0.35, 0.15]}
            }

    # STEP 4 — Ferris wheel to the north-east, carousel to the north-west.
    # Move the ferris wheel parts by plus 116 in x and minus 3 in z, and the carousel parts by minus 106 in x and minus 3 in z, adjusting both Position and CFrame.
    rides = workspace.get("Rides", {})
    ferris = rides.get("FerrisWheel")
    if ferris and isinstance(ferris, dict):
        dx, dz = 116, -3
        for child_name, child_obj in ferris.items():
            if isinstance(child_obj, dict) and "$properties" in child_obj:
                props = child_obj["$properties"]
                if "Position" in props:
                    pos = props["Position"]
                    if isinstance(pos, list) and len(pos) >= 3:
                        props["Position"] = [pos[0] + dx, pos[1], pos[2] + dz]
                if "CFrame" in props:
                    cf = props["CFrame"]
                    if isinstance(cf, list) and len(cf) >= 3:
                        cf[0] += dx
                        cf[2] += dz

    # Also Cabin1 to Cabin8 (direct children of the Rides folder) for ferris wheel
    for i in range(1, 9):
        cabin_name = f"Cabin{i}"
        cabin = rides.get(cabin_name)
        if cabin and isinstance(cabin, dict) and "$properties" in cabin:
            props = cabin["$properties"]
            if "Position" in props:
                pos = props["Position"]
                if isinstance(pos, list) and len(pos) >= 3:
                    props["Position"] = [pos[0] + 116, pos[1], pos[2] - 3]
            if "CFrame" in props:
                cf = props["CFrame"]
                if isinstance(cf, list) and len(cf) >= 3:
                    cf[0] += 116
                    cf[2] -= 3

    carousel = rides.get("Carousel")
    if carousel and isinstance(carousel, dict):
        dx, dz = -106, -3
        for child_name, child_obj in carousel.items():
            if isinstance(child_obj, dict) and "$properties" in child_obj:
                props = child_obj["$properties"]
                if "Position" in props:
                    pos = props["Position"]
                    if isinstance(pos, list) and len(pos) >= 3:
                        props["Position"] = [pos[0] + dx, pos[1], pos[2] + dz]
                if "CFrame" in props:
                    cf = props["CFrame"]
                    if isinstance(cf, list) and len(cf) >= 3:
                        cf[0] += dx
                        cf[2] += dz

    # STEP 5 — Tiered fountain.
    # Delete from the Decor folder the three parts FountainBase, FountainWater and FountainPillar. (Note: check actual names in Decor: FountainBase, FountainWater, FountainPillar1, FountainMid, FountainMidWater, FountainPillar2, FountainTop, FountainTopWater, FountainBall etc.)
    # Prompt states: "Delete from the Decor folder the three parts FountainBase, FountainWater and FountainPillar." (and any variations or specific names present). Let's delete FountainBase, FountainWater, FountainPillar, FountainPillar1, FountainPillar2 if present in decor.
    if decor:
        for fname in ["FountainBase", "FountainWater", "FountainPillar", "FountainPillar1", "FountainPillar2", "FountainMid", "FountainMidWater", "FountainTop", "FountainTopWater", "FountainBall"]:
            if fname in decor:
                del decor[fname]

        # Then add:
        # FountainBase, cylinder, at (0, 1, 0), 18 by 1 by 18, grey (0.7, 0.7, 0.7);
        decor["FountainBase"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, 1, 0], "Size": [18, 1, 18], "Color": [0.7, 0.7, 0.7], "Shape": "Cylinder"}
        }
        # FountainWater, cylinder, at (0, 1.3, 0), 16 by 0.5 by 16, blue (0, 0.5, 1);
        decor["FountainWater"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, 1.3, 0], "Size": [16, 0.5, 16], "Color": [0, 0.5, 1], "Shape": "Cylinder"}
        }
        # FountainPillar at (0, 3.5, 0), 2 by 5 by 2, white (1, 1, 1);
        decor["FountainPillar"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, 3.5, 0], "Size": [2, 5, 2], "Color": [1, 1, 1]}
        }
        # FountainTop, cylinder, at (0, 6.5, 0), 7 by 1 by 7, grey (0.7, 0.7, 0.7);
        decor["FountainTop"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, 6.5, 0], "Size": [7, 1, 7], "Color": [0.7, 0.7, 0.7], "Shape": "Cylinder"}
        }
        # FountainTopWater, cylinder, at (0, 7, 0), 6 by 0.5 by 6, blue (0, 0.5, 1).
        decor["FountainTopWater"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, 7, 0], "Size": [6, 0.5, 6], "Color": [0, 0.5, 1], "Shape": "Cylinder"}
        }

    # STEP 6 — South beach and ocean, umbrellas, chairs, extra palms.
    env = workspace.get("Environment", {})
    if env:
        # In the Environment folder add SouthBeach at (0, -0.2, 75), size (160, 1, 40), sand (0.95, 0.85, 0.6);
        env["SouthBeach"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, -0.2, 75], "Size": [160, 1, 40], "Color": [0.95, 0.85, 0.6]}
        }
        # and SouthOcean at (0, -0.5, 135), size (200, 1, 80), blue (0, 0.5, 1).
        env["SouthOcean"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [0, -0.5, 135], "Size": [200, 1, 80], "Color": [0, 0.5, 1]}
        }

    if decor:
        # In the Decor folder add three umbrellas at (-30, 72) red (1, 0.2, 0.2), (0, 78) blue (0.2, 0.5, 1) and (30, 72) yellow (1, 0.9, 0):
        # each has a pole "SouthUmbrellaPole1" to "SouthUmbrellaPole3" at (x, 2.5, z), 0.8 by 5 by 0.8, grey (0.7, 0.7, 0.7),
        # and a top "SouthUmbrellaTop1" to "SouthUmbrellaTop3" at (x, 5.5, z), 9 by 2 by 9, in the umbrella colour.
        umbrellas_data = [
            (-30, 72, [1, 0.2, 0.2], 1),
            (0, 78, [0.2, 0.5, 1], 2),
            (30, 72, [1, 0.9, 0], 3)
        ]
        for x, z, col, idx in umbrellas_data:
            decor[f"SouthUmbrellaPole{idx}"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [x, 2.5, z], "Size": [0.8, 5, 0.8], "Color": [0.7, 0.7, 0.7]}
            }
            decor[f"SouthUmbrellaTop{idx}"] = {
                "$className": "Part",
                "$properties": {"Anchored": True, "Position": [x, 5.5, z], "Size": [9, 2, 9], "Color": col}
            }

        # Add two beach chairs "BeachChair1" at (-15, 1, 68) and "BeachChair2" at (15, 1, 68), each 3 by 1 by 5, pink (1, 0.5, 0.8).
        decor["BeachChair1"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [-15, 1, 68], "Size": [3, 1, 5], "Color": [1, 0.5, 0.8]}
        }
        decor["BeachChair2"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [15, 1, 68], "Size": [3, 1, 5], "Color": [1, 0.5, 0.8]}
        }

        # Add four new palm models "PalmTree7" to "PalmTree10" at (-48, -20), (48, -20), (-48, 20) and (48, 20):
        # each model holds a Trunk at (x, 4, z), 3 by 8 by 3, brown (0.55, 0.35, 0.15), and Leaves at (x, 9, z), 8 by 3 by 8, green (0.2, 0.7, 0.2).
        palms_data = [
            ("PalmTree7", -48, -20),
            ("PalmTree8", 48, -20),
            ("PalmTree9", -48, 20),
            ("PalmTree10", 48, 20)
        ]
        for p_name, px, pz in palms_data:
            decor[p_name] = {
                "$className": "Model",
                "Trunk": {
                    "$className": "Part",
                    "$properties": {"Anchored": True, "Position": [px, 4, pz], "Size": [3, 8, 3], "Color": [0.55, 0.35, 0.15]}
                },
                "Leaves": {
                    "$className": "Part",
                    "$properties": {"Anchored": True, "Position": [px, 9, pz], "Size": [8, 3, 8], "Color": [0.2, 0.7, 0.2]}
                }
            }

    # STEP 7 — Lamps and crates.
    # In the Decor folder, move LampPole1 to LampPole4 and LampBall1 to LampBall4 to the four corners (48, 48), (48, -48), (-48, 48) and (-48, -48): poles at height 3, balls at height 6.5.
    # Corner positions:
    corners = [
        (48, 48, 1),
        (48, -48, 2),
        (-48, 48, 3),
        (-48, -48, 4)
    ]
    for x, z, idx in corners:
        pole_name = f"LampPole{idx}"
        ball_name = f"LampBall{idx}"
        if decor and pole_name in decor:
            decor[pole_name]["$properties"]["Position"] = [x, 3, z]
        if decor and ball_name in decor:
            decor[ball_name]["$properties"]["Position"] = [x, 6.5, z]

    # Move Crate1 to (-30, 2, 30) and Crate2 to (30, 2, -30).
    if decor:
        if "Crate1" in decor:
            decor["Crate1"]["$properties"]["Position"] = [-30, 2, 30]
        if "Crate2" in decor:
            decor["Crate2"]["$properties"]["Position"] = [30, 2, -30]

    # Save project file back in compact form: two-space indent, number lists on single line, trailing newline.
    project_json_str = json_dumps_compact(proj, indent=2)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(project_json_str)

    print("Project file rebuilt and saved successfully.")

    # STEP 8 — Spawner: brainrots now travel west to east along X.
    if not os.path.exists(SPAWNER_PATH):
        print(f"Error: {SPAWNER_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    with open(SPAWNER_PATH, "r", encoding="utf-8") as f:
        spawner_text = f.read()

    # Replacement one:
    # the spawn line that reads (with one leading tab) tab + "body.Position = Vector3.new(math.random(-4, 4), 3, -130)"
    # becomes tab + "body.Position = Vector3.new(-58, 3, 18 + math.random(-4, 4))"
    target1 = '\tbody.Position = Vector3.new(math.random(-4, 4), 3, -130)'
    replacement1 = '\tbody.Position = Vector3.new(-58, 3, 18 + math.random(-4, 4))'

    # Also handle possible slight whitespace variations just in case
    if target1 in spawner_text:
        spawner_text = spawner_text.replace(target1, replacement1)
    else:
        # fallback search for similar pattern
        pass

    # Replacement two: a five-line block —
    # line one: a tab followed by "local currentPos = body.Position";
    # line two: a tab followed by "local newZ = currentPos.Z + (speed * dt)";
    # line three: a tab followed by "body.Position = Vector3.new(currentPos.X, currentPos.Y, newZ)";
    # line four: empty;
    # line five: a tab followed by "if newZ >= -10 then" —
    # becomes the same five lines but with newX in place of newZ:
    # "local newX = currentPos.X + (speed * dt)", "body.Position = Vector3.new(newX, currentPos.Y, currentPos.Z)", and "if newX >= 58 then".
    block_target = '\tlocal currentPos = body.Position\n\tlocal newZ = currentPos.Z + (speed * dt)\n\tBody.Position = Vector3.new(currentPos.X, currentPos.Y, newZ)\n\n\tif newZ >= -10 then' # note case sensitivity or exact match
    
    # Let's check exact lines in spawner file
    lines = spawner_text.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        # check for 5-line block pattern
        if i + 4 < len(lines) and \
           lines[i].startswith("\t") and "local currentPos = body.Position" in lines[i] and \
           lines[i+1].startswith("\t") and "local newZ = currentPos.Z" in lines[i+1] and \
           lines[i+2].startswith("\t") and "body.Position = Vector3.new(currentPos.X" in lines[i+2] and \
           lines[i+3].strip() == "" and \
           lines[i+4].startswith("\t") and "if newZ" in lines[i+4]:
            
            new_lines.append("\tlocal currentPos = body.Position")
            new_lines.append("\tlocal newX = currentPos.X + (speed * dt)")
            new_lines.append("\tbody.Position = Vector3.new(newX, currentPos.Y, currentPos.Z)")
            new_lines.append("")
            new_lines.append("\tif newX >= 58 then")
            i += 5
        else:
            new_lines.append(lines[i])
            i += 1

    spawner_text = "\n".join(new_lines) + "\n"

    with open(SPAWNER_PATH, "w", encoding="utf-8") as f:
        f.write(spawner_text)

    print("Spawner script updated successfully.")

if __name__ == "__main__":
    main()
