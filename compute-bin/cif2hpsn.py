from ase.io import read
from math import acos, degrees
import json

# Predefined magnetic moments (in μB) for common elements
MAGNETIC_MOMENTS = {
    "H": 0.0, "He": 0.0,
    "Li": 0.0, "Be": 0.0, "B": 0.0, "C": 0.0, "N": 0.0, "O": 0.0, "F": 0.0, "Ne": 0.0,
    "Na": 0.0, "Mg": 0.0, "Al": 0.0, "Si": 0.0, "P": 0.0, "S": 0.0, "Cl": 0.0, "Ar": 0.0,
    "K": 0.0, "Ca": 0.0, 
    "Sc": 0.0, "Ti": 0.0, "V": 1.0, "Cr": 2.0, "Mn": 5.0, "Fe": 5.0, "Co": 3.0, "Ni": 2.0,
    "Cu": 1.0, "Zn": 0.0, 
    "Ru": 1.0, "Rh": 0.0, "Pd": 0.0, "Ag": 0.0, "Cd": 0.0, 
    "La": 0.0, "Ce": 1.0, "Pr": 3.0, "Nd": 3.5, "Pm": 3.5, "Sm": 3.0, "Eu": 7.0,
    # Extend this for the rest of the periodic table
}

def assign_afm_spins(structure, axis='c', magnitude=5.0):
    """
    Assign antiferromagnetic spins based on spatial layers along a given axis.
    Non-magnetic elements (e.g., O) are assigned spin magnitude 0.0.
    :param structure: ASE Atoms object.
    :param axis: Lattice direction for AFM ordering ('a', 'b', or 'c').
    :param magnitude: Magnetic moment magnitude for AFM ordering.
    :return: List of spin dictionaries.
    """
    axis_map = {'a': 0, 'b': 1, 'c': 2}
    axis_index = axis_map[axis]
    
    # Get unique layers along the chosen axis (in fractional coordinates)
    fractional_positions = structure.get_scaled_positions()
    layers = sorted(set(fractional_positions[:, axis_index]))
    
    # Assign spins alternatingly for layers
    magnetic_spins = []
    for atom, frac_coords in zip(structure, fractional_positions):
        # Exclude non-magnetic elements
        spin_magnitude = MAGNETIC_MOMENTS.get(atom.symbol, 0.0)
        if spin_magnitude == 0.0:
            spin_orientation = [0, 0, 0]  # No orientation for non-magnetic atoms
        else:
            layer_index = layers.index(frac_coords[axis_index])  # Use fractional coordinate for layer index
            spin_magnitude = magnitude if layer_index % 2 == 0 else -magnitude
            spin_orientation = [0, 0, +1] if spin_magnitude > 0 else [0, 0, -1]
        
        magnetic_spins.append({
            "atom_index": atom.index,
            "symbol": atom.symbol,
            "spin_magnitude": abs(spin_magnitude),
            "spin_orientation": spin_orientation
        })

    return magnetic_spins


def cif_to_hpsn(cif_file, assign_spins=False, axis='c', magnitude=5.0):
    """
    Convert a CIF file to HPSN notation with optional magnetic spins and orientations.
    
    :param cif_file: Path to the CIF file.
    :param assign_spins: Boolean to assign magnetic spins to atoms.
    :param axis: Lattice direction for AFM ordering ('a', 'b', or 'c').
    :param magnitude: Magnetic moment magnitude for AFM ordering.
    :return: HPSN dictionary.
    """
    # Read CIF file using ASE
    structure = read(cif_file)
    
    # Extract lattice parameters
    cell = structure.get_cell()
    a, b, c = cell.lengths()
    alpha = degrees(acos(cell[1].dot(cell[2]) / (b * c)))  # Angle between b and c
    beta = degrees(acos(cell[0].dot(cell[2]) / (a * c)))  # Angle between a and c
    gamma = degrees(acos(cell[0].dot(cell[1]) / (a * b)))  # Angle between a and b
    
    lattice_params = {
        "a": a,
        "b": b,
        "c": c,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma
    }
    
    # Extract atomic positions and types
    atoms = []
    for i, atom in enumerate(structure):
        frac_coords = structure.get_scaled_positions()[i]
        atoms.append([i, atom.symbol, frac_coords[0], frac_coords[1], frac_coords[2]])

    # Generate adjacency list (based on a cutoff radius)
    cutoff = 2.5  # Angstrom, adjustable
    adjacency_list = {}
    for i, atom1 in enumerate(atoms):
        adjacency_list[i] = []
        for j, atom2 in enumerate(atoms):
            if i != j:
                dist = structure.get_distance(i, j, mic=True)
                if dist < cutoff:
                    adjacency_list[i].append([j, "single"])  # Default bond type
    
    # Create HPSN dictionary
    hpsn = {
        "name": structure.get_chemical_formula(),
        "lattice": lattice_params,
        "type": "Hybrid",
        "atoms": atoms,
        "adjacency_list": adjacency_list
    }
    
    # Add magnetic spins to HPSN if applicable
    if assign_spins:
        magnetic_spins = assign_afm_spins(structure, axis=axis, magnitude=magnitude)
        hpsn["magnetic_spins"] = magnetic_spins
    
    return hpsn


def save_hpsn_to_json(hpsn, output_file):
    """
    Save HPSN dictionary to a JSON file.
    
    :param hpsn: HPSN dictionary.
    :param output_file: Path to save JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(hpsn, f, indent=4)
        print(f"HPSN saved to {output_file}")


# Example usage
cif_file_path = "1011267.cif"  # Path to your CIF file
output_json_path = "output_hpsn_with_afm_spins.json"

# Convert CIF to HPSN with AFM spins
hpsn_data = cif_to_hpsn(cif_file_path, assign_spins=True, axis='c', magnitude=5.0)
save_hpsn_to_json(hpsn_data, output_json_path)

