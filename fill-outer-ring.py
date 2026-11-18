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

    # Check if FillTree0 already exists in Decor
    try:
        decor = data["tree"]["Workspace"]["Decor"]
        if "FillTree0" in decor:
            print("Error: 'FillTree0' already exists in the Decor folder.", file=sys.stderr)
            sys.exit(1)
    except KeyError:
        pass

    # STEP 1: Update walls in Environment
    try:
        env = data["tree"]["Workspace"]["Environment"]
    except KeyError:
        env = {}
        data["tree"]["Workspace"]["Environment"] = env

    walls = {
        "WallNorth": {"pos": [0, 10, -160], "size": [340, 20, 2], "color": [1, 0.3, 0.6]},
        "WallSouth": {"pos": [0, 10, 180], "size": [340, 20, 2], "color": [0.2, 0.5, 1]},
        "WallWest": {"pos": [-170, 10, 10], "size": [2, 20, 340], "color": [0.2, 0.8, 0.2]},
        "WallEast": {"pos": [170, 10, 10], "size": [2, 20, 340], "color": [1, 0.9, 0]}
    }

    for name, info in walls.items():
        if name not in env:
            env[name] = {"$className": "Part"}
        env[name]["$className"] = "Part"
        if "$properties" not in env[name]:
            env[name]["$properties"] = {}
        env[name]["$properties"]["Anchored"] = True
        env[name]["$properties"]["Position"] = info["pos"]
        env[name]["$properties"]["Size"] = info["size"]
        env[name]["$properties"]["Color"] = info["color"]

    # Ensure Decor folder exists
    if "Decor" not in data["tree"]["Workspace"]:
        data["tree"]["Workspace"]["Decor"] = {"$className": "Folder"}
    decor = data["tree"]["Workspace"]["Decor"]

    # STEP 2: 60 decorations
    flower_colors = [
        [1, 0.9, 0],     # yellow
        [1, 0.5, 0.8],   # pink
        [0.2, 0.8, 1],   # cyan
        [1, 0.2, 0.2],   # red
        [0.6, 0.2, 0.8]  # purple
    ]

    coords = [
        (-50.3, -135.4), (-154.2, -28.0), (-107.1, 66.7), (-142.9, -148.0),
        (-93.3, -103.9), (26.6, -115.7), (-23.3, -133.6), (127.7, -92.2),
        (102.4, 29.2), (70.2, -131.6), (-32.5, -63.7), (86.2, -114.5),
        (-97.1, 30.5), (107.8, -11.1), (121.2, 50.5), (19.4, -128.9),
        (76.6, -72.7), (-130.2, -89.4), (-126.5, -65.3), (-146.7, 3.6),
        (-15.6, -103.7), (103.5, 82.4), (-151.8, -41.9), (-11.0, -89.9),
        (-48.3, -76.0), (-78.6, 46.3), (148.5, -116.4), (-92.4, 77.9),
        (8.8, -111.2), (131.7, 4.6), (1.0, -99.4), (76.3, 35.5),
        (153.9, 88.5), (-105.3, -127.2), (-84.8, -149.2), (-148.8, -13.8),
        (-134.3, 73.1), (157.8, -103.7), (127.2, -127.4), (-136.5, 58.0),
        (-131.6, -1.2), (128.6, -18.2), (-19.8, -147.8), (-63.7, -98.1),
        (64.7, -17.9), (100.9, -29.7), (128.6, -143.4), (47.1, -114.7),
        (20.0, -101.6), (138.1, -60.9), (118.1, -64.6), (-138.1, 91.7),
        (124.7, 90.3), (-43.3, -94.5), (-126.2, -46.2), (-72.4, -83.6),
        (60.4, -143.0), (155.9, -53.2), (-79.8, 14.9), (88.7, 18.6)
    ]

    flower_count = 0
    for i in range(60):
        kind = i % 4
        x, z = coords[i]
        if kind == 0:
            # Tree Model
            model_name = f"FillTree{i}"
            decor[model_name] = {
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
                        "Size": [9, 4, 9],
                        "Color": [0.2, 0.7, 0.2]
                    }
                }
            }
        elif kind == 1:
            # Flower part
            part_name = f"FillFlower{i}"
            col = flower_colors[flower_count % len(flower_colors)]
            flower_count += 1
            decor[part_name] = {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Position": [x, 0.8, z],
                    "Size": [5, 1.5, 5],
                    "Color": col
                }
            }
        elif kind == 2:
            # Lamp pole + ball
            pole_name = f"FillLamp{i}"
            ball_name = f"FillLampBall{i}"
            decor[pole_name] = {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Position": [x, 3, z],
                    "Size": [1, 6, 1],
                    "Color": [0.2, 0.2, 0.2]
                }
            }
            decor[ball_name] = {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Shape": "Ball",
                    "Position": [x, 6.5, z],
                    "Size": [2.5, 2.5, 2.5],
                    "Color": [1, 0.9, 0.3]
                }
            }
        elif kind == 3:
            # Bush part
            part_name = f"FillBush{i}"
            decor[part_name] = {
                "$className": "Part",
                "$properties": {
                    "Anchored": True,
                    "Position": [x, 1.5, z],
                    "Size": [5, 3, 5],
                    "Color": [0.2, 0.7, 0.2]
                }
            }

    # STEP 3: Two blue ponds in NE and NW corners
    ponds = [
        ("PondNE", [120, 0.5, -110], [30, 1, 30], [0.2, 0.6, 1], None),
        ("PondNEBall", [120, 2, -110], [4, 4, 4], [1, 0.9, 0], "Ball"),
        ("PondNW", [-120, 0.5, -110], [30, 1, 30], [0.2, 0.6, 1], None),
        ("PondNWBall", [-120, 2, -110], [4, 4, 4], [1, 0.5, 0.8], "Ball")
    ]
    for name, pos, size, color, shape in ponds:
        props = {
            "Anchored": True,
            "Position": pos,
            "Size": size,
            "Color": color
        }
        if shape:
            props["Shape"] = shape
        decor[name] = {
            "$className": "Part",
            "$properties": props
        }

    # STEP 4: Eight colourful path tiles
    paths = [
        ("OuterPath1", [-110, 1.1, 0], [1, 0.2, 0.2]),
        ("OuterPath2", [-80, 1.1, 0], [1, 0.5, 0]),
        ("OuterPath3", [80, 1.1, 0], [0.2, 0.5, 1]),
        ("OuterPath4", [110, 1.1, 0], [0.2, 0.8, 0.2]),
        ("OuterPath5", [0, 1.1, -100], [1, 0.9, 0]),
        ("OuterPath6", [0, 1.1, -130], [0.6, 0.2, 0.8]),
        ("OuterPath7", [-110, 1.1, -80], [1, 0.5, 0.8]),
        ("OuterPath8", [110, 1.1, -80], [0.2, 0.8, 1])
    ]
    for name, pos, color in paths:
        decor[name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": pos,
                "Size": [8, 0.2, 8],
                "Color": color
            }
        }

    # Custom serializer to format number lists on a single line
    def custom_dump(obj, indent=2):
        def _to_json(val, level=0):
            ind = " " * (indent * level)
            ind_inner = " " * (indent * (level + 1))
            
            if isinstance(val, bool):
                return "true" if val else "false"
            elif val is None:
                return "null"
            elif isinstance(val, (int, float)):
                return str(val)
            elif isinstance(val, str):
                return json.dumps(val)
            elif isinstance(val, list):
                # Check if list contains only numbers
                if all(isinstance(x, (int, float)) for x in val):
                    # format on single line
                    items_str = ", ".join(str(x) for x in val)
                    return f"[{items_str}]"
                else:
                    parts = [_to_json(item, level + 1) for item in val]
                    return "[\n" + ",\n".join(ind_inner + p for p in parts) + "\n" + ind + "]"
            elif isinstance(val, dict):
                if not val:
                    return "{}"
                parts = []
                for k, v in val.items():
                    key_str = json.dumps(k)
                    val_str = _to_json(v, level + 1)
                    parts.append(f"{ind_inner}{key_str}: {val_str}")
                return "{\n" + ",\n".join(parts) + "\n" + ind + "}"
            else:
                return json.dumps(val)

        return _to_json(obj, 0)

    output_str = custom_dump(data, indent=2) + "\n"
    with open(project_path, "w", encoding="utf-8") as f:
        f.write(output_str)

    print(f"Successfully updated {project_path}")

if __name__ == "__main__":
    main()
