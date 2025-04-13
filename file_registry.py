import os
import mysql.connector
import platform
import hashlib
import json
import time
import argparse
import socket
from tqdm import tqdm

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

# Example usage
cnx = get_database_connection()

def file_exists_in_database(file_path):

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

def add_to_database(hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date):

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

def scan_directory_old(directory_path):
    # Recursively scan the directory and its subdirectories
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
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

            add_to_database(hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date)

from tqdm import tqdm

def scan_directory(directory_path):
    # Prepare a list to store all file paths
    print("scaning files...")
    all_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            all_files.append(os.path.join(root, file))

    print("file count :", len(all_files))
        
    # Initialize tqdm progress bar
    pbar = tqdm(total=len(all_files), unit="file")

    for file_path in all_files:

        # fast mode
        if file_exists_in_database(file_path):
            pbar.update(1)
            continue

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

        add_to_database(hostname, ip_address, os_version, file_path, md5_checksum, file_size, modification_date)

        # Update the progress bar
        pbar.update(1)

    # Close the progress bar
    pbar.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan a directory and add its files to a MySQL database.')
    parser.add_argument('directory_path', type=str, help='the path to the directory to scan')
    args = parser.parse_args()

    scan_directory(args.directory_path)

