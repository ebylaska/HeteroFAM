USE HeteroFAM_Project;


-- Create the 'materials' table with the additional columns
CREATE TABLE IF NOT EXISTS materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_name VARCHAR(255),
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the 'exafs' table
CREATE TABLE IF NOT EXISTS exafs (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier
    name VARCHAR(255) NOT NULL,        -- Material name
    description TEXT,                  -- Material description
    mformula VARCHAR(255),             -- Material formula
    materials_ids JSON,                -- exafs materia id
    materials_weights JSON,            -- exafs weights
    weight_exafs BLOB,                 -- combined exafs BLOB
    experiment_exafs BLOB,              -- experiment exafs BLOB
    version INT DEFAULT 1
);

-- Create join table between exafs and materials
CREATE TABLE IF NOT EXISTS exafs_materials_map (
    exafs_id INT,
    material_id INT,
    weight FLOAT,
    PRIMARY KEY (exafs_id, material_id),
    FOREIGN KEY (exafs_id) REFERENCES exafs(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

-- 🔍 Indexes for faster lookups
CREATE INDEX idx_materials_sample ON materials(sample_name);
CREATE INDEX idx_exafs_name ON exafs(name);

