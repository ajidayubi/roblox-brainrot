import json
import math
import sys
import os

PROJECT_PATH = "default.project.json"

def main():
    if not os.path.exists(PROJECT_PATH):
        print(f"Error: {PROJECT_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Navigate workspace tree
    # Rojo project structure: tree -> Workspace -> Decor / PlazaLife / Bases
    tree = data.get("tree", {})
    workspace = tree.get("Workspace", {})
    
    # Check if PlazaRim1 already exists in PlazaLife
    plaza_life = workspace.get("PlazaLife", {})
    if isinstance(plaza_life, dict) and "PlazaRim1" in plaza_life:
        print("Error: part 'PlazaRim1' already exists in the PlazaLife folder.", file=sys.stderr)
        sys.exit(1)

    # Ensure Decor and PlazaLife exist as folders
    if "Decor" not in workspace:
        workspace["Decor"] = {"$className": "Folder"}
    decor = workspace["Decor"]

    if "PlazaLife" not in workspace:
        workspace["PlazaLife"] = {"$className": "Folder"}
    plaza_life = workspace["PlazaLife"]

    # STEP 1 — Fountain tower
    # Delete FountainPillar if present
    if "FountainPillar" in decor:
        del decor["FountainPillar"]

    decor["FountainBase"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Shape": "Cylinder",
            "Position": [0, 1, 0],
            "Size": [24, 1, 24],
            "Color": [0.7, 0.7, 0.7]
        }
    }
    decor["FountainWater"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Shape": "Cylinder",
            "Position": [0, 1.3, 0],
            "Size": [22, 0.5, 22],
            "Color": [0, 0.5, 1]
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
            "Shape": "Cylinder",
            "Position": [0, 7, 0],
            "Size": [14, 1, 14],
            "Color": [0.7, 0.7, 0.7]
        }
    }
    decor["FountainMidWater"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Shape": "Cylinder",
            "Position": [0, 7.3, 0],
            "Size": [12, 0.5, 12],
            "Color": [0, 0.5, 1]
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
            "Shape": "Cylinder",
            "Position": [0, 13, 0],
            "Size": [8, 1, 8],
            "Color": [0.7, 0.7, 0.7]
        }
    }
    decor["FountainTopWater"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Shape": "Cylinder",
            "Position": [0, 13.3, 0],
            "Size": [7, 0.5, 7],
            "Color": [0, 0.5, 1]
        }
    }
    decor["FountainBall"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Shape": "Ball",
            "Position": [0, 15.5, 0],
            "Size": [4, 4, 4],
            "Color": [1, 0.8, 0.2]
        }
    }

    # STEP 2 — Flag poles and bright balls on market stalls
    bases = workspace.get("Bases", {})
    base_colors = {
        "RedBase": [1, 0.2, 0.2],
        "BlueBase": [0.2, 0.5, 1],
        "GreenBase": [0.2, 0.8, 0.2],
        "YellowBase": [1, 0.9, 0]
    }
    for bname, bnode in list(bases.items()):
        if bname.startswith("$") or not isinstance(bnode, dict):
            continue
        pad = bnode.get("Pad")
        if pad and isinstance(pad, dict):
            props = pad.get("$properties", {})
            pos = props.get("Position", [0, 0, 0])
            cx, cz = pos[0], pos[2]
            # Add FlagPole and FlagBall into the base model itself
            bnode["FlagPole"] = {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Position": [cx, 11, cz],
                    "Size": [1, 8, 1],
                    "Color": [0.7, 0.7, 0.7]
                }
            }
            color = base_colors.get(bname, [1, 1, 1])
            bnode["FlagBall"] = {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Shape": "Ball",
                    "Position": [cx, 16, cz],
                    "Size": [5, 5, 5],
                    "Color": color
                }
            }

    # STEP 3 — Big rainbow arch at spawn (z=28)
    if "ArchPillarL" in plaza_life:
        plaza_life["ArchPillarL"]["$properties"]["Position"] = [-8, 6, 28]
        plaza_life["ArchPillarL"]["$properties"]["Size"] = [2, 12, 2]
        plaza_life["ArchPillarL"]["$properties"]["Color"] = [1, 0.2, 0.2]
    else:
        plaza_life["ArchPillarL"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [-8, 6, 28], "Size": [2, 12, 2], "Color": [1, 0.2, 0.2]}
        }

    if "ArchPillarR" in plaza_life:
        plaza_life["ArchPillarR"]["$properties"]["Position"] = [8, 6, 28]
        plaza_life["ArchPillarR"]["$properties"]["Size"] = [2, 12, 2]
        plaza_life["ArchPillarR"]["$properties"]["Color"] = [0.2, 0.5, 1]
    else:
        plaza_life["ArchPillarR"] = {
            "$className": "Part",
            "$properties": {"Anchored": True, "Position": [8, 6, 28], "Size": [2, 12, 2], "Color": [0.2, 0.5, 1]}
        }

    plaza_life["ArchBeam1"] = {
        "$className": "Part",
        "$properties": {"Anchored": True, "Position": [-6, 12, 28], "Size": [6, 2, 2], "Color": [1, 0.2, 0.2]}
    }
    plaza_life["ArchBeam2"] = {
        "$className": "Part",
        "$properties": {"Anchored": True, "Position": [0, 12, 28], "Size": [6, 2, 2], "Color": [1, 0.9, 0]}
    }
    plaza_life["ArchBeam3"] = {
        "$className": "Part",
        "$properties": {"Anchored": True, "Position": [6, 12, 28], "Size": [6, 2, 2], "Color": [0.2, 0.5, 1]}
    }
    plaza_life["ArchBall"] = {
        "$className": "Part",
        "$properties": {"Anchored": True, "Shape": "Ball", "Position": [0, 14, 28], "Size": [4, 4, 4], "Color": [1, 0.8, 0.2]}
    }

    # STEP 4 — Colourful ring around plaza edge (radius 56)
    rim_positions = [
        (56, 0), (39.6, 39.6), (0, 56), (-39.6, 39.6),
        (-56, 0), (-39.6, -39.6), (0, -56), (39.6, -39.6)
    ]
    rim_colors = [
        [1, 0.2, 0.2], [1, 0.5, 0], [1, 0.9, 0], [0.2, 0.8, 0.2],
        [0.2, 0.5, 1], [0.6, 0.2, 0.8], [1, 0.5, 0.8], [0.2, 0.8, 1]
    ]
    for i, (rx, rz) in enumerate(rim_positions, 1):
        plaza_life[f"PlazaRim{i}"] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [rx, 1, rz],
                "Size": [10, 2, 2],
                "Color": rim_colors[i-1]
            }
        }

    # STEP 5 — Eight flower boxes around plaza (radius 66)
    flower_positions = [
        (61, 25.3), (25.3, 61), (-25.3, 61), (-61, 25.3),
        (-61, -25.3), (-25.3, -61), (25.3, -61), (61, -25.3)
    ]
    flower_colors = [
        [1, 0.5, 0.8], [1, 0.9, 0], [0.6, 0.2, 0.8], [1, 0.2, 0.2],
        [0.2, 0.8, 1], [1, 0.5, 0.8], [0.2, 0.8, 0.2], [1, 0.5, 0.8]
    ]
    for i, (fx, fz) in enumerate(flower_positions, 1):
        plaza_life[f"Flower{i}"] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [fx, 0.8, fz],
                "Size": [4, 1.5, 4],
                "Color": flower_colors[i-1]
            }
        }

    # Save compact json with list single-lining
    class CompactEncoder(json.JSONEncoder):
        def encode(self, o):
            if isinstance(o, list) and all(isinstance(x, (int, float)) for x in o):
                return "[" + ", ".join(f"{x:g}" if isinstance(x, float) and x.is_integer() else str(x) for x in o) + "]"
            return super().encode(o)
        
        def iterencode(self, o, _w=None):
            if isinstance(o, list) and all(isinstance(x, (int, float)) for x in o):
                yield "[" + ", ".join(str(x) for x in o) + "]"
            else:
                yield from super().iterencode(o, _w)

    # Standard json dump with indent=2, then post-process lists of numbers onto single lines
    raw_json = json.dumps(data, indent=2)
    
    # Custom post-processor to make number lists single-line
    import re
    def single_line_lists(match):
        content = match.group(1)
        # remove newlines and extra spaces inside list
        items = re.findall(r'-?\d+(?:\.\d+)?', content)
        return "[" + ", ".join(items) + "]"

    # Regex matches arrays containing numbers (ints/floats) spanning multiple lines
    formatted_json = re.sub(r'\[\s*(-?\d+(?:\.\d+)?(?:\s*,\s*-?\d+(?:\.\d+)?)*)\s*\]', single_line_lists, raw_json)

    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(formatted_json + "\n")

    print(f"Successfully updated {PROJECT_PATH} with dense park enhancements.")

if __name__ == "__main__":
    main()
