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

    # ✅ Extract calculations
    calc_lines = calc_match.group(1).split("-") if calc_match else []

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
        "calc_lines": calc_lines
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

    # ✅ Step 2: Write NWPW block
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

    # ✅ Step 3: Set commands
    nwinput.append("set nwpw:kbpp_ray    .true.")
    nwinput.append("set nwpw:kbpp_filter .true.")
    nwinput.append("set nwpw:cif_filename H63O128Fe63Ru1")

    # ✅ Step 4: Handle `pspspin off`
    nwinput.append("nwpw")
    nwinput.append("pspspin off")
    nwinput.append("end\n")
    nwinput.append("set nwpw:kbpp_ray .false.\n")

    # ✅ Step 5: Write calculation tasks **AFTER** `nwpw`
    for calc in parsed_data["calc_lines"]:
        if calc.startswith("set{"):
            nwinput.append(f"set {calc[4:-1]}")
        else:
            nwinput.append(f"task {parsed_data['theory']} {calc}")

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
esmiles_file = "esmiles.inp"
with open(esmiles_file,'r') as ff:
   esmiles_example = ff.read()

esmiles_to_nwinput(esmiles_example, "output.nw")

