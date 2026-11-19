import json
import math
import os
import sys

def format_json_compact(obj, indent=2):
    """
    Serializes obj to JSON with 2-space indent, ensuring that any list containing
    only numbers (ints or floats) is formatted on a single line.
    The closing bracket of an object is always '}'.
    """
    def is_num_list(val):
        return isinstance(val, list) and len(val) > 0 and all(isinstance(x, (int, float)) for x in val)

    def _to_json(o, level=0):
        spaces = " " * (indent * level)
        next_spaces = " " * (indent * (level + 1))
        
        if isinstance(o, dict):
            if not o:
                return "{}"
            items = []
            for k, v in o.items():
                key_str = json.dumps(k)
                val_str = _to_json(v, level + 1)
                items.append(f"{next_spaces}{key_str}: {val_str}")
            joined = ",\n".join(items)
            return f"{{\n{joined}\n{spaces}}}"
        elif is_num_list(o):
            # Format list of numbers on a single line
            items_str = ", ".join(json.dumps(x) for x in o)
            return f"[{items_str}]"
        elif isinstance(o, list):
            if not o:
                return "[]"
            items = []
            for item in o:
                items.append(f"{next_spaces}{_to_json(item, level + 1)}")
            joined = ",\n".join(items)
            return f"[\n{joined}\n{spaces}]"
        else:
            return json.dumps(o)

    return _to_json(obj, 0) + "\n"

def main():
    project_path = "default.project.json"
    if not os.path.exists(project_path):
        print(f"Error: {project_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(project_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Navigate to Workspace
    try:
        workspace = data["tree"]["Workspace"]
    except KeyError:
        print("Error: tree.Workspace not found in project file.", file=sys.stderr)
        sys.exit(1)

    # Conveyor rename check / update
    if "Conveyor" in workspace:
        workspace["ConveyorBelt"] = workspace.pop("Conveyor")
    elif "ConveyorBelt" not in workspace:
        # If neither exists, we could either create or ignore; instructions say:
        # "Rename the top-level part called "Conveyor" to "ConveyorBelt", keeping all its properties... If "ConveyorBelt" already exists instead, leave it alone."
        pass

    # Refuse to run if Rides folder already exists under Workspace
    if "Rides" in workspace:
        print("Error: Top-level folder 'Rides' already exists under Workspace.", file=sys.stderr)
        sys.exit(1)

    rides = {
        "$className": "Folder"
    }

    added_count = 0

    # Shared colors
    yellow = [1, 0.8, 0.2]
    grey = [0.5, 0.5, 0.5]
    red = [1, 0.2, 0.2]
    dark_col = [0.2, 0.2, 0.2]

    # Helper for part node
    def make_part(pos, size, color, shape=None, cframe=None):
        props = {
            "Anchored": True,
            "Position": pos,
            "Size": size,
            "Color": color
        }
        if shape:
            props["Shape"] = shape
        if cframe:
            props["CFrame"] = cframe
        return {
            "$className": "Part",
            "$properties": props
        }

    # 1. Ferris Wheel Model
    ferris_wheel = {
        "$className": "Model",
        "TowerL": make_part([-76, 10, -50], [2, 20, 2], grey),
        "TowerR": make_part([-64, 10, -50], [2, 20, 2], grey),
        "Hub": make_part([-70, 20, -50], [3, 3, 3], red)
    }

    # Spokes (rotated about Z axis by 0, 45, 90, 135)
    # Z-axis rotation matrix rows: (cos, -sin, 0), (sin, cos, 0), (0, 0, 1)
    def z_rot_cframe(x, y, z, angle_deg):
        th = math.radians(angle_deg)
        c = math.cos(th)
        s = math.sin(th)
        # cframe 12 numbers: pos(3) + 3x3 rotation matrix flattened row-major or column-major?
        # Wait, Roblox CFrame components in JSON usually list position + 9 elements of rotation matrix.
        # Let's check instructions: "a 12-number orientation list called CFrame (position followed by a 3 by 3 rotation matrix)."
        # Row-major or column-major? Rotation about Z:
        # [ c, -s,  0 ]
        # [ s,  c,  0 ]
        # [ 0,  0,  1 ]
        # Flattened row-major: c, -s, 0, s, c, 0, 0, 0, 1
        return [x, y, z, c, -s, 0, s, c, 0, 0, 0, 1]

    spoke_angles = [0, 45, 90, 135]
    for idx, ang in enumerate(spoke_angles, 1):
        # each 24 long, 1 thick, 1 deep, yellow, rotated about Z by ang
        # center at hub (-70, 20, -50)
        cframe = z_rot_cframe(-70, 20, -50, ang)
        ferris_wheel[f"Spoke{idx}"] = make_part([-70, 20, -50], [24, 1, 1], yellow, cframe=cframe)

    # 8 rim pieces
    rim_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    cabin_colors = [
        red,
        [1, 0.5, 0],       # orange
        [1, 0.9, 0],       # yellow
        [0.2, 0.8, 0.2],   # green
        [0.2, 0.5, 1],     # blue
        [0.6, 0.2, 0.8],   # purple
        [1, 0.5, 0.8],     # pink
        [0.2, 0.8, 1]      # cyan
    ]

    for idx, ang in enumerate(rim_angles, 1):
        x = round(-70 + 12 * math.cos(math.radians(ang)), 1)
        y = round(20 + 12 * math.sin(math.radians(ang)), 1)
        z = -50
        # rim piece rotated about Z by ang + 90
        rim_cframe = z_rot_cframe(x, y, z, ang + 90)
        ferris_wheel[f"Rim{idx}"] = make_part([x, y, z], [9, 1, 1], yellow, cframe=rim_cframe)

    rides["FerrisWheel"] = ferris_wheel
    added_count += 1

    # Eight cabins as direct children of Rides folder
    for idx, ang in enumerate(rim_angles, 1):
        x = round(-70 + 12 * math.cos(math.radians(ang)), 1)
        y = round(20 + 12 * math.sin(math.radians(ang)), 1)
        z = -50
        col = cabin_colors[idx - 1]
        rides[f"Cabin{idx}"] = make_part([x, y, z], [3, 3, 3], col)
        added_count += 1

    # 2. Carousel Model at (65, -50)
    carousel = {
        "$className": "Model",
        "Platform": make_part([65, 0.5, -50], [16, 1, 16], red),
        "Pole": make_part([65, 4.5, -50], [2, 8, 2], yellow),
        "Roof": make_part([65, 9.5, -50], [18, 3, 18], [0.8, 0.2, 0.8], shape="Ball"),
        "Horse1": make_part([70, 2.5, -50], [2, 3, 4], [1, 1, 1]), # white
        "Horse2": make_part([65, 2.5, -45], [4, 3, 2], [0.5, 0.35, 0.2]), # brown
        "Horse3": make_part([60, 2.5, -50], [2, 3, 4], [0, 0, 0]), # black
        "Horse4": make_part([65, 2.5, -55], [4, 3, 2], [0.8, 0.8, 0.8])  # light grey
    }
    rides["Carousel"] = carousel
    added_count += 1

    # 3. Slide at (-60, 60), direct children of Rides
    # X-axis rotation matrix for 30 degrees about X:
    # [ 1,  0,       0      ]
    # [ 0,  cos,    -sin    ]
    # [ 0,  sin,     cos    ]
    th_slide = math.radians(30)
    c_s = math.cos(th_slide)
    s_s = math.sin(th_slide)
    slide_chute_cframe = [-60, 3.5, 61, 1, 0, 0, 0, c_s, -s_s, 0, s_s, c_s]

    slide_parts = {
        "SlidePlatform": make_part([-60, 6, 56], [5, 0.5, 5], red),
        "SlideChute": make_part([-60, 3.5, 61], [4, 0.5, 10], [1, 0.9, 0], cframe=slide_chute_cframe),
        "LadderPole1": make_part([-62, 3, 53.5], [1, 6, 1], grey),
        "LadderPole2": make_part([-58, 3, 53.5], [1, 6, 1], grey),
        "LadderRung1": make_part([-60, 2, 53.5], [4, 0.5, 0.5], grey),
        "LadderRung2": make_part([-60, 3.5, 53.5], [4, 0.5, 0.5], grey),
        "LadderRung3": make_part([-60, 5, 53.5], [4, 0.5, 0.5], grey),
    }
    for name, part in slide_parts.items():
        rides[name] = part
        added_count += 1

    # 4. Swing set at (60, 60), direct children of Rides
    swing_parts = {
        "SwingTopBar": make_part([60, 6, 60], [10, 1, 1], [0.2, 0.5, 1]),
        "SwingLeg1": make_part([56, 3, 58.5], [1, 6, 1], [0.2, 0.5, 1]),
        "SwingLeg2": make_part([56, 3, 61.5], [1, 6, 1], [0.2, 0.5, 1]),
        "SwingLeg3": make_part([64, 3, 58.5], [1, 6, 1], [0.2, 0.5, 1]),
        "SwingLeg4": make_part([64, 3, 61.5], [1, 6, 1], [0.2, 0.5, 1]),
    }
    for name, part in swing_parts.items():
        rides[name] = part
        added_count += 1

    # Two swing Models: Swing1 (x=57.5, red seat) and Swing2 (x=62.5, yellow seat)
    for name, x_pos, seat_col in [("Swing1", 57.5, red), ("Swing2", 62.5, [1, 0.9, 0])]:
        swing_model = {
            "$className": "Model",
            "Pivot": make_part([x_pos, 6, 60], [1, 1, 1], [0.2, 0.2, 0.2]),
            "ChainA": make_part([x_pos - 1, 3.75, 60], [0.3, 4.5, 0.3], [0.7, 0.7, 0.7]),
            "ChainB": make_part([x_pos + 1, 3.75, 60], [0.3, 4.5, 0.3], [0.7, 0.7, 0.7]),
            "Seat": make_part([x_pos, 1.25, 60], [2.5, 0.5, 1.5], seat_col)
        }
        rides[name] = swing_model
        added_count += 1

    # 5. Bumper car arena at (-70, 20), direct children of Rides
    bumper_items = {
        "BumperFloor": make_part([-70, 0.5, 20], [24, 0.5, 24], dark_col),
        "BumperWallN": make_part([-70, 1, 8], [24, 2, 1], red),
        "BumperWallS": make_part([-70, 1, 32], [24, 2, 1], red),
        "BumperWallW": make_part([-82, 1, 20], [1, 2, 24], red),
        "BumperWallE": make_part([-58, 1, 20], [1, 2, 24], red),
        "BumperCar1": make_part([-76, 1.5, 14], [4, 1.5, 3], red),
        "BumperCar2": make_part([-64, 1.5, 14], [4, 1.5, 3], [0.2, 0.5, 1]), # blue
        "BumperCar3": make_part([-76, 1.5, 26], [4, 1.5, 3], [0.2, 0.8, 0.2]), # green
        "BumperCar4": make_part([-64, 1.5, 26], [4, 1.5, 3], [1, 0.9, 0]), # yellow
    }
    for name, part in bumper_items.items():
        rides[name] = part
        added_count += 1

    # 6. Roller coaster loop centred at (-110, -30), direct children of Rides
    # 16 pads
    pad_positions = []
    for i in range(16):
        angle = i * 22.5
        th = math.radians(angle)
        x = round(-110 + 25 * math.cos(th), 1)
        z = -30 + 40 * math.sin(th) # Wait, instructions say x and z rounded to one decimal. Let's round both.
        z = round(z, 1)
        y = round(5 + 3 * math.sin(2 * th), 1)
        pad_positions.append((x, y, z))
        pad_name = f"CoasterPad{i+1}"
        rides[pad_name] = make_part([x, y, z], [4, 0.5, 4], [0.3, 0.3, 0.3])
        added_count += 1

    # Two coaster cars as direct-child Models: CoasterCar1 at pad 0 (index 0) and CoasterCar2 at pad 8 (index 8)
    for car_name, pad_idx, body_col in [("CoasterCar1", 0, red), ("CoasterCar2", 8, [0.2, 0.5, 1])]:
        px, py, pz = pad_positions[pad_idx]
        top_y = py + 1.5
        car_model = {
            "$className": "Model",
            "Body": make_part([px, py, pz], [3, 2, 5], body_col),
            "Top": make_part([px, top_y, pz], [2, 1, 3], yellow)
        }
        rides[car_name] = car_model
        added_count += 1

    # Attach Rides folder to Workspace
    workspace["Rides"] = rides

    # Save output
    output_content = format_json_compact(data, indent=2)
    with open(project_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"Successfully added Rides folder with {added_count} children items/models to default.project.json.")

if __name__ == "__main__":
    main()
