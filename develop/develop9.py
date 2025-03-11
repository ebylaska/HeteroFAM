import re

# ✅ Step 1: Clean input - Remove everything after # in each line
def clean_input(nwinput_str):
    return "\n".join(line.split("#")[0].strip() for line in nwinput_str.splitlines() if line.strip())

# ✅ Step 2: Parse the 'geometry' block correctly
def parse_geometry(nwinput_str):
    """Extracts atomic coordinates and unit cell information from the geometry block."""
    if "geometry" not in nwinput_str:
        return ""

    # Extract geometry block
    geometry_blk = nwinput_str.split("geometry", 1)[1]
    lattice_blk = ""

    if "system crystal" in geometry_blk:
        lattice_blk, geometry_blk = geometry_blk.split("end", 1)
    else:
        geometry_blk = geometry_blk.split("end", 1)[0]

    atom_lines = [line.strip() for line in geometry_blk.split("\n") if line.strip()]
    valid_atoms = [line.split() for line in atom_lines if len(line.split()) == 4]

    xyz_data = [f"{symb} {x} {y} {z}" for symb, x, y, z in valid_atoms]

    if lattice_blk:
        if "cartesian" in lattice_blk:
            geometry = "xyzdata{" + " | ".join(xyz_data) + "}"
        else:
            geometry = "fractionaldata{" + " | ".join(xyz_data) + "}"

        lattice_data = lattice_blk.split("system crystal", 1)[1].strip()
        lattice_lines = [line.strip() for line in lattice_data.split("\n") if line.strip()]
        lattice = " | ".join(lattice_lines)
        geometry += " unitcell{" + lattice + "}"
    else:
        geometry = "xyzdata{" + " | ".join(xyz_data) + "}"

    return geometry


def parse_theory(nwinput_str):
    """Determines the theory method used: 'pspw' (default for nwpw) or 'band'."""
    nwinput_str = clean_input(nwinput_str)
    
    if "task band" in nwinput_str:
        return "theory{band}"
    elif "nwpw" in nwinput_str:  # If 'nwpw' appears anywhere, default to 'pspw'
        return "theory{pspw}"
    
    return ""  # No theory if neither 'nwpw' nor 'task band' is found


# ✅ Step 3: Parse NWPW settings correctly
def parse_nwpw_block(nwinput_str):
    """Parses the 'nwpw' block while handling comments and ensuring pspspin parsing works."""
    nwinput_str = clean_input(nwinput_str)

    match = re.search(r"nwpw(.*?)end\s*\n", nwinput_str, re.DOTALL | re.IGNORECASE)
    if not match:
        return ""

    nwpw_block = match.group(1).strip()
    output = []

    # Extract key values
    patterns = {
        "xc": r"\bxc\s+(\S+)",
        "mult": r"\bmult\s+(\d+)",
        "cutoff": r"\bcutoff\s+([\d\.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, nwpw_block, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            output.append(f"{key}{{{value}}}" if key != "cutoff" else f"basis{{{value}}}")

    # ✅ Improved: Capture both `pspspin up` and `pspspin down` with multiple spaces handled
    pspspin_up = re.findall(r"pspspin\s+up\s+d\s+(-?\d+\.?\d*)\s+([\d\s]+)", nwpw_block, re.IGNORECASE)
    pspspin_down = re.findall(r"pspspin\s+down\s+d\s+(-?\d+\.?\d*)\s+([\d\s]+)", nwpw_block, re.IGNORECASE)

    if pspspin_up:
        spin_value, indices = pspspin_up[0]
        output.append(f"pspspin{{up d {spin_value} {indices.strip()}}}")

    if pspspin_down:
        spin_value, indices = pspspin_down[0]
        output.append(f"pspspin{{down d {spin_value} {indices.strip()}}}")

    return " ".join(output)


def parse_calculation(nwinput_str):
    """Parses task commands, tracks set commands, and includes pspspin off when present."""
    tasks = nwinput_str.split("task")
    calculations = []
    set_commands = []
    task_count = 0
    include_pspspin_off = False

    # ✅ Step 1: Check for "nwpw pspspin off end" and flag it
    nwpw_blocks = nwinput_str.split("nwpw")
    for block in nwpw_blocks[1:]:  # Ignore first split part before the first `nwpw`
        if "pspspin off" in block and "end" in block:
            include_pspspin_off = True

    # ✅ Step 2: Process tasks, preserving order and adding set commands
    for task in tasks[1:]:  # Skip the first split part before 'task'
        lines = task.strip().split("\n")
        first_line = lines[0].strip()
        calc_type = first_line.replace("ignore", "").replace("pspw", "").strip()

        # Extract `set` commands before second and later tasks
        for line in lines:
            if line.startswith("set "):
                set_commands.append(f"set{{{line[4:].strip()}}}")

        if calc_type:  # Only add if it's not empty
            if task_count > 0 and set_commands:
                calculations.append(" ".join(set_commands))
                set_commands.clear()  # Reset set commands for next task
            calculations.append(calc_type)
            task_count += 1

    # ✅ Step 3: Append any remaining set commands at the end
    if set_commands:
        calculations.append(" ".join(set_commands))

    # ✅ Step 4: Insert `pspspin off` correctly
    if include_pspspin_off:
        calculations.insert(1, "pspspin{off}")  # Place it after the first task

    return f"calculation_type{{{'-'.join(calculations)}}}" if calculations else "calculation_type{}"


# ✅ Step 5: Main processing function
def parse_nw_file_to_esmiles(file_path):
    """Reads and parses a .nw file."""
    with open(file_path, "r") as f:
        nwinput_str = f.read()
    nwinput_str = nwinput_str.split("============================== echo of input deck ==============================")[1]
    nwinput_str = nwinput_str.split("================================================================================")[0]

    nwinput_str = clean_input(nwinput_str)
    mygeom = parse_geometry(nwinput_str)
    theory = parse_theory(nwinput_str)
    nwpw_settings = parse_nwpw_block(nwinput_str)
    calculations = parse_calculation(nwinput_str)

    #print("nwpw_settings=", nwpw_settings)
    #print("calculations=", calculations)
    #print("mygeom=", mygeom)

    esmiles = f"{mygeom} {theory} {nwpw_settings} {calculations}"
    #print("esmiles=", esmiles)
    return esmiles

# ✅ Run Parser
#nwoutput = "test9.nw"
nwoutput = "H63O128Fe63Ru1.out00"

esmiles = parse_nw_file_to_esmiles(nwoutput)
print("esmiles=", esmiles)

