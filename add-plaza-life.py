import json
import math
import os
import sys

def round1(v):
    return round(v, 1)

def round4(v):
    return round(v, 4)

def vec3(x, y, z):
    return [round1(x), round1(y), round1(z)]

def size3(x, y, z):
    return [round1(x), round1(y), round1(z)]

def color3(r, g, b):
    return [round(r, 3), round(g, 3), round(b, 3)]

def make_part(class_name, pos, size, color, anchored=True, shape=None, cframe=None):
    props = {
        "Anchored": anchored,
        "Position": vec3(*pos),
        "Size": size3(*size),
        "Color": color3(*color)
    }
    if shape:
        props["Shape"] = shape
    if cframe:
        props["CFrame"] = [round1(cframe[0]), round1(cframe[1]), round1(cframe[2])] + [round4(x) for x in cframe[3:]]
    node = {
        "$className": class_name,
        "$properties": props
    }
    return node

def main():
    project_path = "default.project.json"
    if not os.path.exists(project_path):
        print(f"Error: {project_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(project_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Find Workspace and Rides folder
    tree = data.get("tree", {})
    workspace = tree.get("Workspace", {})
    if not workspace:
        print("Error: Workspace not found in project tree.", file=sys.stderr)
        sys.exit(1)

    # Check top-level folder "PlazaLife" under Workspace
    if "PlazaLife" in workspace:
        print("Error: PlazaLife folder already exists in Workspace.", file=sys.stderr)
        sys.exit(1)

    rides_folder = workspace.get("Rides")
    if not rides_folder:
        print("Error: Rides folder not found in Workspace.", file=sys.stderr)
        sys.exit(1)

    # 1. Move Ferris Wheel and Carousel
    # Ferris wheel moves by +12 in x and +8 in z
    # FerrisWheel model parts: TowerL, TowerR, Hub, Spoke1 to Spoke4, Rim1 to Rim8
    ferris_wheel = rides_folder.get("FerrisWheel")
    if ferris_wheel:
        fw_children = {k: v for k, v in ferris_wheel.items() if not k.startswith("$")}
        for name, child in fw_children.items():
            if "$properties" in child:
                props = child["$properties"]
                if "Position" in props:
                    p = props["Position"]
                    props["Position"] = [round1(p[0] + 12), round1(p[1]), round1(p[2] + 8)]
                if "CFrame" in props:
                    cf = props["CFrame"]
                    cf[0] = round1(cf[0] + 12)
                    cf[2] = round1(cf[2] + 8)

    # Cabin1 to Cabin8 are direct children of Rides folder
    for i in range(1, 9):
        cabin_name = f"Cabin{i}"
        cabin = rides_folder.get(cabin_name)
        if cabin and "$properties" in cabin:
            props = cabin["$properties"]
            if "Position" in props:
                p = props["Position"]
                props["Position"] = [round1(p[0] + 12), round1(p[1]), round1(p[2] + 8)]
            if "CFrame" in props:
                cf = props["CFrame"]
                cf[0] = round1(cf[0] + 12)
                cf[2] = round1(cf[2] + 8)

    # Carousel moves by -17 in x and +8 in z
    # Carousel model parts: Platform, Pole, Roof, Horse1 to Horse4
    carousel = rides_folder.get("Carousel")
    if carousel:
        c_children = {k: v for k, v in carousel.items() if not k.startswith("$")}
        for name, child in c_children.items():
            if "$properties" in child:
                props = child["$properties"]
                if "Position" in props:
                    p = props["Position"]
                    props["Position"] = [round1(p[0] - 17), round1(p[1]), round1(p[2] + 8)]
                if "CFrame" in props:
                    cf = props["CFrame"]
                    cf[0] = round1(cf[0] - 17)
                    cf[2] = round1(cf[2] + 8)

    # 2. Add sixteen roller coaster rails CoasterRail1 to CoasterRail16 to Rides folder
    # Pad formula: pad i (i from 0 to 15) at angle i times 22.5 degrees
    pads = []
    for i in range(16):
        angle_deg = i * 22.5
        angle_rad = math.radians(angle_deg)
        x = -110 + 25 * math.cos(angle_rad)
        z = -30 + 40 * math.sin(angle_rad)
        y = 5 + 3 * math.sin(2 * angle_rad)
        pads.append((round1(x), round1(y), round1(z)))

    gold_color = (1, 0.8, 0.2)
    for i in range(16):
        rail_num = i + 1
        pad_a = pads[i]
        pad_b = pads[(i + 1) % 16]

        ax, ay, az = pad_a
        bx, by, bz = pad_b

        dx = bx - ax
        dy = by - ay
        dz = bz - az

        length = math.sqrt(dx*dx + dy*dy + dz*dz)

        # Direction vector (bx-ax, by-ay, bz-az) normalized for Z axis
        if length > 0:
            z_axis = (dx / length, dy / length, dz / length)
        else:
            z_axis = (0, 0, 1)

        # Up vector = (0, 1, 0)
        # X axis = normalize(cross((0, 1, 0), z_axis))
        ux, uy, uz = 0, 1, 0
        zx, zy, zz = z_axis
        # cross(u, z) = (uy*zz - uz*zy, uz*zx - ux*zz, ux*zy - uy*zx) = (0*zz - 1*zy, 1*zx - 0*zz, 0*zy - 0*zx) = (-zy, zx, 0)
        cx = -zy
        cy = zx
        cz = 0
        c_len = math.sqrt(cx*cx + cy*cy + cz*cz)
        if c_len > 0:
            x_axis = (cx / c_len, cy / c_len, cz / c_len)
        else:
            x_axis = (1, 0, 0)

        # Y axis = cross(z_axis, x_axis)
        # cross(z, x) = (zy*xx - zz*xy, zz*xx - zx*xz ...)
        xx, xy, xz = x_axis
        yx = zy * xz - zz * xy
        yy = zz * xx - zx * xz
        yz = zx * xy - zy * xx
        y_len = math.sqrt(yx*yx + yy*yy + yz*yz)
        if y_len > 0:
            y_axis = (yx / y_len, yy / y_len, yz / y_len)
        else:
            y_axis = (0, 1, 0)

        midpoint = (ax + dx / 2.0, ay + dy / 2.0, az + dz / 2.0)

        cframe = [
            midpoint[0], midpoint[1], midpoint[2],
            x_axis[0], x_axis[1], x_axis[2],
            y_axis[0], y_axis[1], y_axis[2],
            z_axis[0], z_axis[1], z_axis[2]
        ]

        rail_node = make_part(
            "Part",
            pos=(0, 0, 0),
            size=(0.6, 0.3, length),
            color=gold_color,
            anchored=True,
            cframe=cframe
        )
        rides_folder[f"CoasterRail{rail_num}"] = rail_node

    # 3. Lower DespawnGate in Workspace
    despawn_gate = workspace.get("DespawnGate")
    if despawn_gate and "$properties" in despawn_gate:
        despawn_gate["$properties"]["Position"] = [0.0, 2.25, -10.0]
        despawn_gate["$properties"]["Size"] = [14.0, 2.5, 1.5]
        despawn_gate["$properties"]["Color"] = [0.2, 0.2, 0.2]

    # 4. Create PlazaLife Folder under Workspace
    plaza_life = {}

    rainbow_colors = [
        (1, 0.2, 0.2),    # red
        (1, 0.5, 0),      # orange
        (1, 0.9, 0),      # yellow
        (0.2, 0.8, 0.2),  # green
        (0.2, 0.5, 1),    # blue
        (0.6, 0.2, 0.8),  # purple
        (1, 0.5, 0.8),    # pink
        (0.2, 0.8, 1)     # cyan
    ]

    added_count = 0

    # Rainbow path: PathTile1 to PathTile12 at (0, 1.1, z) where z goes 30, 26, 22, 18, 14, 10, 6, 2, -2, -6, -10, -14
    z_vals = [30, 26, 22, 18, 14, 10, 6, 2, -2, -6, -10, -14]
    for j, z in enumerate(z_vals):
        color = rainbow_colors[j % 8]
        plaza_life[f"PathTile{j+1}"] = make_part("Part", (0, 1.1, z), (6, 0.2, 4), color)
        added_count += 1

    # Cross path east-west: CrossTile1 to CrossTile15 at (x, 1.1, 0) where x goes -42 to 42 step 6
    x_vals = [-42, -36, -30, -24, -18, -12, -6, 0, 6, 12, 18, 24, 30, 36, 42]
    for j, x in enumerate(x_vals):
        color = rainbow_colors[(j + 3) % 8]
        plaza_life[f"CrossTile{j+1}"] = make_part("Part", (x, 1.1, 0), (5, 0.2, 5), color)
        added_count += 1

    # Scattered pastel tiles
    pastel_tiles_data = [
        ("PlazaTile1", -30, 20, (1, 0.7, 0.7)),
        ("PlazaTile2", 30, 20, (0.7, 0.9, 1)),
        ("PlazaTile3", -30, -20, (0.7, 1, 0.7)),
        ("PlazaTile4", 30, -20, (1, 0.9, 0.6)),
        ("PlazaTile5", -15, 25, (0.9, 0.7, 1)),
        ("PlazaTile6", 15, -25, (0.7, 1, 1)),
        ("PlazaTile7", -40, 35, (1, 0.8, 0.9)),
        ("PlazaTile8", 40, 35, (0.8, 1, 0.8)),
        ("PlazaTile9", -20, -35, (1, 1, 0.7)),
        ("PlazaTile10", 20, -35, (0.9, 0.8, 1)),
        ("PlazaTile11", 0, 18, (0.7, 0.8, 1)),
        ("PlazaTile12", -35, 5, (1, 0.7, 0.5)),
    ]
    for name, x, z, color in pastel_tiles_data:
        plaza_life[name] = make_part("Part", (x, 1.1, z), (5, 0.2, 5), color)
        added_count += 1

    # Welcome arch just north of spawn at z = 30
    plaza_life["ArchPillarL"] = make_part("Part", (-5, 6, 30), (2, 10, 2), (1, 0.2, 0.2))
    added_count += 1
    plaza_life["ArchPillarR"] = make_part("Part", (5, 6, 30), (2, 10, 2), (0.2, 0.5, 1))
    added_count += 1
    plaza_life["ArchBeam"] = make_part("Part", (0, 11.5, 30), (14, 2, 2), (1, 0.9, 0))
    added_count += 1
    plaza_life["ArchSign"] = make_part("Part", (0, 9, 30), (9, 3, 0.5), (1, 0.5, 0.8))
    added_count += 1

    ball_colors = [(1, 0.2, 0.2), (1, 0.9, 0), (0.2, 0.8, 0.2), (0.2, 0.5, 1), (0.6, 0.2, 0.8)]
    ball_xs = [-4, -2, 0, 2, 4]
    for idx, (bx, bcol) in enumerate(zip(ball_xs, ball_colors), start=1):
        plaza_life[f"ArchBall{idx}"] = make_part("Part", (bx, 13.5, 30), (2, 2, 2), bcol, shape="Ball")
        added_count += 1

    # Trees on four plaza corners (-44, 44), (44, 44), (-44, -44), (44, -44)
    corner_coords = [(-44, 44), (44, 44), (-44, -44), (44, -44)]
    brown_color = (0.55, 0.35, 0.15)
    leaves_color = (0.2, 0.7, 0.2)
    for idx, (tx, tz) in enumerate(corner_coords, start=1):
        plaza_life[f"PlazaTree{idx}"] = make_part("Part", (tx, 4, tz), (1.5, 6, 1.5), brown_color)
        added_count += 1
        plaza_life[f"PlazaLeaves{idx}"] = make_part("Part", (tx, 8.5, tz), (6, 5, 6), leaves_color, shape="Ball")
        added_count += 1

    # Balloons on poles near fountain at (-12, 12), (12, 12), (-12, -12), (12, -12)
    balloon_coords = [(-12, 12), (12, 12), (-12, -12), (12, -12)]
    pole_color = (0.7, 0.7, 0.7)
    balloon_colors_list = [(1, 0.2, 0.2), (0.2, 0.5, 1), (1, 0.9, 0), (1, 0.5, 0.8)]
    for idx, ((bx, bz), bcol) in enumerate(zip(balloon_coords, balloon_colors_list), start=1):
        plaza_life[f"BalloonPole{idx}"] = make_part("Part", (bx, 3.5, bz), (0.5, 5, 0.5), pole_color)
        added_count += 1
        plaza_life[f"Balloon{idx}"] = make_part("Part", (bx, 7, bz), (3, 3.5, 3), bcol, shape="Ball")
        added_count += 1

    # Benches by fountain at (-8, -6) and (8, -6)
    bench_coords = [(-8, -6), (8, -6)]
    for idx, (bx, bz) in enumerate(bench_coords, start=1):
        plaza_life[f"BenchSeat{idx}"] = make_part("Part", (bx, 1.8, bz), (4, 0.5, 2), brown_color)
        added_count += 1
        plaza_life[f"BenchBack{idx}"] = make_part("Part", (bx, 3, bz + 0.9), (4, 2, 0.5), brown_color)
        added_count += 1

    # Wrap PlazaLife folder structure
    plaza_node = {"$className": "Folder"}
    plaza_node.update(plaza_life)
    workspace["PlazaLife"] = plaza_node

    # Save project file with compact custom writer
    class CompactJSONEncoder:
        @staticmethod
        def encode(obj, indent_level=0):
            ind = "  " * indent_level
            if isinstance(obj, dict):
                if not obj:
                    return "{}"
                items = []
                for k, v in obj.items():
                    items.append(f'{ind}  "{k}": {CompactJSONEncoder.encode(v, indent_level + 1)}')
                return "{\n" + ",\n".join(items) + f"\n{ind}}}"
            elif isinstance(obj, list):
                if not obj:
                    return "[]"
                # Check if list contains only numbers/scalars
                if all(isinstance(x, (int, float, bool, str)) for x in obj):
                    # Format nicely on single line
                    formatted = []
                    for x in obj:
                        if isinstance(x, float):
                            formatted.append(str(x))
                        elif isinstance(x, int):
                            formatted.append(str(x))
                        elif isinstance(x, bool):
                            formatted.append("true" if x else "false")
                        else:
                            formatted.append(json.dumps(x))
                    return "[" + ", ".join(formatted) + "]"
                else:
                    items = []
                    for item in obj:
                        items.append(f'{ind}  {CompactJSONEncoder.encode(item, indent_level + 1)}')
                    return "[\n" + ",\n".join(items) + f"\n{ind}]"
            elif isinstance(obj, str):
                return json.dumps(obj)
            elif isinstance(obj, bool):
                return "true" if obj else "false"
            elif obj is None:
                return "null"
            else:
                return str(obj)

    output_str = CompactJSONEncoder.encode(data, 0) + "\n"

    with open(project_path, "w", encoding="utf-8") as f:
        f.write(output_str)

    print(f"Success! Added {added_count} children to PlazaLife and updated project.")

if __name__ == "__main__":
    main()
    print(f"Added {16} rails to Rides.")
