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
    duplicate_id INT,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'missing', 'likely_deleted', 'deleted', 'moved') DEFAULT 'active'
);

-- Duplicates table - Tracks duplicate files across the system
CREATE TABLE duplicates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255),
    count INT,
    detection_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scan Log table - Records scanning activity
CREATE TABLE scan_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    directory_path VARCHAR(255),
    host_name VARCHAR(255),
    host_ip VARCHAR(15),
    os_version VARCHAR(255),
    user_name VARCHAR(255),
    date_time_issued DATETIME,
    scan_type VARCHAR(50) DEFAULT 'full',
    status VARCHAR(50) DEFAULT 'in-progress',
    scan_duration INT,
    scan_start_time DATETIME,
    scan_end_time DATETIME
);

-- Metadata table - Stores file metadata including MD5 checksums
CREATE TABLE IF NOT EXISTS file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_log_id INT,
    file_path VARCHAR(1024) NOT NULL,
    md5_checksum VARCHAR(32) NOT NULL,
    file_size BIGINT,
    modification_date DATETIME,
    scan_date DATETIME,
    file_path_hash VARCHAR(32) NOT NULL,
    UNIQUE INDEX (file_path_hash, scan_log_id)
);

-- File History table - Tracks changes to files over time
CREATE TABLE IF NOT EXISTS file_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT,
    event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type ENUM('created', 'modified', 'deleted', 'moved', 'status_change'),
    old_md5 VARCHAR(32),
    new_md5 VARCHAR(32),
    old_path VARCHAR(1024),
    new_path VARCHAR(1024),
    old_status VARCHAR(50),
    new_status VARCHAR(50)
);
