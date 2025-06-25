-- Create the root user with full privileges
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '05291999';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;


-- Optionally, add localhost access for root
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Create databases
CREATE DATABASE IF NOT EXISTS TNT_Project;
CREATE DATABASE IF NOT EXISTS HeteroFAM_Project;

-- Create user 'arrows' with access to 'TNT_Project'
CREATE USER IF NOT EXISTS 'arrows'@'%' IDENTIFIED BY 'reaction';
GRANT ALL PRIVILEGES ON TNT_Project.* TO 'arrows'@'%';

-- Load eric3.sql into TNT_Project
USE TNT_Project;
SOURCE /docker-entrypoint-initdb.d/eric3.sql;

-- Create user 'hetero' with access to 'HeteroFAM_Project'
CREATE USER IF NOT EXISTS 'hetero'@'%' IDENTIFIED BY 'solid';
GRANT ALL PRIVILEGES ON HeteroFAM_Project.* TO 'hetero'@'%';

-- Load eric4.sql into HeteroFAM_Project
USE HeteroFAM_Project;
SOURCE /docker-entrypoint-initdb.d/eric4.sql;


-- Grant user 'arrows' access to the 'HeteroFAM_Project' database
-- Grant user 'hetero' access to the 'TNT_Project' database
GRANT ALL PRIVILEGES ON HeteroFAM_Project.* TO 'arrows'@'%';
GRANT ALL PRIVILEGES ON TNT_Project.* TO 'hetero'@'%';

-- Apply changes
FLUSH PRIVILEGES;

