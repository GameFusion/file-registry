
To create database :

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

CREATE TABLE duplicates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255),
    count INT
);


CREATE TABLE scan_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    directory_path VARCHAR(255),
    host_name VARCHAR(255),
    host_ip VARCHAR(15),
    user_name VARCHAR(255),
    date_time_issued DATETIME
);


