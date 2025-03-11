import re

def parse_esmiles(esmiles):
    """Parses eSMILES and extracts components for generating an NWChem input deck."""
    
    # ✅ Extract data using regex
    geometry_match = re.search(r"(xyzdata|fractionaldata)\{(.*?)\}", esmiles)
    unitcell_match = re.search(r"unitcell\{(.*?)\}", esmiles)
    theory_match = re.search(r"theory\{(.*?)\}", esmiles)
    xc_match = re.search(r"xc\{(.*?)\}", esmiles)
    mult_match = re.search(r"mult\{(.*?)\}", esmiles)
    basis_match = re.search(r"basis\{(.*?)\}", esmiles)
    pspspin_up_match = re.search(r"pspspin\{up d (.*?)\}", esmiles)
    pspspin_down_match = re.search(r"pspspin\{down d (.*?)\}", esmiles)
    calc_match = re.search(r"calculation_type\{(.*?)\}", esmiles)

    # ✅ Extract geometry
    geometry_type = "cartesian" if "xyzdata" in esmiles else "fractional"
    geometry_lines = geometry_match.group(2).split("|") if geometry_match else []
    unitcell_lines = unitcell_match.group(1).split("|") if unitcell_match else []

    # ✅ Extract theory settings
    theory = theory_match.group(1) if theory_match else "pspw"  # Default to PSPW
    xc = xc_match.group(1) if xc_match else "pbe96"
    mult = mult_match.group(1) if mult_match else "1"
    basis = basis_match.group(1) if basis_match else "50.0"

    # ✅ Extract pspspin settings
    pspspin_up = f"pspspin up d {pspspin_up_match.group(1)}" if pspspin_up_match else ""
    pspspin_down = f"pspspin down d {pspspin_down_match.group(1)}" if pspspin_down_match else ""

    # ✅ Extract calculations and intermediate set blocks (REVERSED ORDER)
    calc_steps = []
    set_blocks = []
    
    if calc_match:
        calc_items = calc_match.group(1).split("-")
        for c in calc_items:
            if c.startswith("set{"):
                set_blocks.append(c[4:-1])  # Extract set command content
            else:
                calc_steps.append(c)

    return {
        "geometry_type": geometry_type,
        "geometry_lines": geometry_lines,
        "unitcell_lines": unitcell_lines,
        "theory": theory,
        "xc": xc,
        "mult": mult,
        "basis": basis,
        "pspspin_up": pspspin_up,
        "pspspin_down": pspspin_down,
        "calc_steps": calc_steps,  # Ordered in REVERSE JSON sequence
        "set_blocks": set_blocks
    }

def generate_nwinput(parsed_data):
    """Generates an NWChem input file from parsed eSMILES data."""
    
    nwinput = []

    # ✅ Step 1: Write charge and geometry block
    nwinput.append("charge 0\n")
    nwinput.append("geometry noautoz nocenter noautosym")

    if parsed_data["geometry_type"] == "fractional":
        nwinput.append("system crystal")
        nwinput.append("   lattice_vectors")
        for line in parsed_data["unitcell_lines"]:
            nwinput.append(f"     {line.strip()}")
        nwinput.append("end")

    for line in parsed_data["geometry_lines"]:
        nwinput.append(f"{line.strip()}")

    nwinput.append("end\n")

    # ✅ Step 2: Write NWPW block (Initial Setup)
    nwinput.append("nwpw")
    nwinput.append(f"  xc {parsed_data['xc']}")
    nwinput.append(f"  mult {parsed_data['mult']}")
    nwinput.append(f"  cutoff {parsed_data['basis']}")
    nwinput.append("  ### pseudopotential block begin ###")
    nwinput.append("  ### pseudopotential block end   ###")

    if parsed_data["pspspin_up"]:
        nwinput.append(f"  {parsed_data['pspspin_up']}")
    if parsed_data["pspspin_down"]:
        nwinput.append(f"  {parsed_data['pspspin_down']}")

    nwinput.append("end\n")

    # ✅ Step 3: Initial `set` blocks (before first task)
    nwinput.append("set nwpw:kbpp_ray    .true.")
    nwinput.append("set nwpw:kbpp_filter .true.")
    nwinput.append("set nwpw:cif_filename H63O128Fe63Ru1")

    # ✅ Step 4: Insert first task (from calculation_type{}, ordered from left to right)
    if parsed_data["calc_steps"]:
        first_task = parsed_data["calc_steps"].pop(0)  # First calculation step
        nwinput.append(f"task {parsed_data['theory']} {first_task}")

    # ✅ Step 5: Handle subsequent tasks with updates
    for i, calc in enumerate(parsed_data["calc_steps"]):
        if i == 0:
            # Insert `nwpw pspspin off` block before the second task
            nwinput.append("\nnwpw")
            nwinput.append("pspspin off")
            nwinput.append("end\n")

        if i < len(parsed_data["set_blocks"]):
            # Insert the corresponding set block before the next task
            set_command = parsed_data["set_blocks"][i]
            nwinput.append(f"set {set_command}")

        nwinput.append(f"task {parsed_data['theory']} {calc}")

    # ✅ Final set block after all calculations
    nwinput.append("set nwpw:kbpp_ray .false.\n")

    return "\n".join(nwinput)

# ✅ Main function
def esmiles_to_nwinput(esmiles, output_file="generated.nw"):
    """Converts eSMILES to an NWChem input file and saves it."""
    
    parsed_data = parse_esmiles(esmiles)
    nwinput_content = generate_nwinput(parsed_data)

    with open(output_file, "w") as f:
        f.write(nwinput_content)

    print(f"NWChem input deck generated: {output_file}")

# ✅ Example Run
# ✅ Example Run
esmiles_file = "esmiles.inp"
with open(esmiles_file,'r') as ff:
   esmiles_example = ff.read()


esmiles_to_nwinput(esmiles_example, "output2.nw")

