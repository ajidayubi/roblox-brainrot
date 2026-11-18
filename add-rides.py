import json
import math
import os
import sys

def rotation_z(theta_deg):
    th = math.radians(theta_deg)
    c = math.cos(th)
    s = math.sin(th)
    # Row-based matrices in description:
    # Z-axis: (cos, -sin, 0), (sin, cos, 0), (0, 0, 1)
    # Plus columns for 3x3
    return [
        c, -s, 0.0,
        s,  c, 0.0,
        0.0, 0.0, 1.0
    ]

def rotation_x(theta_deg):
    th = math.radians(theta_deg)
    c = math.cos(th)
    s = math.sin(th)
    # X-axis: (1, 0, 0), (0, cos, -sin), (0, sin, cos)
    return [
        1.0, 0.0, 0.0,
        0.0,  c, -s,
        0.0,  s,  c
    ]

def make_part(pos, size, color, anchored=True, shape=None, cframe_rot=None):
    props = {
        "Anchored": anchored,
        "Position": [round(float(v), 1) for v in pos],
        "Size": [round(float(v), 1) for v in size],
        "Color": [round(float(v), 3) for v in color]
    }
    if shape:
        props["Shape"] = shape
    if cframe_rot:
        # CFrame is position (3) + 3x3 rotation matrix (9) = 12 numbers
        cf = [round(float(v), 4) for v in pos] + [round(float(v), 4) for v in cframe_rot]
        props["CFrame"] = cf
    return {
        "$className": "Part",
        "$properties": props
    }

def make_model(children):
    node = {"$className": "Model"}
    node.update(children)
    return node

class CompactJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 2

    def encode(self, o):
        return self._encode(o, 0)

    def _encode(self, obj, level):
        indent_str = "  " * level
        next_indent = "  " * (level + 1)

        if isinstance(obj, dict):
            if not obj:
                return "{}"
            items = []
            for k, v in obj.items():
                items.append(f'{next_indent}"{k}": {self._encode(v, level + 1)}')
            return "{\n" + ",\n".join(items) + f"\n{indent_str}}}"

        elif isinstance(obj, list):
            if not obj:
                return "[]"
            # Check if list contains only numbers/booleans/strings (scalar list)
            if all(isinstance(x, (int, float, bool, str)) for x in obj):
                # Format as a single line
                formatted_items = []
                for x in obj:
                    if isinstance(x, float):
                        formatted_items.append(f"{x:g}" if isinstance(x, float) else str(x)) # or standard json formatting
                    else:
                        formatted_items.append(json.dumps(x))
                # Actually json.dumps handles list of numbers nicely:
                return json.dumps(obj)
            else:
                items = []
                for x in obj:
                    items.append(f'{next_indent}{self._encode(x, level + 1)}')
                return "[\n" + ",\n".join(items) + f"\n{indent_str}]"
        else:
            return json.dumps(obj)

def main():
    proj_path = "default.project.json"
    if not os.path.exists(proj_path):
        print(f"Error: {proj_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(proj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    workspace = data.get("tree", {}).get("Workspace")
    if workspace is None:
        print("Error: Workspace not found in project tree.", file=sys.stderr)
        sys.exit(1)

    # Check Rides folder
    if "Rides" in workspace:
        print("Error: 'Rides' folder already exists in Workspace.", file=sys.stderr)
        sys.exit(1)

    # Rename Conveyor to ConveyorBelt if Conveyor exists
    if "Conveyor" in workspace and "ConveyorBelt" not in workspace:
        workspace["ConveyorBelt"] = workspace.pop("Conveyor")
    elif "ConveyorBelt" not in workspace:
        # If neither exists, or ConveyorBelt already exists, we do nothing or ensure it's handled.
        pass

    yellow = (1.0, 0.8, 0.2)
    grey = (0.5, 0.5, 0.5)
    red = (1.0, 0.2, 0.2)

    rides_children = {}

    # 1. Ferris Wheel Model & Cabins
    # Centre (-70, 20, -50), radius 12, Z = -50
    ferris_children = {
        "TowerL": make_part((-76, 10, -50), (2, 20, 2), grey),
        "TowerR": make_part((-64, 10, -50), (2, 20, 2), grey),
        "Hub": make_part((-70, 20, -50), (3, 3, 3), red)
    }

    spoke_angles = [0, 45, 90, 135]
    for idx, ang in enumerate(spoke_angles, 1):
        rot = rotation_z(ang)
        ferris_children[f"Spoke{idx}"] = make_part((-70, 20, -50), (24, 1, 1), yellow, cframe_rot=rot)

    rim_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    cabin_colors = [
        (1.0, 0.2, 0.2), # red
        (1.0, 0.5, 0.0), # orange
        (1.0, 0.9, 0.0), # yellow
        (0.2, 0.8, 0.2), # green
        (0.2, 0.5, 1.0), # blue
        (0.6, 0.2, 0.8), # purple
        (1.0, 0.5, 0.8), # pink
        (0.2, 0.8, 1.0)  # cyan
    ]

    for idx, ang in enumerate(rim_angles, 1):
        rad = math.radians(ang)
        cx = round(-70.0 + 12.0 * math.cos(rad), 1)
        cy = round(20.0 + 12.0 * math.sin(rad), 1)
        cz = -50.0
        # rim piece: 9 long, 1 thick, 1 deep, yellow, rotated about Z by angle + 90
        rim_rot = rotation_z(ang + 90)
        ferris_children[f"Rim{idx}"] = make_part((cx, cy, cz), (9, 1, 1), yellow, cframe_rot=rim_rot)

        # Cabin as direct child of Rides folder
        ccolor = cabin_colors[idx - 1]
        rides_children[f"Cabin{idx}"] = make_part((cx, cy, cz), (3, 3, 3), ccolor)

    rides_children["FerrisWheel"] = make_model(ferris_children)

    # 2. Carousel at (65, -50)
    carousel_children = {
        "Platform": make_part((65, 0.5, -50), (16, 1, 16), red),
        "Pole": make_part((65, 4.5, -50), (2, 8, 2), yellow),
        "Roof": make_part((65, 9.5, -50), (18, 3, 18), (0.8, 0.2, 0.8), shape="Ball"),
        "Horse1": make_part((70, 2.5, -50), (2, 3, 4), (1.0, 1.0, 1.0)), # white
        "Horse2": make_part((65, 2.5, -45), (4, 3, 2), (0.5, 0.35, 0.2)), # brown
        "Horse3": make_part((60, 2.5, -50), (2, 3, 4), (0.0, 0.0, 0.0)), # black (or dark) - description says black, let's use (0.1, 0.1, 0.1) or (0,0,0)
        "Horse4": make_part((65, 2.5, -55), (4, 3, 2), (0.8, 0.8, 0.8))  # light grey
    }
    # Fix black horse color to strictly valid rgb or (0.1, 0.1, 0.1) or (0,0,0)
    carousel_children["Horse3"]["$properties"]["Color"] = [0.1, 0.1, 0.1]
    rides_children["Carousel"] = make_model(carousel_children)

    # 3. Slide at (-60, 60), direct children of Rides
    slide_chute_rot = rotation_x(30)
    rides_children["SlidePlatform"] = make_part((-60, 6, 56), (5, 0.5, 5), red)
    rides_children["SlideChute"] = make_part((-60, 3.5, 61), (4, 0.5, 10), (1.0, 0.9, 0.0), cframe_rot=slide_chute_rot)
    rides_children["LadderPole1"] = make_part((-62, 3, 53.5), (1, 6, 1), grey)
    rides_children["LadderPole2"] = make_part((-58, 3, 53.5), (1, 6, 1), grey)
    rides_children["LadderRung1"] = make_part((-60, 2, 53.5), (4, 0.5, 0.5), grey)
    rides_children["LadderRung2"] = make_part((-60, 3.5, 53.5), (4, 0.5, 0.5), grey)
    rides_children["LadderRung3"] = make_part((-60, 5, 53.5), (4, 0.5, 0.5), grey)

    # 4. Swing set at (60, 60), direct children of Rides
    blue_color = (0.2, 0.5, 1.0)
    light_grey = (0.7, 0.7, 0.7)
    dark_color = (0.2, 0.2, 0.2)
    yellow_seat = (1.0, 0.9, 0.0)

    rides_children["SwingTopBar"] = make_part((60, 6, 60), (10, 1, 1), blue_color)
    rides_children["SwingLeg1"] = make_part((56, 3, 58.5), (1, 6, 1), blue_color)
    rides_children["SwingLeg2"] = make_part((56, 3, 61.5), (1, 6, 1), blue_color)
    rides_children["SwingLeg3"] = make_part((64, 3, 58.5), (1, 6, 1), blue_color)
    rides_children["SwingLeg4"] = make_part((64, 3, 61.5), (1, 6, 1), blue_color)

    # Two swing Models: Swing1 (x=57.5, red seat), Swing2 (x=62.5, yellow seat)
    for name, sx, seat_col in [("Swing1", 57.5, red), ("Swing2", 62.5, yellow_seat)]:
        swing_children = {
            "Pivot": make_part((sx, 6, 60), (1, 1, 1), dark_color),
            "ChainA": make_part((sx - 1, 3.75, 60), (0.3, 4.5, 0.3), light_grey),
            "ChainB": make_part((sx + 1, 3.75, 60), (0.3, 4.5, 0.3), light_grey),
            "Seat": make_part((sx, 1.25, 60), (2.5, 0.5, 1.5), seat_col)
        }
        rides_children[name] = make_model(swing_children)

    # 5. Bumper car arena at (-70, 20), direct children of Rides
    rides_children["BumperFloor"] = make_part((-70, 0.5, 20), (24, 0.5, 24), dark_color)
    rides_children["BumperWallN"] = make_part((-70, 1, 8), (24, 2, 1), red)
    rides_children["BumperWallS"] = make_part((-70, 1, 32), (24, 2, 1), red)
    rides_children["BumperWallW"] = make_part((-82, 1, 20), (1, 2, 24), red)
    rides_children["BumperWallE"] = make_part((-58, 1, 20), (1, 2, 24), red)

    rides_children["BumperCar1"] = make_part((-76, 1.5, 14), (4, 1.5, 3), red)
    rides_children["BumperCar2"] = make_part((-64, 1.5, 14), (4, 1.5, 3), blue_color)
    rides_children["BumperCar3"] = make_part((-76, 1.5, 26), (4, 1.5, 3), (0.2, 0.8, 0.2))
    rides_children["BumperCar4"] = make_part((-64, 1.5, 26), (4, 1.5, 3), yellow_seat)

    # 6. Roller coaster loop centred at (-110, -30), direct children of Rides
    pad_positions = []
    pad_color = (0.3, 0.3, 0.3)
    for i in range(16):
        angle_deg = i * 22.5
        angle_rad = math.radians(angle_deg)
        px = round(-110.0 + 25.0 * math.cos(angle_rad), 1)
        pz = round(-30.0 + 40.0 * math.sin(angle_rad), 1)
        py = round(5.0 + 3.0 * math.sin(2.0 * angle_rad), 1)
        pad_positions.append((px, py, pz))
        rides_children[f"CoasterPad{i+1}"] = make_part((px, py, pz), (4, 0.5, 4), pad_color)

    # Checkpoint values check according to description:
    # pad 0 is (-85, 5, -30) -> let's verify pad_positions[0]: px = -110 + 25 = -85, pz = -30, py = 5 + 3*sin(0) = 5. Exact!

    # Two cars as direct-child Models: CoasterCar1 at pad 0 (index 0) and CoasterCar2 at pad 8 (index 8)
    for car_name, pad_idx, body_col in [("CoasterCar1", 0, red), ("CoasterCar2", 8, blue_color)]:
        pos = pad_positions[pad_idx]
        bx, by, bz = pos
        top_y = by + 1.5
        car_children = {
            "Body": make_part((bx, by, bz), (3, 2, 5), body_col),
            "Top": make_part((bx, top_y, bz), (2, 1, 3), yellow_seat)
        }
        rides_children[car_name] = make_model(car_children)

    # Create Rides folder in Workspace
    workspace["Rides"] = {
        "$className": "Folder"
    }
    workspace["Rides"].update(rides_children)

    # Save using CompactJSONEncoder
    with open(proj_path, "w", encoding="utf-8") as f:
        encoder = CompactJSONEncoder()
        f.write(encoder.encode(data) + "\n")

    count = len(rides_children)
    print(f"Successfully added Rides folder with {count} children to default.project.json.")

if __name__ == "__main__":
    main()
