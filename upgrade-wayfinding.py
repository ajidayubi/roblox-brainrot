import json
import os
import sys

def dump_compact(obj, indent=2):
    def _format(o, level):
        spaces = " " * (level * indent)
        if isinstance(o, dict):
            if not o:
                return "{}"
            items = []
            for k, v in o.items():
                items.append(f'{spaces}{" " * indent}"{k}": {_format(v, level + 1)}')
            return "{\n" + ",\n".join(items) + f"\n{spaces}}}"
        elif isinstance(o, list):
            if all(isinstance(x, (int, float, bool, str)) for x in o):
                inner = ", ".join(json.dumps(x) for x in o)
                return f"[{inner}]"
            else:
                if not o:
                    return "[]"
                items = []
                for item in o:
                    items.append(f'{spaces}{" " * indent}{_format(item, level + 1)}')
                return "[\n" + ",\n".join(items) + f"\n{spaces}]"
        else:
            return json.dumps(o)

    return _format(obj, 0) + "\n"

def main():
    path = "default.project.json"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)

    # Check if BeaconPole already exists in Decor
    try:
        decor_folder = data.get("tree", {}).get("Workspace", {}).get("Decor", {})
        if isinstance(decor_folder, dict) and "BeaconPole" in decor_folder:
            print("Error: Part 'BeaconPole' already exists in the Decor folder.")
            sys.exit(1)
    except Exception:
        pass

    tree = data.setdefault("tree", {})
    workspace = tree.setdefault("Workspace", {"$className": "Folder"})
    decor = workspace.setdefault("Decor", {"$className": "Folder"})
    env = workspace.setdefault("Environment", {"$className": "Folder"})

    # STEP 1 — Beacon above the fountain
    decor["BeaconPole"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 26, 0],
            "Size": [3, 38, 3],
            "Color": [1, 0.3, 0.6]
        }
    }
    decor["BeaconBall"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 48, 0],
            "Size": [8, 8, 8],
            "Color": [1, 0.8, 0.2],
            "Shape": "Ball"
        }
    }

    # STEP 2 — Border walls around the play area
    env["WallNorth"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 4, -160],
            "Size": [340, 8, 2],
            "Color": [1, 0.3, 0.6]
        }
    }
    env["WallSouth"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 4, 180],
            "Size": [340, 8, 2],
            "Color": [0.2, 0.5, 1]
        }
    }
    env["WallWest"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [-170, 4, 10],
            "Size": [2, 8, 340],
            "Color": [0.2, 0.8, 0.2]
        }
    }
    env["WallEast"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [170, 4, 10],
            "Size": [2, 8, 340],
            "Color": [1, 0.9, 0]
        }
    }

    # STEP 3 — Outer trees
    tree_spots = [
        (90, -60), (-90, -60), (120, 40), (-120, 40),
        (90, 100), (-90, 100), (0, -120), (140, -20),
        (-140, 80), (120, 120)
    ]

    for idx, (x, z) in enumerate(tree_spots, start=1):
        tree_name = f"OuterTree{idx}"
        decor[tree_name] = {
            "$className": "Model",
            "Trunk": {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Position": [x, 4, z],
                    "Size": [3, 8, 3],
                    "Color": [0.55, 0.35, 0.15]
                }
            },
            "Leaves": {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Position": [x, 9, z],
                    "Size": [8, 3, 8],
                    "Color": [0.2, 0.7, 0.2]
                }
            }
        }

    output_content = dump_compact(data, indent=2)
    with open(path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print("Successfully updated default.project.json with wayfinding elements.")

if __name__ == "__main__":
    main()
