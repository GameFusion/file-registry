import os
import mysql.connector
import platform
import hashlib
import json
import time
import argparse
import socket
from tqdm import tqdm
import getpass
from datetime import datetime


def get_database_connection():
    # Load the credentials from the JSON file
    with open('credentials.json') as f:
        credentials = json.load(f)

    # Connect to the MySQL database
    try:
        cnx = mysql.connector.connect(
            user=credentials['user'],
            password=credentials['password'],
            host=credentials['host'],
            database=credentials['database']
        )
        return cnx
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        return None

def is_connection_valid(cnx):
    try:
        # Check if connection is still alive
        return cnx.is_connected()
    except:
        # If an error occurs, assume the connection is not valid
        return False


def file_exists_in_database(cnx, file_path):

    cursor = cnx.cursor()

    try:
        # Check if the file_path exists in the table
        query = "SELECT 1 FROM files WHERE file_path = %s"
        cursor.execute(query, (file_path,))
        result = cursor.fetchone()
        return result is not None
    finally:
        # Ensure the database connection is closed even if an error occurs
        cursor.close()

def add_to_database(cnx, hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date):

    cursor = cnx.cursor()

    # Check if the file_path exists in the table
    cursor.execute("SELECT md5_checksum FROM files WHERE file_path = %s", (file_path,))
    result = cursor.fetchone()
    if result is not None:
        if result[0] == md5_checksum:
            print(f"File {file_path} already exists in the table with the same md5 checksum.")
            return
        else:
            print(f"File {file_path} already exists in the table with a different md5 checksum. Updating the existing entry.")
            cursor.execute("UPDATE files SET md5_checksum = %s, file_size = %s, modification_date = %s WHERE file_path = %s", (md5_checksum, file_size, modification_date, file_path))
            cnx.commit()
            cursor.close()
            return

    # Insert the hostname, IP address, OS version, file path, MD5 checksum, file size, and modification date into the database
    add_server = ("INSERT INTO files "
                  "(hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date) "
                  "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    data_server = (hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date)
    cursor.execute(add_server, data_server)

    # Check if the MD5 checksum is unique or a duplicate
    cursor.execute("SELECT COUNT(*) FROM files WHERE md5_checksum = %s", (md5_checksum,))
    result = cursor.fetchone()
    if result:
        count = result[0]
        if count > 1:
            print(f"Duplicate file found: {file_path}")
            # Add the duplicate file to the duplicates table
            add_duplicate = ("INSERT INTO duplicates "
                             "(file_path, count) "
                             "VALUES (%s, %s)")
            data_duplicate = (file_path, count)
            cursor.execute(add_duplicate, data_duplicate)

            # Get the ID of the duplicate file in duplicates
            cursor.execute("SELECT id FROM duplicates WHERE file_path = %s", (file_path,))
            result = cursor.fetchone()
            if result:
                duplicate_id = result[0]

                # Update the duplicate ID in files
                cursor.execute("UPDATE files SET duplicate_id = %s WHERE file_path = %s", (duplicate_id, file_path))

    # Commit the changes and close the connection
    cnx.commit()
    cursor.close()

def get_file_paths(cnx):
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT file_path FROM files")
        # Fetch all results and extract 'file_path' into a list
        file_paths = [item[0] for item in cursor.fetchall()]
        return file_paths
    except mysql.connector.Error as err:
        print(f"Error fetching file paths: {err}")
        return []
    finally:
        cursor.close()

def scan_directory(cnx, directory_path):
    # Load excluded directories and files from JSON files
    with open('excluded_dirs.json') as f:
        excluded_dirs = set(json.load(f))
    with open('excluded_files.json') as f:
        excluded_files = set(json.load(f))

    # loading cached database
    print("loading files database to cach")
    file_paths_list = get_file_paths(cnx)
    print("done caching")

    # Prepare a list to store all file paths
    print("scaning files...")
    all_files = []
    print("file_paths len in database", len(file_paths_list))
    for root, dirs, files in os.walk(directory_path):
        # Filter out the excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        match_count = 0
        add_count = 0
        for file in files:
            # Skip the excluded files
            if file in excluded_files:
                continue
           
            file_path = os.path.join(root, file)
            
            if file_path in file_paths_list:
                #print("found match", file)
                match_count = match_count+1
                continue

            all_files.append(file_path)
            if(add_count % 100)
                print("adding file", count, end='\r')
            add_count = add_count+1

    print("found matching files ", match_count)
    print("file count :", len(all_files))
        
    # Initialize tqdm progress bar
    pbar = tqdm(total=len(all_files), unit="file")

    for file_path in all_files:

        #
        # fast mode
        #if file_exists_in_database(cnx, file_path):
        #    pbar.update(1)
        #    continue

        hostname = platform.node()
        ip_address = socket.gethostbyname(hostname)
        os_version = platform.platform()

        # Compute the MD5 checksum of the file
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        md5_checksum = md5_hash.hexdigest()

        # Get the file size and modification date
        file_size = os.path.getsize(file_path)
        modification_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))

        add_to_database(cnx, hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date)

        # Update the progress bar
        pbar.update(1)

    # Close the progress bar
    pbar.close()

def log_scan(cnx, directory_path):
    hostname = platform.node()
    ip_address = socket.gethostbyname(hostname)
    user_name = getpass.getuser()
    date_time_issued = datetime.now()

    cursor = cnx.cursor()
    try:
        add_log = ("INSERT INTO scan_log "
                   "(directory_path, host_name, host_ip, user_name, date_time_issued) "
                   "VALUES (%s, %s, %s, %s, %s)")
        data_log = (directory_path, hostname, ip_address, user_name, date_time_issued)
        cursor.execute(add_log, data_log)
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error logging scan: {err}")
    finally:
        cursor.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan a directory and add its files to a MySQL database.')
    parser.add_argument('directory_path', type=str, help='the path to the directory to scan')
    args = parser.parse_args()

    cnx = get_database_connection()
    if cnx and is_connection_valid(cnx):
        log_scan(cnx, args.directory_path)  # Log the scan details
        scan_directory(cnx, args.directory_path)  # Assuming scan_directory now also takes cnx as an argument
        cnx.close()
    else:
        print("Failed to connect to the database or connection timed out.")

