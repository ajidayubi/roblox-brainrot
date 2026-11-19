import json
import math
import os

PROJECT_PATH = "default.project.json"
RIDES_PATH = "src/server/Rides.luau"

def rot_z_matrix(theta_deg):
    theta = math.radians(theta_deg)
    c = round(math.cos(theta), 4)
    s = round(math.sin(theta), 4)
    return [
        c, -s, 0.0,
        s, c, 0.0,
        0.0, 0.0, 1.0
    ]

def make_part(pos, size, color, anchored=True, shape=None, cframe=None):
    props = {
        "Anchored": anchored,
        "Position": [round(p, 1) for p in pos],
        "Size": [round(s, 1) for s in size],
        "Color": [round(c, 4) for c in color]
    }
    if shape:
        props["Shape"] = shape
    if cframe:
        props["CFrame"] = [round(x, 4) for x in cframe]
    return {
        "$className": "Part",
        "$properties": props
    }

def make_model(children):
    model = {
        "$className": "Model"
    }
    for k, v in children.items():
        model[k] = v
    return model

def main():
    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        proj = json.load(f)

    workspace = proj["tree"]["Workspace"]
    rides = workspace["Rides"]
    bases = workspace["Bases"]

    rainbow = [
        (1, 0.2, 0.2),
        (1, 0.5, 0),
        (1, 0.9, 0),
        (0.2, 0.8, 0.2),
        (0.2, 0.5, 1),
        (0.6, 0.2, 0.8),
        (1, 0.5, 0.8),
        (0.2, 0.8, 1)
    ]

    # STEP 1: Ferris Wheel rebuilt bigger at centre (58, 20, -45), radius 15
    ferris_children = {}
    ferris_children["Hub"] = make_part([58, 20, -45], [3, 3, 3], (1, 0.2, 0.2))
    
    angles = [0, 45, 90, 135, 180, 225, 270, 315]

    for i in range(4):
        ang = angles[i]
        mat = rot_z_matrix(ang)
        cf = [58.0, 20.0, -45.0] + mat
        ferris_children[f"Spoke{i+1}"] = make_part(
            [58, 20, -45], [30, 1, 1], (1, 0.8, 0.2), cframe=cf
        )

    for i in range(8):
        ang = angles[i]
        rx = 58 + 15 * math.cos(math.radians(ang))
        ry = 20 + 15 * math.sin(math.radians(ang))
        rz = -45
        mat = rot_z_matrix(ang + 90)
        cf = [round(rx, 1), round(ry, 1), round(rz, 1)] + mat
        ferris_children[f"Rim{i+1}"] = make_part(
            [rx, ry, rz], [11, 1, 1], rainbow[i], cframe=cf
        )

    ferris_children["TowerL"] = make_part([52, 10, -45], [2, 20, 2], (0.5, 0.5, 0.5))
    ferris_children["TowerR"] = make_part([64, 10, -45], [2, 20, 2], (0.5, 0.5, 0.5))

    rides["FerrisWheel"] = make_model(ferris_children)

    cabin_points = [
        (0, (73, 20, -45)),
        (45, (68.6, 30.6, -45)),
        (90, (58, 35, -45)),
        (135, (47.4, 30.6, -45)),
        (180, (43, 20, -45)),
        (225, (47.4, 9.4, -45)),
        (270, (58, 5, -45)),
        (315, (68.6, 9.4, -45))
    ]

    for k in list(rides.keys()):
        if k.startswith("Cabin"):
            del rides[k]

    for i, (ang, pos) in enumerate(cabin_points):
        rides[f"Cabin{i+1}"] = make_part(pos, [4, 4, 4], rainbow[i])

    # STEP 2: Carousel
    if "Carousel" in rides:
        carousel = rides["Carousel"]
        if "Horse1" in carousel:
            carousel["Horse1"]["$properties"]["Color"] = [1, 0.5, 0.8]
        if "Horse2" in carousel:
            carousel["Horse2"]["$properties"]["Color"] = [0.2, 0.5, 1]
        if "Horse3" in carousel:
            carousel["Horse3"]["$properties"]["Color"] = [1, 0.9, 0]
        if "Horse4" in carousel:
            carousel["Horse4"]["$properties"]["Color"] = [0.2, 0.8, 0.2]
        
        carousel["RoofTop"] = make_part([-58, 11.5, -45], [4, 2, 4], (1, 0.8, 0.2), shape="Ball")

    # STEP 3: Market stalls
    goods_colors = [
        (1, 0.2, 0.2),
        (1, 0.9, 0),
        (0.2, 0.8, 0.2),
        (0.2, 0.5, 1),
        (1, 0.5, 0.8)
    ]

    for k, base in list(bases.items()):
        if k.startswith("$") or not isinstance(base, dict):
            continue
        if "Pad" in base:
            pad_pos = base["Pad"]["$properties"]["Position"]
            cx, cz = pad_pos[0], pad_pos[2]
        else:
            continue

        base["Peak"] = make_part([cx, 7.5, cz], [12, 1.5, 12], (1, 1, 1))
        fz = -1 if cz < 0 else 1
        x_offsets = [-6, -3, 0, 3, 6]
        for idx, xoff in enumerate(x_offsets):
            gx = cx + xoff
            gy = 3.75
            gz = cz + fz * 9
            base[f"Goods{idx+1}"] = make_part([gx, gy, gz], [2, 2, 2], goods_colors[idx])

    def write_compact_json(obj, out_path):
        def is_num_list(v):
            return isinstance(v, list) and len(v) > 0 and all(isinstance(x, (int, float)) for x in v)
        def enc(o, level):
            sp = "  " * level
            nsp = "  " * (level + 1)
            if isinstance(o, dict):
                if not o:
                    return "{}"
                parts = []
                for k, v in o.items():
                    parts.append(nsp + json.dumps(k) + ": " + enc(v, level + 1))
                return "{\n" + ",\n".join(parts) + "\n" + sp + "}"
            if is_num_list(o):
                return "[" + ", ".join(json.dumps(x) for x in o) + "]"
            if isinstance(o, list):
                if not o:
                    return "[]"
                parts = [nsp + enc(x, level + 1) for x in o]
                return "[\n" + ",\n".join(parts) + "\n" + sp + "]"
            return json.dumps(o)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(enc(obj, 0) + "\n")
    write_compact_json(proj, PROJECT_PATH)
    print(f"Successfully updated {PROJECT_PATH}")

    # STEP 4: Animator radius in Rides.luau
    if os.path.exists(RIDES_PATH):
        with open(RIDES_PATH, "r", encoding="utf-8") as f:
            rides_code = f.read()
        old_target = "Vector3.new(12 * math.cos(a), 12 * math.sin(a), 0)"
        new_target = "Vector3.new(15 * math.cos(a), 15 * math.sin(a), 0)"
        if old_target in rides_code:
            rides_code = rides_code.replace(old_target, new_target)
        elif "local radius = 12.0" in rides_code:
            rides_code = rides_code.replace("local radius = 12.0", "local radius = 15.0")
            rides_code = rides_code.replace("radius * math.cos(angle)", "15 * math.cos(angle)")
            rides_code = rides_code.replace("radius * math.sin(angle)", "15 * math.sin(angle)")
        with open(RIDES_PATH, "w", encoding="utf-8") as f:
            f.write(rides_code)
        print(f"Successfully updated animator radius in {RIDES_PATH}")
    else:
        print(f"Warning: {RIDES_PATH} not found")

if __name__ == "__main__":
    main()
