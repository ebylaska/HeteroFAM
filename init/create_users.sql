

-- ------------------------------
-- Ensure root access from all hosts
-- ------------------------------
ALTER USER 'root'@'localhost' IDENTIFIED BY '05291999';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '05291999';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;


-- ------------------------------
-- Create databases if they don't exist
-- ------------------------------
CREATE DATABASE IF NOT EXISTS TNT_Project;
CREATE DATABASE IF NOT EXISTS HeteroFAM_Project;



-- ------------------------------
-- Create user 'arrows' and grant access to TNT_Project
-- ------------------------------
CREATE USER IF NOT EXISTS 'arrows'@'%' IDENTIFIED BY 'reaction';
GRANT ALL PRIVILEGES ON TNT_Project.* TO 'arrows'@'%';

-- ------------------------------
-- Load TNT_Project schema
-- Make sure eric3.sql starts with: USE TNT_Project;
-- ------------------------------
SOURCE /docker-entrypoint-initdb.d/backup/eric3.sql;

-- ------------------------------
-- Create user 'hetero' and grant access to HeteroFAM_Project
-- ------------------------------
CREATE USER IF NOT EXISTS 'hetero'@'%' IDENTIFIED BY 'solid';
GRANT ALL PRIVILEGES ON HeteroFAM_Project.* TO 'hetero'@'%';


-- Load eric5.sql into HeteroFAM_Project
SOURCE /docker-entrypoint-initdb.d/backup/eric5.sql;


-- Grant user 'arrows' access to the 'HeteroFAM_Project' database
-- Grant user 'hetero' access to the 'TNT_Project' database
GRANT ALL PRIVILEGES ON HeteroFAM_Project.* TO 'arrows'@'%';
GRANT ALL PRIVILEGES ON TNT_Project.* TO 'hetero'@'%';

-- Apply changes
FLUSH PRIVILEGES;

