 
import re
 
def parse_geometry(nwinput_str):
   # find geometry block
   geometry_blk =  nwinput_str.split("geometry")[1]
   lattice_blk =  ""


   if "system crystal" in geometry_blk:
      lattice_blk = geometry_blk.split("end")[0]
      geometry_blk = geometry_blk.split("end")[1]
   else:
      geometry_blk = geometry_blk.split("end")[0]

   atom_lines = [line.strip() for line in geometry_blk.split("\n") if line.strip()]
   valid_atoms = [line.split() for line in atom_lines if len(line.split()) == 4]
   natoms = len(valid_atoms)

   xyz_data = []
   for ii, (symb, x, y, z) in enumerate(valid_atoms):
      atom_entry = f"{symb} {x} {y} {z}"
      xyz_data.append(atom_entry)


   if (len(lattice_blk)>0):
      if "cartesian" in lattice_blk:
         geometry = "xyzdata{" 
         geometry +=  " | ".join(xyz_data) 
         geometry += "}"
      else:
         geometry = "fractionaldata{" 
         geometry +=  " | ".join(xyz_data) 
         geometry += "}"

      lattice_data = lattice_blk.split("system crystal", 1)[1].strip()
      lattice_lines = [line.strip() for line in lattice_data.split("\n") if line.strip()]
      lattice = " | ".join(lattice_lines)

      geometry += " unitcell{" + lattice + "}"
   else:
      geometry = "xyzdata{" 
      geometry +=  " | ".join(xyz_data) 
      geometry += "}"

  
   return geometry

def parse_calculation(nwinput_str):
    tasks = nwinput_str.split("task")
    calculations = []

    for task in tasks[1:]:  # Skip the first split part before 'task'
        first_line = task.split("\n")[0].strip()
        calc_type = first_line.replace("ignore", "").replace("pspw", "").strip()

        if calc_type:  # Only add if it's not empty
            calculations.append(calc_type)

    return f"calculation_type{{{'-'.join(calculations)}}}" if calculations else "calculation_type{}"

def parse_initial_setup(nwinput_str):
    init_tasks = nwinput_str.split("task")[0]


def clean_input(nwinput_str):
    """ Removes comments from each line (everything after '#') """
    return "\n".join(line.split("#")[0].strip() for line in nwinput_str.splitlines())

def parse_nwpw_block(nwinput_str):
    """ Parses the 'nwpw' block while handling comments and ensuring pspspin parsing works """
    
    # ✅ Step 1: Clean input (remove everything after # in each line)
    nwinput_str = clean_input(nwinput_str)

    # ✅ Step 2: Extract `nwpw` block while ignoring real 'end' but not losing data
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

    # ✅ Fix: Capture both pspspin up & down correctly, even with multiple spaces
    pspspin_up = re.findall(r"pspspin\s+up\s+d\s+(-?\d+\.?\d*)\s+([\d\s]+)", nwpw_block, re.IGNORECASE)
    pspspin_down = re.findall(r"pspspin\s+down\s+d\s+(-?\d+\.?\d*)\s+([\d\s]+)", nwpw_block, re.IGNORECASE)

    if pspspin_up:
        spin_value, indices = pspspin_up[0]
        output.append(f"pspspin{{up d {spin_value} {indices.strip()}}}")

    if pspspin_down:
        spin_value, indices = pspspin_down[0]
        output.append(f"pspspin{{down d {spin_value} {indices.strip()}}}")

    # ✅ Keep the previous "set nwpw:" parsing logic
    set_values = re.findall(r"set\s+(nwpw:\S+)\s+(\S+)", nwinput_str, re.IGNORECASE)
    for key, value in set_values:
        output.append(f"set{{{key} {value}}}")

    return " ".join(output)





nwoutput = "test9.nw"
#nwoutput = "test2.nw"
#nwoutput = "test3.nw"
#nwoutput = "testxyz.nw"

with open(nwoutput,'r') as ff:
   aa = ff.read()

mygeom = parse_geometry(aa)
nwpw_settings = parse_nwpw_block(aa)  # Parses NWPW parameters
calculations = parse_calculation(aa)  # Parses calculation types
print("nwpw_settings=",nwpw_settings)
print("calculations=",calculations)

print("mygeom=",mygeom)

esmiles = f"{mygeom} {nwpw_settings} {calculations}"
print("esmiles=",esmiles)
