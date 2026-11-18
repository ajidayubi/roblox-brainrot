import json
import math
import os

def rot_z_matrix(theta_deg):
    theta = math.radians(theta_deg)
    c = round(math.cos(theta), 4)
    s = round(math.sin(theta), 4)
    return [c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0]

def make_part_node(class_name, properties, children=None):
    node = {
        "$className": class_name,
        "$properties": properties
    }
    if children:
        for k, v in children.items():
            node[k] = v
    return node

def format_json_compact_lists(obj, indent=2):
    def _encode(o, current_indent):
        space = " " * current_indent
        next_space = " " * (current_indent + indent)
        
        if isinstance(o, dict):
            if not o:
                return "{}"
            items = []
            for k, v in o.items():
                key_str = json.dumps(k)
                val_str = _encode(v, current_indent + indent)
                items.append(f"{next_space}{key_str}: {val_str}")
            return "{\n" + ",\n".join(items) + "\n" + space + "}"
        elif isinstance(o, list):
            if all(isinstance(x, (int, float)) for x in o):
                formatted_nums = []
                for x in o:
                    if isinstance(x, float):
                        if x.is_integer():
                            formatted_nums.append(str(int(x)))
                        else:
                            formatted_nums.append(str(x))
                    else:
                        formatted_nums.append(str(x))
                return "[" + ", ".join(formatted_nums) + "]"
            else:
                if not o:
                    return "[]"
                items = []
                for item in o:
                    items.append(next_space + _encode(item, current_indent + indent))
                return "[\n" + ",\n".join(items) + "\n" + space + "]"
        elif isinstance(o, str):
            return json.dumps(o)
        elif isinstance(o, bool):
            return "true" if o else "false"
        elif o is None:
            return "null"
        else:
            return str(o)

    return _encode(obj, 0) + "\n"

def main():
    project_path = "default.project.json"
    rides_luau_path = "src/server/Rides.luau"

    rainbow = [
        [1, 0.2, 0.2],     # red
        [1, 0.5, 0],       # orange
        [1, 0.9, 0],       # yellow
        [0.2, 0.8, 0.2],   # green
        [0.2, 0.5, 1],     # blue
        [0.6, 0.2, 0.8],   # purple
        [1, 0.5, 0.8],     # pink
        [0.2, 0.8, 1],     # cyan
    ]

    with open(project_path, "r") as f:
        project = json.load(f)

    workspace = project.get("tree", {}).get("Workspace", {})
    rides_folder = workspace.get("Rides", {})
    bases_folder = workspace.get("Bases", {})

    # ==========================================
    # STEP 1: Ferris wheel rebuilt bigger
    # ==========================================
    ferris_wheel_children = {}
    
    ferris_wheel_children["Hub"] = make_part_node("Part", {
        "Anchored": True,
        "Position": [58, 20, -45],
        "Size": [3, 3, 3],
        "Color": [1, 0.2, 0.2]
    })

    spoke_angles = [0, 45, 90, 135]
    for i, angle in enumerate(spoke_angles, 1):
        rot_mat = rot_z_matrix(angle)
        cframe = [58.0, 20.0, -45.0] + rot_mat
        ferris_wheel_children[f"Spoke{i}"] = make_part_node("Part", {
            "Anchored": True,
            "Position": [58, 20, -45],
            "Size": [30, 1, 1],
            "Color": [1, 0.8, 0.2],
            "CFrame": cframe
        })

    rim_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    for i, angle in enumerate(rim_angles, 1):
        rad = math.radians(angle)
        rx = 58 + 15 * math.cos(rad)
        ry = 20 + 15 * math.sin(rad)
        rz = -45.0
        
        rot_mat = rot_z_matrix(angle + 90)
        cframe = [round(rx, 1), round(ry, 1), round(rz, 1)] + rot_mat
        
        ferris_wheel_children[f"Rim{i}"] = make_part_node("Part", {
            "Anchored": True,
            "Position": [round(rx, 1), round(ry, 1), round(rz, 1)],
            "Size": [11, 1, 1],
            "Color": rainbow[(i - 1) % len(rainbow)],
            "CFrame": cframe
        })

    ferris_wheel_children["TowerL"] = make_part_node("Part", {
        "Anchored": True,
        "Position": [52, 10, -45],
        "Size": [2, 20, 2],
        "Color": [0.5, 0.5, 0.5]
    })
    ferris_wheel_children["TowerR"] = make_part_node("Part", {
        "Anchored": True,
        "Position": [64, 10, -45],
        "Size": [2, 20, 2],
        "Color": [0.5, 0.5, 0.5]
    })

    rides_folder["FerrisWheel"] = make_part_node("Model", {}, ferris_wheel_children)

    cabin_points = [
        (73.0, 20.0, -45.0),
        (68.6, 30.6, -45.0),
        (58.0, 35.0, -45.0),
        (47.4, 30.6, -45.0),
        (43.0, 20.0, -45.0),
        (47.4, 9.4, -45.0),
        (58.0, 5.0, -45.0),
        (68.6, 9.4, -45.0),
    ]

    keys_to_remove = [k for k in rides_folder.keys() if k.startswith("Cabin")]
    for k in keys_to_remove:
        del rides_folder[k]

    for i, pos in enumerate(cabin_points, 1):
        rides_folder[f"Cabin{i}"] = make_part_node("Part", {
            "Anchored": True,
            "Position": list(pos),
            "Size": [4, 4, 4],
            "Color": rainbow[(i - 1) % len(rainbow)]
        })

    # ==========================================
    # STEP 2: Carousel bright horses and gold roof ball
    # ==========================================
    carousel_model = rides_folder.get("Carousel")
    if carousel_model and isinstance(carousel_model, dict):
        horse_colors = {
            "Horse1": [1, 0.5, 0.8],
            "Horse2": [0.2, 0.5, 1],
            "Horse3": [1, 0.9, 0],
            "Horse4": [0.2, 0.8, 0.2]
        }
        for h_name, h_col in horse_colors.items():
            if h_name in carousel_model and isinstance(carousel_model[h_name], dict):
                props = carousel_model[h_name].get("$properties", {})
                props["Color"] = h_col
                carousel_model[h_name]["$properties"] = props

        carousel_model["RoofTop"] = make_part_node("Part", {
            "Anchored": True,
            "Shape": "Ball",
            "Position": [-58, 11.5, -45],
            "Size": [4, 2, 4],
            "Color": [1, 0.8, 0.2]
        })

    # ==========================================
    # STEP 3: Market stalls: tent peaks and goods
    # ==========================================
    for b_key, b_val in list(bases_folder.items()):
        if b_key.startswith("$") or not isinstance(b_val, dict):
            continue
        
        pad = b_val.get("Pad")
        if pad and isinstance(pad, dict):
            pad_props = pad.get("$properties", {})
            pos = pad_props.get("Position")
            if pos and len(pos) >= 3:
                cx, cz = pos[0], pos[2]
                
                b_val["Peak"] = make_part_node("Part", {
                    "Anchored": True,
                    "Position": [cx, 7.5, cz],
                    "Size": [12, 1.5, 12],
                    "Color": [1, 1, 1]
                })

                fz = -1 if cz < 0 else 1
                
                goods_x_offsets = [-6, -3, 0, 3, 6]
                goods_colors = [
                    [1, 0.2, 0.2],     # red
                    [1, 0.9, 0],       # yellow
                    [0.2, 0.8, 0.2],   # green
                    [0.2, 0.5, 1],     # blue
                    [1, 0.5, 0.8],     # pink
                ]

                for idx, (ox, gcol) in enumerate(zip(goods_x_offsets, goods_colors), 1):
                    gx = cx + ox
                    gy = 3.75
                    gz = cz + fz * 9
                    b_val[f"Goods{idx}"] = make_part_node("Part", {
                        "Anchored": True,
                        "Position": [gx, gy, gz],
                        "Size": [2, 2, 2],
                        "Color": gcol
                    })

    output_content = format_json_compact_lists(project, indent=2)
    with open(project_path, "w") as f:
        f.write(output_content)

    print("Successfully updated default.project.json")

    # ==========================================
    # STEP 4: Animator radius in Rides.luau
    # ==========================================
    if os.path.exists(rides_luau_path):
        with open(rides_luau_path, "r") as f:
            luau_text = f.read()
        
        target_str = "Vector3.new(12 * math.cos(angle), 12 * math.sin(angle), 0)"
        replacement_str = "Vector3.new(15 * math.cos(angle), 15 * math.sin(angle), 0)"
        
        if target_str in luau_text:
            luau_text = luau_text.replace(target_str, replacement_str)
            with open(rides_luau_path, "w") as f:
                f.write(luau_text)
            print("Successfully updated Rides.luau radius from 12 to 15.")
        else:
            print("Warning: Target string not found in Rides.luau.")
    else:
        print(f"Warning: {rides_luau_path} not found.")

if __name__ == "__main__":
    main()
