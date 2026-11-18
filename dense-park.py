import json
import os
import math

def format_json(data):
    """
    Custom serializer that formats JSON with 2-space indent,
    but keeps lists containing only numbers on a single line.
    Also ensures closing bracket rules are strictly correct (no bug with ']' for objects).
    """
    def is_number_list(obj):
        return isinstance(obj, list) and all(isinstance(x, (int, float)) for x in obj)

    def _to_json(obj, indent=0):
        spaces = "  " * indent
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            parts = []
            for k, v in obj.items():
                key_str = json.dumps(k)
                val_str = _to_json(v, indent + 1)
                parts.append(f"{spaces}  {key_str}: {val_str}")
            joined = ",\n".join(parts)
            return f"{{\n{joined}\n{spaces}}}"
        elif is_number_list(obj):
            return json.dumps(obj)
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            parts = []
            for item in obj:
                parts.append(f"{spaces}  {_to_json(item, indent + 1)}")
            joined = ",\n".join(parts)
            return f"[\n{joined}\n{spaces}]"
        else:
            return json.dumps(obj)

    return _to_json(data, 0) + "\n"

def main():
    project_path = "default.project.json"
    if not os.path.exists(project_path):
        print(f"Error: {project_path} not found.")
        exit(1)

    with open(project_path, "r") as f:
        data = json.load(f)

    # Navigate to Workspace -> PlazaLife
    workspace = data.get("tree", {}).get("Workspace", {})
    plaza_life = workspace.get("PlazaLife")
    if plaza_life is None:
        # PlazaLife might be a dict or under children if structured differently,
        # but in Rojo json projects, children are direct keys of the model/folder node.
        # Let's check how default.project.json structures Workspace children.
        # Usually Workspace has $className: "Workspace", and children are direct keys.
        plaza_life = workspace.get("PlazaLife")

    if plaza_life is not None:
        if "PlazaRim1" in plaza_life:
            print("Error: Part 'PlazaRim1' already exists in the PlazaLife folder.")
            exit(1)

    # If PlazaLife folder doesn't exist yet in workspace, create it
    if "PlazaLife" not in workspace:
        workspace["PlazaLife"] = {
            "$className": "Folder"
        }
        plaza_life = workspace["PlazaLife"]

    decor = workspace.get("Decor")
    if decor is None:
        workspace["Decor"] = {
            "$className": "Folder"
        }
        decor = workspace["Decor"]

    bases = workspace.get("Bases")
    if bases is None:
        workspace["Bases"] = {
            "$className": "Folder"
        }
        bases = workspace["Bases"]

    # STEP 1 — Fountain tower
    # In Decor folder: delete "FountainPillar". Enlarge "FountainBase", "FountainWater". Add FountainPillar1, FountainMid, FountainMidWater, FountainPillar2, FountainTop, FountainTopWater, FountainBall.
    if "FountainPillar" in decor:
        del decor["FountainPillar"]

    decor["FountainBase"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 1, 0],
            "Size": [24, 1, 24],
            "Color": [0.7, 0.7, 0.7],
            "Shape": "Cylinder"
        }
    }
    decor["FountainWater"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 1.3, 0],
            "Size": [22, 0.5, 22],
            "Color": [0, 0.5, 1],
            "Shape": "Cylinder"
        }
    }
    decor["FountainPillar1"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 4, 0],
            "Size": [3, 6, 3],
            "Color": [1, 1, 1]
        }
    }
    decor["FountainMid"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 7, 0],
            "Size": [14, 1, 14],
            "Color": [0.7, 0.7, 0.7],
            "Shape": "Cylinder"
        }
    }
    decor["FountainMidWater"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 7.3, 0],
            "Size": [12, 0.5, 12],
            "Color": [0, 0.5, 1],
            "Shape": "Cylinder"
        }
    }
    decor["FountainPillar2"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 10, 0],
            "Size": [2, 5, 2],
            "Color": [1, 1, 1]
        }
    }
    decor["FountainTop"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 13, 0],
            "Size": [8, 1, 8],
            "Color": [0.7, 0.7, 0.7],
            "Shape": "Cylinder"
        }
    }
    decor["FountainTopWater"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 13.3, 0],
            "Size": [7, 0.5, 7],
            "Color": [0, 0.5, 1],
            "Shape": "Cylinder"
        }
    }
    decor["FountainBall"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 15.5, 0],
            "Size": [4, 4, 4],
            "Color": [1, 0.8, 0.2],
            "Shape": "Ball"
        }
    }

    # STEP 2 — Flag poles and bright balls on every market stall
    # For each base model in Bases folder (skip any key starting with $ and non-dict): read "Pad" part position (cx, cz). Add FlagPole and FlagBall with base color.
    base_colors = {
        "RedBase": [1, 0.2, 0.2],
        "BlueBase": [0.2, 0.5, 1],
        "GreenBase": [0.2, 0.8, 0.2],
        "YellowBase": [1, 0.9, 0]
    }

    for b_name, b_node in bases.items():
        if b_name.startswith("$") or not isinstance(b_node, dict):
            continue
        pad = b_node.get("Pad")
        if pad and isinstance(pad, dict):
            pos = pad.get("$properties", {}).get("Position")
            if pos and len(pos) >= 3:
                cx, cz = pos[0], pos[2]
                b_col = base_colors.get(b_name, [1, 1, 1])
                b_node["FlagPole"] = {
                    "$className": "Part",
                    "$properties": {
                        "Anchored": True,
                        "Position": [cx, 11, cz],
                        "Size": [1, 8, 1],
                        "Color": [0.7, 0.7, 0.7]
                    }
                }
                b_node["FlagBall"] = {
                    "$className": "Part",
                    "$properties": {
                        "Anchored": True,
                        "Position": [cx, 16, cz],
                        "Size": [5, 5, 5],
                        "Color": b_col,
                        "Shape": "Ball"
                    }
                }

    # STEP 3 — Big rainbow arch at spawn, moved to z=28
    # In PlazaLife folder: move ArchPillarL to (-8, 6, 28) size (2, 12, 2) red; move ArchPillarR to (8, 6, 28) size (2, 12, 2) blue.
    # Add three beams at y=12, z=28: ArchBeam1 (-6, 12, 28) size (6, 2, 2) red; ArchBeam2 (0, 12, 28) size (6, 2, 2) yellow; ArchBeam3 (6, 12, 28) size (6, 2, 2) blue.
    # Add ArchBall (0, 14, 28) size (4, 4, 4) gold ball.
    if "ArchPillarL" in plaza_life:
        plaza_life["ArchPillarL"]["$properties"]["Position"] = [-8, 6, 28]
        plaza_life["ArchPillarL"]["$properties"]["Size"] = [2, 12, 2]
        plaza_life["ArchPillarL"]["$properties"]["Color"] = [1, 0.2, 0.2]
    else:
        plaza_life["ArchPillarL"] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [-8, 6, 28],
                "Size": [2, 12, 2],
                "Color": [1, 0.2, 0.2]
            }
        }

    if "ArchPillarR" in plaza_life:
        plaza_life["ArchPillarR"]["$properties"]["Position"] = [8, 6, 28]
        plaza_life["ArchPillarR"]["$properties"]["Size"] = [2, 12, 2]
        plaza_life["ArchPillarR"]["$properties"]["Color"] = [0.2, 0.5, 1]
    else:
        plaza_life["ArchPillarR"] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [8, 6, 28],
                "Size": [2, 12, 2],
                "Color": [0.2, 0.5, 1]
            }
        }

    plaza_life["ArchBeam1"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [-6, 12, 28],
            "Size": [6, 2, 2],
            "Color": [1, 0.2, 0.2]
        }
    }
    plaza_life["ArchBeam2"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 12, 28],
            "Size": [6, 2, 2],
            "Color": [1, 0.9, 0]
        }
    }
    plaza_life["ArchBeam3"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [6, 12, 28],
            "Size": [6, 2, 2],
            "Color": [0.2, 0.5, 1]
        }
    }
    plaza_life["ArchBall"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 14, 28],
            "Size": [4, 4, 4],
            "Color": [1, 0.8, 0.2],
            "Shape": "Ball"
        }
    }

    # STEP 4 — Colourful ring around the plaza edge
    # PlazaRim1 to PlazaRim8 at radius 56, angles 0, 45, 90, 135, 180, 225, 270, 315
    # positions specified: (56, 0), (39.6, 39.6), (0, 56), (-39.6, 39.6), (-56, 0), (-39.6, -39.6), (0, -56), (39.6, -39.6) (note: prompt gives x, z coordinates)
    rim_positions = [
        [56, 1, 0],
        [39.6, 1, 39.6],
        [0, 1, 56],
        [-39.6, 1, 39.6],
        [-56, 1, 0],
        [-39.6, 1, -39.6],
        [0, 1, -56],
        [39.6, 1, -39.6]
    ]
    rim_colors = [
        [1, 0.2, 0.2],    # red
        [1, 0.5, 0],      # orange
        [1, 0.9, 0],      # yellow
        [0.2, 0.8, 0.2],  # green
        [0.2, 0.5, 1],    # blue
        [0.6, 0.2, 0.8],  # purple
        [1, 0.5, 0.8],    # pink
        [0.2, 0.8, 1]     # cyan
    ]

    for i in range(8):
        name = f"PlazaRim{i+1}"
        plaza_life[name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": rim_positions[i],
                "Size": [10, 2, 2],
                "Color": rim_colors[i]
            }
        }

    # STEP 5 — Eight flower boxes around the plaza
    # Flower1 to Flower8 at radius 66, angles 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5
    # positions: (61, 25.3), (25.3, 61), (-25.3, 61), (-61, 25.3), (-61, -25.3), (-25.3, -61), (25.3, -61), (61, -25.3) at y=0.8
    flower_positions = [
        [61, 0.8, 25.3],
        [25.3, 0.8, 61],
        [-25.3, 0.8, 61],
        [-61, 0.8, 25.3],
        [-61, 0.8, -25.3],
        [-25.3, 0.8, -61],
        [25.3, 0.8, -61],
        [61, 0.8, -25.3]
    ]
    flower_colors = [
        [1, 0.5, 0.8],    # pink
        [1, 0.9, 0],      # yellow
        [0.6, 0.2, 0.8],  # purple
        [1, 0.2, 0.2],    # red
        [0.2, 0.8, 1],    # cyan
        [1, 0.5, 0],      # orange
        [0.2, 0.8, 0.2],  # green
        [1, 0.5, 0.8]     # pink
    ]

    for i in range(8):
        name = f"Flower{i+1}"
        plaza_life[name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": flower_positions[i],
                "Size": [4, 1.5, 4],
                "Color": flower_colors[i]
            }
        }

    # Save output
    output_str = format_json(data)
    with open(project_path, "w") as f:
        f.write(output_str)

    print(f"Successfully updated {project_path} with dense park features.")

if __name__ == "__main__":
    main()
