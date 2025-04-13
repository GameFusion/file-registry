-- File Registry Database Setup
-- This script creates the necessary tables for the File Registry system

-- Files table - Stores information about each file in the registry
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255),
    ip_address VARCHAR(255),
    os_version VARCHAR(255),
    file_path VARCHAR(255),
    md5_checksum VARCHAR(32),
    file_size BIGINT,
    modification_date DATETIME,
    duplicate_id INT
);

-- Duplicates table - Tracks duplicate files across the system
CREATE TABLE duplicates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255),
    count INT
);

-- Scan Log table - Records scanning activity
CREATE TABLE scan_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    directory_path VARCHAR(255),
    host_name VARCHAR(255),
    host_ip VARCHAR(15),
    user_name VARCHAR(255),
    date_time_issued DATETIME
);

-- Metadata table - Stores file metadata including MD5 checksums
CREATE TABLE IF NOT EXISTS file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(1024) NOT NULL,
    md5_checksum VARCHAR(32) NOT NULL,
    file_size BIGINT,
    modification_date DATETIME,
    scan_date DATETIME,
    file_path_hash VARCHAR(32) NOT NULL,
    UNIQUE INDEX (file_path_hash),
    INDEX (file_path(190))
);

