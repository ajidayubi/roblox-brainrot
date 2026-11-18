import json
import os
import sys

PROJECT_PATH = "default.project.json"

def main():
    if not os.path.exists(PROJECT_PATH):
        print(f"Error: {PROJECT_PATH} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check for GroundTile1 in Decor folder under Workspace
    try:
        workspace = data["tree"]["Workspace"]
        decor = workspace.get("Decor", {})
        if "GroundTile1" in decor:
            print("Error: GroundTile1 already exists in the Decor folder.", file=sys.stderr)
            sys.exit(1)
    except KeyError:
        pass

    # Ensure Decor folder exists in Workspace
    if "Workspace" not in data["tree"]:
        data["tree"]["Workspace"] = {"$className": "Workspace"}
    if "Decor" not in data["tree"]["Workspace"]:
        data["tree"]["Workspace"]["Decor"] = {"$className": "Folder"}

    decor_folder = data["tree"]["Workspace"]["Decor"]

    # STEP 1 — Shrink Baseplate size to (400, 20, 400)
    if "Baseplate" in data["tree"]["Workspace"]:
        data["tree"]["Workspace"]["Baseplate"]["$properties"]["Size"] = [400, 20, 400]

    # STEP 2 — 48 big pastel ground tiles (GroundTile1 to GroundTile48)
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
        color = pastel_cycle[(i - 1) % len(pastel_cycle)]
        decor_folder[f"GroundTile{i}"] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Color": color,
                "Position": [x, 1.05, z],
                "Size": [18, 0.2, 18]
            }
        }

    # STEP 3 — 14 big trees in outer ring
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
        decor_folder[name] = {
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

    # STEP 4 — 15 big flowers in outer ring
    flower_data = [
        ("BigFlower0", (74.2, 30.0), [1.0, 0.8, 0.85]),
        ("BigFlower8", (-63.0, 49.3), [1.0, 0.95, 0.6]),
        ("BigFlower9", (-92.1, 39.1), [0.85, 0.75, 0.95]),
        ("BigFlower10", (-118.8, 16.7), [0.7, 0.9, 0.6]),
        ("BigFlower11", (-139.0, -17.1), [0.95, 0.9, 0.7]),
        ("BigFlower13", (-79.9, -60.2), [0.75, 0.85, 1.0]),
        ("BigFlower14", (-73.9, -94.6), [1.0, 0.95, 0.6]),
        ("BigFlower15", (-54.7, -128.9), [0.85, 0.75, 0.95]),
        ("BigFlower16", (-11.1, -79.2), [0.7, 0.9, 0.6]),
        ("BigFlower17", (12.2, -99.3), [0.95, 0.9, 0.7]),
        ("BigFlower18", (45.0, -111.3), [1.0, 0.8, 0.85]),
        ("BigFlower19", (84.3, -111.8), [0.75, 0.85, 1.0]),
        ("BigFlower21", (92.1, -39.1), [0.85, 0.75, 0.95]),
        ("BigFlower22", (118.8, -16.7), [0.7, 0.9, 0.6]),
        ("BigFlower23", (139.0, 17.1), [0.95, 0.9, 0.7])
    ]

    for name, (x, z), color in flower_data:
        decor_folder[name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Color": color,
                "Position": [x, 0.9, z],
                "Size": [8, 1.5, 8]
            }
        }

    # Custom serializer to keep lists of numbers on a single line
    def custom_dump(obj, indent=2):
        def _to_str(o, level=0):
            ind = " " * (indent * level)
            ind_next = " " * (indent * (level + 1))
            if isinstance(o, dict):
                if not o:
                    return "{}"
                items = []
                for k, v in o.items():
                    items.append(f'{ind_next}{json.dumps(k)}: {_to_str(v, level + 1)}')
                return "{\n" + ",\n".join(items) + f"\n{ind}}}"
            elif isinstance(o, list):
                if all(isinstance(x, (int, float)) for x in o):
                    return json.dumps(o)
                if not o:
                    return "[]"
                items = []
                for item in o:
                    items.append(f'{ind_next}{_to_str(item, level + 1)}')
                return "[\n" + ",\n".join(items) + f"\n{ind}]"
            else:
                return json.dumps(o)

        return _to_str(obj, 0) + "\n"

    output_content = custom_dump(data, indent=2)

    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(output_content)

    print("Successfully updated default.project.json")

if __name__ == "__main__":
    main()
