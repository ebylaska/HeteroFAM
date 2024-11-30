USE HeteroFAM_Project;

-- Create the 'materials' table with the additional columns
CREATE TABLE IF NOT EXISTS materials (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier
    name VARCHAR(255) NOT NULL,        -- Material name
    description TEXT,                  -- Material description
    xyz TEXT,                          -- Coordinates or geometry data
    unita VARCHAR(50),                 -- Unit of measurement
    mformula VARCHAR(255),             -- Material formula
    charge INT,                        -- Net charge of the system
    multiplicity INT,                  -- Spin multiplicity
    number_atoms INT,                  -- number of atoms
    xc VARCHAR(100),                   -- Exchange-correlation functional
    theory VARCHAR(255),               -- Theory level or method
    k_points TEXT,                     -- K-points configuration
    smearing_type VARCHAR(50),         -- Smearing method type
    smearing_temperature FLOAT,        -- Smearing temperature
    kerker_energy FLOAT,               -- Kerker Temperature
    fractional_occupations TEXT,       -- JSON format
    initial_spin_penalties TEXT,       -- JSON Initial spin-penalties
    atomic_symbols TEXT,               -- JSON atomic symbols
    atomic_charges TEXT,               -- JSON Blochl atomic charges
    Hubbard_U FLOAT,                   -- Hubbard U parameter for DFT+U
    Hubbard_J FLOAT,                   -- Hubbard J parameter for DFT+U
    calculation_type VARCHAR(100),     -- Type of calculation
    machine VARCHAR(100),              -- Machine name used for calculation
    ncpu INT,                          -- Number of CPUs used
    wall_time VARCHAR(50),             -- Wall time for the computation
    pseudopotentials TEXT,             -- JSON Details of pseudopotentials used
    material_name VARCHAR(255),        -- Name of the material
    lattice_parameter_a FLOAT,         -- Lattice parameter for a
    lattice_parameter_b FLOAT,         -- Lattice parameter for b
    lattice_parameter_c FLOAT,         -- Lattice parameter for c
    lattice_parameter_alpha FLOAT,     -- Lattice parameter for alpha
    lattice_parameter_beta FLOAT,      -- Lattice parameter for beta
    lattice_parameter_gamma FLOAT,     -- Lattice parameter for gamma
    lattice_type VARCHAR(100),         -- Type of lattice
    space_group VARCHAR(50),           -- Space group information
    basis TEXT,                        -- JSON Basis set information
    cif TEXT,                          -- CIF file or related metadata
    energy FLOAT,                      -- Energy of the material/system in atomic units
    enthalpy FLOAT,                    -- Enthalpy value in atomic units
    entropy FLOAT,                     -- Entropy value in atomic units
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- Last update timestamp
);

