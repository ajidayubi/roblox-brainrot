import json
import os

def generate():
    project_path = "/home/hatch/workspace/makefun/roblox-brainrot-01/bot/default.project.json"
    if not os.path.exists(project_path):
        print(f"Error: {project_path} does not exist.")
        exit(1)

    with open(project_path, "r") as f:
        data = json.load(f)

    workspace = data.get("tree", {}).get("Workspace", {})
    decor = workspace.get("Decor", {})
    if "BeaconPole" in decor:
        print("Error: BeaconPole already exists in Decor folder.")
        exit(1)

    # Step 1: Beacon above fountain
    if "$className" not in decor:
        decor["$className"] = "Folder"
    
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
            "Shape": "Ball",
            "Position": [0, 48, 0],
            "Size": [8, 8, 8],
            "Color": [1, 0.8, 0.2]
        }
    }

    # Step 2: Border walls
    environment = workspace.get("Environment", {})
    if "$className" not in environment:
        environment["$className"] = "Folder"

    environment["WallNorth"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 4, -160],
            "Size": [340, 8, 2],
            "Color": [1, 0.3, 0.6]
        }
    }
    environment["WallSouth"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 4, 180],
            "Size": [340, 8, 2],
            "Color": [0.2, 0.5, 1]
        }
    }
    environment["WallWest"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [-170, 4, 10],
            "Size": [2, 8, 340],
            "Color": [0.2, 0.8, 0.2]
        }
    }
    environment["WallEast"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [170, 4, 10],
            "Size": [2, 8, 340],
            "Color": [1, 0.9, 0]
        }
    }

    # Step 3: Outer trees
    tree_spots = [
        (90, -60), (-90, -60), (120, 40), (-120, 40),
        (90, 100), (-90, 100), (0, -120), (140, -20),
        (-140, 80), (120, 120)
    ]
    for i, (x, z) in enumerate(tree_spots, 1):
        tree_name = f"OuterTree{i}"
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

    workspace["Decor"] = decor
    workspace["Environment"] = environment
    data["tree"]["Workspace"] = workspace

    # Custom serializer to keep number lists on a single line
    def custom_dump(obj, indent=2):
        def format_val(v, level):
            if isinstance(v, bool):
                return "true" if v else "false"
            elif isinstance(v, (int, float)):
                return str(v)
            elif isinstance(v, str):
                return json.dumps(v)
            elif isinstance(v, list):
                if all(isinstance(x, (int, float, bool, str)) for x in v):
                    items = ", ".join(format_val(x, 0) for x in v)
                    return f"[{items}]"
                else:
                    indent_str = " " * (level * indent)
                    child_indent = " " * ((level + 1) * indent)
                    lines = []
                    for item in v:
                        lines.append(f"{child_indent}{format_val(item, level + 1)}")
                    inner = ",\n".join(lines)
                    return f"[\n{inner}\n{indent_str}]"
            elif isinstance(v, dict):
                indent_str = " " * (level * indent)
                child_indent = " " * ((level + 1) * indent)
                lines = []
                for k, val in v.items():
                    lines.append(f'{child_indent}{json.dumps(k)}: {format_val(val, level + 1)}')
                inner = ",\n".join(lines)
                return f"{{\n{inner}\n{indent_str}}}"
            else:
                return json.dumps(v)
        return format_val(obj, 0) + "\n"

    output_str = custom_dump(data, indent=2)
    with open(project_path, "w") as f:
        f.write(output_str)
    print("Successfully updated default.project.json via upgrade-wayfinding.py")

if __name__ == "__main__":
    generate()
