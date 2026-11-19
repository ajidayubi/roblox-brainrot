import json
import os
import sys

def main():
    project_path = "default.project.json"
    if not os.path.exists(project_path):
        print(f"Error: {project_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(project_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Navigate tree -> Workspace -> Decor
    tree = data.setdefault("tree", {})
    workspace = tree.setdefault("Workspace", {})
    decor = workspace.setdefault("Decor", {})

    # Check if GroundTile1 already exists in Decor
    if "GroundTile1" in decor:
        print("Error: GroundTile1 already exists in the Decor folder.", file=sys.stderr)
        sys.exit(1)

    # STEP 1: Shrink Baseplate size to [400, 20, 400]
    baseplate = workspace.get("Baseplate")
    if baseplate and isinstance(baseplate, dict):
        props = baseplate.setdefault("$properties", {})
        props["Size"] = [400, 20, 400]

    # STEP 2: Forty-eight big pastel ground tiles in Decor
    pastel_cycle = [
        [0.7, 0.9, 0.6],    # light green
        [0.95, 0.9, 0.7],   # cream
        [1.0, 0.8, 0.85],   # pink
        [0.75, 0.85, 1.0],  # light blue
        [1.0, 0.95, 0.6],   # pale yellow
        [0.85, 0.75, 0.95]  # lilac
    ]

    tile_coords = [
        (-50.3, -135.4), (-154.2, -28.0), (-107.1, 66.7), (-142.9, -148.0),
        (-93.3, -103.9), (26.6, -115.7), (-23.3, -133.6), (127.7, -92.2),
        (102.4, 29.2), (70.2, -131.6), (-32.5, -63.7), (86.2, -114.5),
        (-97.1, 30.5), (107.8, -11.1), (121.2, 50.5), (76.6, -72.7),
        (-130.2, -89.4), (-126.5, -65.3), (-146.7, 3.6), (-15.6, -103.7),
        (103.5, 82.4), (-78.6, 46.3), (148.5, -116.4), (-9.1, -77.4),
        (131.7, 4.6), (76.3, 35.5), (153.9, 88.5), (-105.3, -127.2),
        (-84.8, -149.2), (-134.3, 73.1), (127.2, -127.4), (-146.1, -50.6),
        (-63.7, -98.1), (64.7, -17.9), (138.1, -60.9), (124.7, 90.3),
        (-79.8, 14.9), (144.2, -17.2), (110.7, -62.8), (159.6, -36.9),
        (-151.9, 44.3), (-86.3, -50.4), (155.5, -142.5), (-127.9, 50.7),
        (3.1, -141.6), (29.7, -146.8), (95.4, -34.0), (68.1, -95.8)
    ]

    for i, (x, z) in enumerate(tile_coords, start=1):
        tile_name = f"GroundTile{i}"
        color = pastel_cycle[(i - 1) % len(pastel_cycle)]
        decor[tile_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Color": color,
                "Position": [x, 1.05, z],
                "Size": [18, 0.2, 18]
            }
        }

    # STEP 3: Fourteen big trees in Decor
    tree_names = [
        "BigTree0", "BigTree1", "BigTree2", "BigTree10", "BigTree11",
        "BigTree14", "BigTree15", "BigTree16", "BigTree17", "BigTree18",
        "BigTree19", "BigTree20", "BigTree22", "BigTree23"
    ]
    tree_coords = {
        "BigTree0": (94.3, 11.6),
        "BigTree1": (111.3, 45.0),
        "BigTree2": (115.8, 87.3),
        "BigTree10": (-110.5, 46.9),
        "BigTree11": (-143.6, 20.2),
        "BigTree14": (-115.8, -87.3),
        "BigTree15": (-58.5, -74.9),
        "BigTree16": (-46.9, -110.5),
        "BigTree17": (-20.2, -143.6),
        "BigTree18": (11.6, -94.3),
        "BigTree19": (45.0, -111.3),
        "BigTree20": (87.3, -115.8),
        "BigTree22": (110.5, -46.9),
        "BigTree23": (143.6, -20.2)
    }

    for name in tree_names:
        x, z = tree_coords[name]
        decor[name] = {
            "$className": "Model",
            "Trunk": {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Color": [0.55, 0.35, 0.15],
                    "Position": [x, 5, z],
                    "Size": [4, 10, 4]
                }
            },
            "Leaves": {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Color": [0.2, 0.7, 0.2],
                    "Position": [x, 12, z],
                    "Size": [13, 5, 13]
                }
            }
        }

    # STEP 4: Fifteen big flowers in Decor
    flower_data = [
        ("BigFlower0", 74.2, 30.0, [1.0, 0.8, 0.85]),
        ("BigFlower8", -63.0, 49.3, [1.0, 0.95, 0.6]),
        ("BigFlower9", -92.1, 39.1, [0.85, 0.75, 0.95]),
        ("BigFlower10", -118.8, 16.7, [0.7, 0.9, 0.6]),
        ("BigFlower11", -139.0, -17.1, [0.95, 0.9, 0.7]),
        ("BigFlower13", -79.9, -60.2, [0.75, 0.85, 1.0]),
        ("BigFlower14", -73.9, -94.6, [1.0, 0.95, 0.6]),
        ("BigFlower15", -54.7, -128.9, [0.85, 0.75, 0.95]),
        ("BigFlower16", -11.1, -79.2, [0.7, 0.9, 0.6]),
        ("BigFlower17", 12.2, -99.3, [0.95, 0.9, 0.7]),
        ("BigFlower18", 45.0, -111.3, [1.0, 0.8, 0.85]),
        ("BigFlower19", 84.3, -111.8, [0.75, 0.85, 1.0]),
        ("BigFlower21", 92.1, -39.1, [0.85, 0.75, 0.95]),
        ("BigFlower22", 118.8, -16.7, [0.7, 0.9, 0.6]),
        ("BigFlower23", 139.0, 17.1, [0.95, 0.9, 0.7])
    ]

    for name, x, z, color in flower_data:
        decor[name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Color": color,
                "Position": [x, 0.9, z],
                "Size": [8, 1.5, 8]
            }
        }

    # Save back with custom formatting
    formatted_json = compact_json_dump(data)
    with open(project_path, "w", encoding="utf-8") as f:
        f.write(formatted_json)
        f.write("\n")

    print(f"Successfully updated {project_path}")

def compact_json_dump(obj):
    def format_val(v, indent_level):
        indent = "  " * indent_level
        if isinstance(v, dict):
            if not v:
                return "{}"
            item_lines = []
            for k, val in v.items():
                # Check if k is empty string or something weird from old formatting bug
                item_lines.append(f'{indent}  {json.dumps(k)}: {format_val(val, indent_level + 1)}')
            return "{\n" + ",\n".join(item_lines) + f"\n{indent}}}"
        elif isinstance(v, list):
            if v and all(isinstance(x, (int, float)) for x in v):
                return json.dumps(v)
            else:
                if not v:
                    return "[]"
                item_lines = []
                for val in v:
                    item_lines.append(f'{indent}  {format_val(val, indent_level + 1)}')
                return "[\n" + ",\n".join(item_lines) + f"\n{indent}]"
        else:
            return json.dumps(v)

    return format_val(obj, 0)

if __name__ == "__main__":
    main()
