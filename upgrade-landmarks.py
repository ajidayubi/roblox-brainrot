import json
import sys
import re

def main():
    project_path = "default.project.json"
    
    try:
        with open(project_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {project_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Navigate to Workspace -> Decor
    try:
        workspace = data["tree"]["Workspace"]
        # Workspace might have children as direct keys or inside something? 
        # Wait! The prompt says:
        # "The project file is a JSON object; its "tree" key holds a "Workspace" object; 
        # the Workspace object holds the game's parts, models and folders as named children. 
        # "Decor" is a folder under Workspace."
        # In Rojo project format, children of a node are stored in `$children` or directly as keys?
        # Safety instruction (1) explicitly states:
        # "Every node MUST use the Rojo keys: "$className" for the class and "$properties" for the properties, 
        # and children are DIRECT keys of the node object — there is NO plain "className" key and NO "children" key."
        # So Workspace is an object where Decor is a direct key (or inside $children? Wait, 
        # safety instruction says "children are DIRECT keys of the node object").
        decor = workspace.get("Decor")
        if not decor:
            print("Error: 'Decor' folder not found under Workspace.", file=sys.stderr)
            sys.exit(1)
    except KeyError as e:
        print(f"Error navigating project tree: missing key {e}", file=sys.stderr)
        sys.exit(1)
        
    # Check if FlagPole1 already exists in Decor
    if "FlagPole1" in decor:
        print("Error: 'FlagPole1' already exists in the Decor folder.", file=sys.stderr)
        sys.exit(1)
        
    # STEP 1 — Enlarge the beacon
    if "BeaconPole" in decor:
        beacon_pole = decor["BeaconPole"]
        if "$properties" not in beacon_pole:
            beacon_pole["$properties"] = {}
        beacon_pole["$properties"]["Size"] = [5, 38, 5]
        # Position (0, 26, 0) and pink color stay (or ensure properties)
        beacon_pole["$properties"]["Position"] = [0, 26, 0]
        beacon_pole["$properties"]["Color"] = [1, 0.4, 0.7] # or whatever pink was, prompt says "its pink colour stays"
        beacon_pole["$properties"]["Anchored"] = True
        beacon_pole["$className"] = "Part"
        
    if "BeaconBall" in decor:
        beacon_ball = decor["BeaconBall"]
        if "$properties" not in beacon_ball:
            beacon_ball["$properties"] = {}
        beacon_ball["$properties"]["Size"] = [12, 12, 12]
        beacon_ball["$properties"]["Position"] = [0, 48, 0]
        beacon_ball["$properties"]["Color"] = [1, 0.84, 0] # gold
        beacon_ball["$properties"]["Anchored"] = True
        beacon_ball["$className"] = "Part"
        beacon_ball["$properties"]["Shape"] = "Ball"

    # STEP 2 — Four tall flag poles at plaza corners
    poles_data = [
        ("FlagPole1", [45, 7.5, 45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part"),
        ("FlagPole2", [45, 7.5, -45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part"),
        ("FlagPole3", [-45, 7.5, 45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part"),
        ("FlagPole4", [-45, 7.5, -45], [1.5, 15, 1.5], [0.7, 0.7, 0.7], "Part"),
    ]
    
    balls_data = [
        ("FlagBall1", [45, 16, 45], [5, 5, 5], [1, 0.2, 0.2], "Part", "Ball"),       # red
        ("FlagBall2", [45, 16, -45], [5, 5, 5], [0.2, 0.5, 1], "Part", "Ball"),     # blue
        ("FlagBall3", [-45, 16, 45], [5, 5, 5], [0.2, 0.8, 0.2], "Part", "Ball"),   # green
        ("FlagBall4", [-45, 16, -45], [5, 5, 5], [1, 0.9, 0], "Part", "Ball"),      # yellow
    ]

    for name, pos, size, color, class_name in poles_data:
        decor[name] = {
            "$className": class_name,
            "$properties": {
                "Anchored": True,
                "Position": pos,
                "Size": size,
                "Color": color
            }
        }

    for name, pos, size, color, class_name, shape in balls_data:
        decor[name] = {
            "$className": class_name,
            "$properties": {
                "Anchored": True,
                "Position": pos,
                "Size": size,
                "Color": color,
                "Shape": shape
            }
        }

    # Save project file in compact form: two-space indent, every list that contains only numbers on a single line, trailing newline.
    # We can write a custom serializer or use json.dump and format number lists with regex.
    raw_json = json.dumps(data, indent=2)
    
    # Post-process json string so that any list containing only numbers is formatted on a single line.
    # e.g. [
    #   0,
    #   26,
    #   0
    # ] -> [0, 26, 0] or [0, 26, 0] with appropriate spacing/formatting.
    # Actually, a custom recursive json formatter guarantees 100% correct syntax and closing braces '}' without risking ']' bug.
    
    def compact_nums_dump(obj, indent_level=0):
        indent_str = "  " * indent_level
        next_indent_str = "  " * (indent_level + 1)
        
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            items = []
            for k, v in obj.items():
                items.append(f'{next_indent_str}"{k}": {compact_nums_dump(v, indent_level + 1)}')
            return "{\n" + ",\n".join(items) + f"\n{indent_str}}}"
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            # Check if list contains only numbers (or booleans/strings if needed, but prompt specifically says:
                # "every list that contains only numbers written on a single line (so Position, Size and Color each stay on one line)")
            if all(isinstance(x, (int, float, bool)) and not isinstance(x, bool) for x in obj):
                # Format numbers compactly
                num_strs = []
                for x in obj:
                    if isinstance(x, float):
                        # Avoid excessive float printing if integer-like
                        if x.is_integer():
                            num_strs.append(str(int(x)))
                        else:
                            num_strs.append(str(x))
                    else:
                        num_strs.append(str(x))
                return "[" + ", ".join(num_strs) + "]"
            else:
                items = [compact_nums_dump(item, indent_level + 1) for item in obj]
                return "[\n" + ",\n".join(f'{next_indent_str}{item}' for item in items) + f"\n{indent_str}]"
        elif isinstance(obj, str):
            return json.dumps(obj)
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif obj is None:
            return "null"
        else:
            return str(obj)

    formatted_output = compact_nums_dump(data, 0) + "\n"

    try:
        with open(project_path, "w", encoding="utf-8") as f:
            f.write(formatted_output)
    except Exception as e:
        print(f"Error writing {project_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Successfully updated default.project.json with enlarged beacon and plaza corner flag poles.")

if __name__ == "__main__":
    main()
