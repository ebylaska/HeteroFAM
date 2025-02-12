"""A class to perform baser analysis on a gaussian cube file or CHGCAR."""

import shutil
import subprocess
import uuid

from pathlib import Path
from typing import Union

import numpy as np

from ase import Atoms
from ase.calculators.vasp import VaspChargeDensity
from ase.io import cube, read, write
from ase.io.bader import attach_charges
from ase.units import Bohr


def write_charges_to_file(fname, atoms):
    """Write atomic spins to a separate file."""
    with open(fname, "w") as f:
        f.write("# Atomic charges\n")
        f.write(f"# {'Atom':<5} {'X':>12} {'Y':>12} {'Z':>12} {'Charge':>12}\n")
        positions = atoms.get_positions()
        spins = atoms.arrays["initial_charges"]
        symbols = atoms.get_chemical_symbols()
        for symbol, (x, y, z), spin in zip(symbols, positions, spins):
            f.write(
                f"{symbol:<5} {x / Bohr:12.6f} {y / Bohr:12.6f} {z / Bohr:12.6f} {spin:12.6f}\n"
            )

def combine_cube_files(cube_1, cube_2, operation, output_cube_file=None):
    """Return the combination of the two cube files.
    
    Both cube files should be cube files of the same atomic structure, possibly different densities.
    """
    with open(cube_1, "r") as f:
        cube_data_1 = cube.read_cube(f)
    with open(cube_2, "r") as f:
        cube_data_2 = cube.read_cube(f)
    try:
        cube_data_1["data"] = operation(cube_data_1["data"], cube_data_2["data"])
    except Exception:
        cube_data_1["data"] = operation([cube_data_1["data"], cube_data_2["data"]])
    return cube_data_1

class Bader:
    """A class to perform bader analysis on Gaussian cube or CHGCAR files."""

    def __init__(self, bader_script_path: Path, scratch_directory: Path = "/tmp"):
        """Initialize self with the given bader script path.

        This class is designed to be run using this code, which must be installed:
        https://theory.cm.utexas.edu/henkelman/code/bader/

        bader_script_path: path to bader charge script.
        scratch_directory: scratch directory for atomic charges.
        """
        self.bader_script_path = Path(bader_script_path).resolve()
        self.scratch_directory = Path(scratch_directory).resolve()

    def __call__(self, charge_data: Union[Path, dict], out_dir: Path = None):
        """Calculate the atomic charges for the given cube file, optionally saving the output.

        charge_file: Path to the cube file
        out_dir: Optional output directory to store the results (will overwrite existing charges)
        """
        
        # Create a unique temporary directory
        temp_dir = self.scratch_directory / str(uuid.uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)

        if isinstance(charge_data, dict):
            charge_file = (temp_dir / "_TEMPORARY_CUBE_FILE.cube").resolve()
            with open(charge_file, "w") as f:
                cube.write_cube(f, charge_data["atoms"], data=charge_data["data"], origin=charge_data["origin"])
            
        else:
            charge_file = Path(charge_data).resolve()

        # Run the script
        output = subprocess.run(
            [str(self.bader_script_path), str(charge_file)],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
        )
        # Check for errors
        output.check_returncode()

        results = self._parse_files(temp_dir, charge_file)

        # Clean the temp directory
        if out_dir is not None:
            for p in temp_dir.glob("*.*"):
                if p.stem != "_TEMPORARY_CUBE_FILE":
                    p.replace(out_dir / (p.stem + "".join(p.suffixes)))
            with open(out_dir / "bader.out") as f:
                f.write(output.stdout)

        shutil.rmtree(temp_dir)
        return results


    @staticmethod
    def _parse_files(bader_dir: Path, charge_file: Path):
        """Parse the output charge files from the files_dir."""
        if "cube" in charge_file.suffix:
            with open(charge_file, "r") as f:
                ats = cube.read_cube(f)["atoms"]
        elif "CHGCAR" in str(charge_file):
            ats = VaspChargeDensity.read(charge_file).atoms[0]  # TODO: test this
        else:
            ats = read(charge_file)
            ats = ats[0] if not isinstance(ats, Atoms) else ats

        attach_charges(ats, str(bader_dir / "ACF.dat"))

        return ats

def calculate_spin_charges(alpha_cube: Path, beta_cube: Path, bader: Bader = None) -> np.array:
    """
    Calculate the spin charges given the Gaussian cube files of spin up and down density.

    Args:
        alpha_cube (Path): Path to the spin up guassian cube file.
        beta_cube (Path): Path to the spin down guassian cube file.
        bader (Bader, optional): A Bader object that performs bader charge analysis.

    Returns:
        np.ndarray: A NumPy array containing the spin charges per atom.
    """
    if bader is None:
        bader = Bader(Path().home() / "bader") # TODO: set this with docker
    up_ats = bader(alpha_cube)
    down_ats = bader(beta_cube)
    up_ats.arrays["initial_charges"] -= down_ats.arrays["initial_charges"]
    return up_ats.arrays["initial_charges"]
    

if __name__ == "__main__":
    bader = Bader(Path().home() / "bader")
    up_spin_file = Path("cube_files", "alpha.cube")
    down_spin_file = Path("cube_files", "beta.cube")
    diff_spin_file = Path("cube_files", "spin.cube")
    total_spin_file = Path("cube_files", "total.cube")

    up_spins = bader(up_spin_file)
    down_spins = bader(down_spin_file)
    total_spins = bader(total_spin_file)
    #iff_per_tot_spins = bader(combine_cube_files(diff_spin_file, total_spin_file, np.divide))
    diff_spins = up_spins.copy()
    diff_spins.arrays["initial_charges"] = (
        up_spins.arrays["initial_charges"] - down_spins.arrays["initial_charges"]
    )
    assert np.all(diff_spins.arrays["initial_charges"] == calculate_spin_charges(up_spin_file, down_spin_file))

    write_charges_to_file("up_charges.txt", up_spins)
    write_charges_to_file("down_charges.txt", down_spins)
    write_charges_to_file("total_charges.txt", total_spins)
    #write_charges_to_file("diff_per_tot_charges.txt", diff_per_tot_spins)
    write_charges_to_file("diff_charges.txt", diff_spins)

    Path("outputs").mkdir(parents=True, exist_ok=True)
    write(Path("outputs", "up.xyz"), up_spins)
    write(Path("outputs", "down.xyz"), down_spins)
    write(Path("outputs", "total.xyz"), total_spins)
    #write(Path("outputs", "diff_per_tot.xyz"), diff_per_tot_spins)
    write(Path("outputs", "diff.xyz"), diff_spins)
