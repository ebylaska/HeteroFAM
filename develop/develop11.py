import re

def clean_input(nwinput_str):
    """Removes comments and empty lines from the input file."""
    return "\n".join(line.split("#")[0].strip() for line in nwinput_str.splitlines() if line.strip())

def parse_geometry(nwinput_str):
    """Extracts atomic coordinates and unit cell information from the geometry block."""
    if "geometry" not in nwinput_str:
        return ""

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
        if "lattice_vectors" in lattice_blk:
            geometry = "fractionaldata{" + " | ".join(xyz_data) + "}"
        else:
            geometry = "xyzdata{" + " | ".join(xyz_data) + "}"

        lattice_lines = [line.strip() for line in lattice_blk.split("\n") if line.strip()]
        lattice = " | ".join(lattice_lines[1:])  # Skip 'lattice_vectors' line
        geometry += " unitcell{" + lattice + "}"
    else:
        geometry = "xyzdata{" + " | ".join(xyz_data) + "}"

    return geometry




def parse_nwpw_block(nwinput_str):
    """Parses the `nwpw` block for xc, mult, cutoff, pspspin, uterm, and dplot values."""
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

    # Extract pspspin up/down
    pspspin_up = re.findall(r"pspspin\s+up\s+d\s+(-?\d+\.?\d*)\s+([\d\s:]+)", nwpw_block, re.IGNORECASE)
    pspspin_down = re.findall(r"pspspin\s+down\s+d\s+(-?\d+\.?\d*)\s+([\d\s:]+)", nwpw_block, re.IGNORECASE)

    if pspspin_up:
        spin_value, indices = pspspin_up[0]
        output.append(f"pspspin{{up d {spin_value} {indices.strip()}}}")

    if pspspin_down:
        spin_value, indices = pspspin_down[0]
        output.append(f"pspspin{{down d {spin_value} {indices.strip()}}}")

    # ✅ Extract `uterm` values
    uterms = re.findall(r"uterm d (.*?)\n", nwpw_block, re.IGNORECASE)
    for uterm in uterms:
        output.append(f"uterm{{d {uterm.strip()}}}")

    # ✅ Extract `dplot` values
    dplot_match = re.search(r"dplot(.*?)end", nwpw_block, re.DOTALL | re.IGNORECASE)
    if dplot_match:
        dplot_block = dplot_match.group(1).strip()
        densities = re.findall(r"density\s+(\w+)\s+([\w\.]+)", dplot_block, re.IGNORECASE)
        dplot_entries = [f"{density} {file}" for density, file in densities]
        if dplot_entries:
            output.append(f"dplot{{density{{{' | '.join(dplot_entries)}}}}}")

    return " ".join(output)

def parse_calculation(nwinput_str):
    """Parses task commands, tracks set commands, and includes pspspin off when present."""
    tasks = nwinput_str.split("task")
    calculations = []
    set_commands = []
    include_pspspin_off = False

    # ✅ Step 1: Check for "nwpw pspspin off end" and flag it
    nwpw_blocks = nwinput_str.split("nwpw")
    for block in nwpw_blocks[1:]:  # Ignore first split part before the first `nwpw`
        if "pspspin off" in block and "end" in block:
            include_pspspin_off = True

    # ✅ Step 2: Process tasks in REVERSE JSON ORDER
    for task in reversed(tasks[1:]):  # Skip the first split part before 'task'
        lines = task.strip().split("\n")
        first_line = lines[0].strip()
        calc_type = first_line.replace("ignore", "").strip()

        # Extract `set` commands before second and later tasks
        for line in lines:
            if line.startswith("set "):
                set_commands.append(f"set{{{line[4:].strip()}}}")

        if calc_type:
            calculations.append(calc_type)

    # ✅ Step 3: Insert `pspspin off` correctly
    if include_pspspin_off:
        calculations.insert(1, "pspspin{off}")

    # ✅ Step 4: Append `set` commands at the correct places
    calculations = set_commands + calculations  # Set commands first, then tasks

    return f"calculation_type{{{'-'.join(calculations)}}}" if calculations else "calculation_type{}"

def parse_theory(nwinput_str):
    """Determines the theory used (pspw or band). Default to pspw for NWPW calculations."""
    if "nwpw" in nwinput_str.lower():
        return "theory{pspw}"
    return "theory{band}"

def parse_nw_file_to_esmiles(nwinput_str):
    """Reads and parses an NWChem input string to eSMILES."""
    nwinput_str = clean_input(nwinput_str)
    mygeom = parse_geometry(nwinput_str)
    nwpw_settings = parse_nwpw_block(nwinput_str)
    calculations = parse_calculation(nwinput_str)
    theory = parse_theory(nwinput_str)

    esmiles = f"{mygeom} {nwpw_settings} {theory} {calculations}"
    return esmiles

# ✅ Example Run
nwinput_example = """
charge 0

geometry noautoz nocenter noautosym
system crystal
   lattice_vectors
     10.317827 -5.957000 0.000000
     0.000000 11.914000 0.000000
     0.000000 0.000000 18.077000
end

Fe 0.413751 -0.401694 -0.424434
end

nwpw
  xc pbe96
  mult 2
  cutoff 50.0
  pspspin up d -1.00 25 39 54 9
  pspspin down d -1.00 8 40 55 4
  uterm d 0.14634 0.036749 1:60 62:64
  uterm d 0.036749 0.0018375 61

  dplot
    density diff diff.cube
    density alpha alpha.cube
    density beta beta.cube
    density total total.cube
  end
end

task pspw energy ignore
nwpw
  pspspin off
end
set nwpw:kbpp_ray .false.
task pspw optimize
task pspw pspw_dplot
"""

esmiles_output = parse_nw_file_to_esmiles(nwinput_example)
print("esmiles =", esmiles_output)

