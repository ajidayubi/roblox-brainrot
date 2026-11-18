import json
import os
import sys

def upgrade_landmarks(filepath="default.project.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    workspace = data.get("tree", {}).get("Workspace", {})
    decor = workspace.get("Decor", {})

    if "FlagPole1" in decor:
        print("Error: FlagPole1 already exists in Decor.", file=sys.stderr)
        sys.exit(1)

    # STEP 1: Enlarge the beacon
    if "BeaconPole" in decor:
        decor["BeaconPole"]["$properties"]["Size"] = [5, 38, 5]
    if "BeaconBall" in decor:
        decor["BeaconBall"]["$properties"]["Size"] = [12, 12, 12]

    # STEP 2: Four tall flag poles and colored balls at plaza corners
    poles_data = [
        ("FlagPole1", [45, 7.5, 45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part", None),
        ("FlagPole2", [45, 7.5, -45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part", None),
        ("FlagPole3", [-45, 7.5, 45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part", None),
        ("FlagPole4", [-45, 7.5, -45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part", None),
        
        ("FlagBall1", [45, 16, 45], [5, 5, 5], [1, 0.2, 0.2], "Part", "Ball"),
        ("FlagBall2", [45, 16, -45], [5, 5, 5], [0.2, 0.5, 1], "Part", "Ball"),
        ("FlagBall3", [-45, 16, 45], [5, 5, 5], [0.2, 0.8, 0.2], "Part", "Ball"),
        ("FlagBall4", [-45, 16, -45], [5, 5, 5], [1, 0.9, 0], "Part", "Ball"),
    ]

    for name, pos, size, color, class_name, shape in poles_data:
        props = {
            "Anchored": True,
            "Position": pos,
            "Size": size,
            "Color": color
        }
        if shape:
            props["Shape"] = shape
        decor[name] = {
            "$className": class_name,
            "$properties": props
        }

    def custom_dump(obj):
        def format_val(v, indent_level=0):
            ind = "  " * indent_level
            if isinstance(v, dict):
                if not v:
                    return "{}"
                items = []
                for k, subval in v.items():
                    items.append(f'{ind}  "{k}": {format_val(subval, indent_level + 1)}')
                return "{\n" + ",\n".join(items) + f"\n{ind}}}"
            elif isinstance(v, list):
                if all(not isinstance(x, (dict, list)) for x in v):
                    items_str = ", ".join(json.dumps(x) for x in v)
                    return f"[{items_str}]"
                else:
                    items = [f'{ind}  {format_val(x, indent_level + 1)}' for x in v]
                    return "[\n" + ",\n".join(items) + f"\n{ind}]"
            else:
                return json.dumps(v)

        return format_val(obj, 0)

    output = custom_dump(data) + "\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)

    print("Successfully upgraded landmarks in default.project.json.")

if __name__ == "__main__":
    upgrade_landmarks()
