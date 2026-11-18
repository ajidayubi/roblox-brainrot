import json
import math
import sys
import os

def format_json_compact(obj, indent=2):
    """
    Custom JSON serializer that formats numbers lists on a single line,
    while using proper standard JSON formatting with proper braces {} and brackets [].
    Ensures that object closing brackets are '}' and not ']'!
    """
    def _to_json(o, level=0):
        ind = " " * (level * indent)
        next_ind = " " * ((level + 1) * indent)
        
        if isinstance(o, bool):
            return "true" if o else "false"
        elif o is None:
            return "null"
        elif isinstance(o, (int, float)):
            # Format floats neatly if needed, or str(o)
            if isinstance(o, float):
                # avoid trailing .0 if integer, or keep standard representation
                if o.is_integer():
                    return str(int(o))
                return str(o)
            return str(o)
        elif isinstance(o, str):
            return json.dumps(o)
        elif isinstance(o, list):
            # Check if list contains only numbers (or is empty)
            is_num_list = len(o) == 0 or all(isinstance(x, (int, float)) for x in o)
            if is_num_list:
                # Format numbers list on a single line
                items = []
                for x in o:
                    if isinstance(x, float):
                        if x.is_integer():
                            items.append(str(int(x)))
                        else:
                            items.append(str(x))
                    else:
                        items.append(str(x))
                return "[" + ", ".join(items) + "]"
            else:
                lines = ["["]
                for i, item in enumerate(o):
                    comma = "," if i < len(o) - 1 else ""
                    lines.append(next_ind + _to_json(item, level + 1) + comma)
                lines.append(ind + "]")
                return "\n".join(lines)
        elif isinstance(o, dict):
            if not o:
                return "{}"
            lines = ["{"]
            keys = list(o.keys())
            for i, k in enumerate(keys):
                comma = "," if i < len(keys) - 1 else ""
                val_str = _to_json(o[k], level + 1)
                lines.append(next_ind + json.dumps(k) + ": " + val_str + comma)
            lines.append(ind + "}")
            return "\n".join(lines)
        else:
            return json.dumps(o)

    return _to_json(obj, 0) + "\n"

def main():
    project_path = "default.project.json"
    if not os.path.exists(project_path):
        print(f"Error: {project_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(project_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # Find Workspace and Rides folder
    tree = data.get("tree", {})
    workspace = tree.get("Workspace", {})
    if not workspace:
        print("Error: Workspace not found in project tree.", file=sys.stderr)
        sys.exit(1)

    # Refuse to run if PlazaLife top-level folder already exists under Workspace
    if "PlazaLife" in workspace:
        print("Error: PlazaLife folder already exists under Workspace.", file=sys.stderr)
        sys.exit(1)

    rides = workspace.get("Rides", {})
    if not rides:
        print("Error: Rides folder not found under Workspace.", file=sys.stderr)
        sys.exit(1)

    # Helper function to translate part properties (Position and CFrame)
    def translate_part(part_node, dx, dz):
        if not isinstance(part_node, dict):
            return
        props = part_node.get("$properties", {})
        if "Position" in props:
            pos = props["Position"]
            if isinstance(pos, list) and len(pos) == 3:
                pos[0] = round(pos[0] + dx, 1)
                pos[2] = round(pos[2] + dz, 1)
        if "CFrame" in props:
            cf = props["CFrame"]
            if isinstance(cf, list) and len(cf) >= 3:
                cf[0] = round(cf[0] + dx, 1)
                cf[2] = round(cf[2] + dz, 1)

    # 1. Move ferris wheel and carousel
    # Ferris wheel moves by +12 in x and +8 in z
    ferris_wheel = rides.get("FerrisWheel", {})
    if ferris_wheel:
        # Wheel parts inside FerrisWheel: TowerL, TowerR, Hub, Spoke1 to Spoke4, Rim1 to Rim8
        for child_name, child_node in ferris_wheel.items():
            if not child_name.startswith("$"):
                translate_part(child_node, 12, 8)
    # Cabin1 to Cabin8 are direct children of the Rides folder
    for i in range(1, 9):
        cabin_name = f"Cabin{i}"
        if cabin_name in rides:
            translate_part(rides[cabin_name], 12, 8)

    # Carousel moves by -17 in x and +8 in z
    carousel = rides.get("Carousel", {})
    if carousel:
        # Carousel parts: Platform, Pole, Roof, Horse1 to Horse4
        for child_name, child_node in carousel.items():
            if not child_name.startswith("$"):
                translate_part(child_node, -17, 8)

    # 2. Add sixteen gold rails "CoasterRail1" to "CoasterRail16" as direct children of Rides folder
    # Pad positions formula: pad i (i from 0 to 15) at angle i * 22.5 degrees
    pads = []
    for i in range(16):
        angle_deg = i * 22.5
        angle_rad = math.radians(angle_deg)
        x = round(-110 + 25 * math.cos(angle_rad), 1)
        z = round(-30 + 40 * math.sin(angle_rad), 1)
        y = round(5 + 3 * math.sin(2 * angle_rad), 1)
        pads.append((x, y, z))

    # Explicit checkpoint checks / documentation:
    # pad 0 is (-85, 5, -30); pad 4 is (-110, 5, 10); pad 8 is (-135, 5, -30); pad 12 is (-110, 5, -70)

    for i in range(16):
        pad_a = pads[i]
        pad_b = pads[(i + 1) % 16]
        
        ax, ay, az = pad_a
        bx, by, bz = pad_b
        
        # direction: pad b minus pad a
        dx, dy, dz = bx - ax, by - ay, bz - az
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        length = round(dist, 1)
        
        # midpoint: pad a plus half direction
        mx = round(ax + dx / 2.0, 1)
        my = round(ay + dy / 2.0, 1)
        mz = round(az + dz / 2.0, 1)
        
        # normalize direction to get Z axis
        if dist > 0:
            z_axis = (dx / dist, dy / dist, dz / dist)
        else:
            z_axis = (0.0, 0.0, 1.0)
            
        # cross product of up vector (0, 1, 0) with Z axis, normalized, to get X axis
        up = (0.0, 1.0, 0.0)
        cx = up[1] * z_axis[2] - up[2] * z_axis[1]
        cy = up[2] * z_axis[0] - up[0] * z_axis[2]
        cz = up[0] * z_axis[1] - up[1] * z_axis[0]
        c_len = math.sqrt(cx*cx + cy*cy + cz*cz)
        if c_len > 1e-6:
            x_axis = (cx / c_len, cy / c_len, cz / c_len)
        else:
            # fallback if parallel
            x_axis = (1.0, 0.0, 0.0)
            
        # cross product of Z axis with X axis to get Y axis
        y_axis = (
            z_axis[1] * x_axis[2] - z_axis[2] * x_axis[1],
            z_axis[2] * x_axis[0] - z_axis[0] * x_axis[2],
            z_axis[0] * x_axis[1] - z_axis[1] * x_axis[0]
        )
        
        # Twelve CFrame numbers: midpoint (3), X axis (3), Y axis (3), Z axis (3)
        cf_list = [
            round(mx, 1), round(my, 1), round(mz, 1),
            round(x_axis[0], 4), round(x_axis[1], 4), round(x_axis[2], 4),
            round(y_axis[0], 4), round(y_axis[1], 4), round(y_axis[2], 4),
            round(z_axis[0], 4), round(z_axis[1], 4), round(z_axis[2], 4)
        ]
        
        rail_name = f"CoasterRail{i+1}"
        rides[rail_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [0, 0, 0],
                "Size": [round(0.6, 1), round(0.3, 1), length],
                "Color": [1, 0.8, 0.2],
                "CFrame": cf_list
            }
        }

    # 3. Lower the despawn gate: find top-level part called "DespawnGate" in Workspace
    despawn_gate = workspace.get("DespawnGate")
    if despawn_gate and isinstance(despawn_gate, dict):
        despawn_gate["$properties"]["Position"] = [0, 2.25, -10]
        despawn_gate["$properties"]["Size"] = [14, 2.5, 1.5]
        despawn_gate["$properties"]["Color"] = [0.2, 0.2, 0.2]

    # 4. Create Folder called "PlazaLife" under Workspace with all requested items
    plaza_life = {}

    rainbow_colors = [
        [1, 0.2, 0.2],      # red
        [1, 0.5, 0],        # orange
        [1, 0.9, 0],        # yellow
        [0.2, 0.8, 0.2],    # green
        [0.2, 0.5, 1],      # blue
        [0.6, 0.2, 0.8],    # purple
        [1, 0.5, 0.8],      # pink
        [0.2, 0.8, 1]       # cyan
    ]

    added_count = 0

    # Rainbow path: 12 tiles "PathTile1" to "PathTile12" at (0, 1.1, z) where z goes 30, 26, 22, 18, 14, 10, 6, 2, -2, -6, -10, -14
    z_vals = [30, 26, 22, 18, 14, 10, 6, 2, -2, -6, -10, -14]
    for j, z in enumerate(z_vals):
        tile_name = f"PathTile{j+1}"
        color = rainbow_colors[j % 8]
        plaza_life[tile_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [0, 1.1, z],
                "Size": [6, 0.2, 4],
                "Color": color
            }
        }
        added_count += 1

    # Cross path east-west: 15 tiles "CrossTile1" to "CrossTile15" at (x, 1.1, 0) where x goes -42 to 42 step 6
    x_vals = [-42, -36, -30, -24, -18, -12, -6, 0, 6, 12, 18, 24, 30, 36, 42]
    for j, x in enumerate(x_vals):
        tile_name = f"CrossTile{j+1}"
        color = rainbow_colors[(j + 3) % 8]
        plaza_life[tile_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [x, 1.1, 0],
                "Size": [5, 0.2, 5],
                "Color": color
            }
        }
        added_count += 1

    # Scattered pastel tiles, each 5 by 0.2 by 5 at height 1.1
    pastel_tiles = [
        ("PlazaTile1", -30, 20, [1, 0.7, 0.7]),
        ("PlazaTile2", 30, 20, [0.7, 0.9, 1]),
        ("PlazaTile3", -30, -20, [0.7, 1, 0.7]),
        ("PlazaTile4", 30, -20, [1, 0.9, 0.6]),
        ("PlazaTile5", -15, 25, [0.9, 0.7, 1]),
        ("PlazaTile6", 15, -25, [0.7, 1, 1]),
        ("PlazaTile7", -40, 35, [1, 0.8, 0.9]),
        ("PlazaTile8", 40, 35, [0.8, 1, 0.8]),
        ("PlazaTile9", -20, -35, [1, 1, 0.7]),
        ("PlazaTile10", 20, -35, [0.9, 0.8, 1]),
        ("PlazaTile11", 0, 18, [0.7, 0.8, 1]),
        ("PlazaTile12", -35, 5, [1, 0.7, 0.5])
    ]
    for name, tx, tz, col in pastel_tiles:
        plaza_life[name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [tx, 1.1, tz],
                "Size": [5, 0.2, 5],
                "Color": col
            }
        }
        added_count += 1

    # Welcome arch just north of spawn, at z = 30
    plaza_life["ArchPillarL"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [-5, 6, 30],
            "Size": [2, 10, 2],
            "Color": [1, 0.2, 0.2]
        }
    }
    added_count += 1

    plaza_life["ArchPillarR"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [5, 6, 30],
            "Size": [2, 10, 2],
            "Color": [0.2, 0.5, 1]
        }
    }
    added_count += 1

    plaza_life["ArchBeam"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 11.5, 30],
            "Size": [14, 2, 2],
            "Color": [1, 0.9, 0]
        }
    }
    added_count += 1

    plaza_life["ArchSign"] = {
        "$className": "Part",
        "$properties": {
            "Anchored": True,
            "Position": [0, 9, 30],
            "Size": [9, 3, 0.5],
            "Color": [1, 0.5, 0.8]
        }
    }
    added_count += 1

    arch_ball_colors = [[1, 0.2, 0.2], [1, 0.9, 0], [0.2, 0.8, 0.2], [0.2, 0.5, 1], [0.6, 0.2, 0.8]]
    arch_ball_xs = [-4, -2, 0, 2, 4]
    for k, bx_pos in enumerate(arch_ball_xs):
        ball_name = f"ArchBall{k+1}"
        plaza_life[ball_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Shape": "Ball",
                "Position": [bx_pos, 13.5, 30],
                "Size": [2, 2, 2],
                "Color": arch_ball_colors[k]
            }
        }
        added_count += 1

    # Trees on four plaza corners (-44, 44), (44, 44), (-44, -44), (44, -44)
    tree_coords = [(-44, 44), (44, 44), (-44, -44), (44, -44)]
    for idx, (tx, tz) in enumerate(tree_coords):
        trunk_name = f"PlazaTree{idx+1}"
        leaves_name = f"PlazaLeaves{idx+1}"
        
        plaza_life[trunk_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [tx, 4, tz],
                "Size": [1.5, 6, 1.5],
                "Color": [0.55, 0.35, 0.15]
            }
        }
        added_count += 1

        plaza_life[leaves_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Shape": "Ball",
                "Position": [tx, 8.5, tz],
                "Size": [6, 5, 6],
                "Color": [0.2, 0.7, 0.2]
            }
        }
        added_count += 1

    # Balloons on poles near fountain at (-12, 12), (12, 12), (-12, -12), (12, -12)
    balloon_coords = [(-12, 12), (12, 12), (-12, -12), (12, -12)]
    balloon_colors = [[1, 0.2, 0.2], [0.2, 0.5, 1], [1, 0.9, 0], [1, 0.5, 0.8]]
    for idx, (bx, bz) in enumerate(balloon_coords):
        pole_name = f"BalloonPole{idx+1}"
        balloon_name = f"Balloon{idx+1}"
        
        plaza_life[pole_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [bx, 3.5, bz],
                "Size": [0.5, 5, 0.5],
                "Color": [0.7, 0.7, 0.7]
            }
        }
        added_count += 1

        plaza_life[balloon_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Shape": "Ball",
                "Position": [bx, 7, bz],
                "Size": [3, 3.5, 3],
                "Color": balloon_colors[idx]
            }
        }
        added_count += 1

    # Benches by fountain at (-8, -6) and (8, -6)
    bench_coords = [(-8, -6), (8, -6)]
    for idx, (bx, bz) in enumerate(bench_coords):
        seat_name = f"BenchSeat{idx+1}"
        back_name = f"BenchBack{idx+1}"
        
        plaza_life[seat_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [bx, 1.8, bz],
                "Size": [4, 0.5, 2],
                "Color": [0.55, 0.35, 0.15]
            }
        }
        added_count += 1

        plaza_life[back_name] = {
            "$className": "Part",
            "$properties": {
                "Anchored": True,
                "Position": [bx, 3, bz + 0.9],
                "Size": [4, 2, 0.5],
                "Color": [0.55, 0.35, 0.15]
            }
        }
        added_count += 1

    workspace["PlazaLife"] = {
        "$className": "Folder",
        **plaza_life
    }

    # Save project file back in compact form using format_json_compact
    output_content = format_json_compact(data, indent=2)
    with open(project_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"Successfully added PlazaLife with {added_count} items and updated Rides/DespawnGate.")

if __name__ == "__main__":
    main()
