#!/usr/bin/env python3
"""
MD5 Metadata Scanner
-------------------
This script scans directories and calculates MD5 checksums for files,
storing the results either in a central MySQL database or as extended attributes.
"""

import argparse
import hashlib
import os
import time
import json
import socket
import platform
from tqdm import tqdm
import log_scan

# For xattr support
try:
    import xattr
    XATTR_AVAILABLE = True
except ImportError:
    XATTR_AVAILABLE = False

# For database support
try:
    import mysql.connector
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Counters
file_count = 0
folder_count = 0
very_verbose = False

# List of folder names to skip
folders_to_skip = [".git", ".gitold", ".snapshots", ".snapshot", "SNAPSHOTS", "snapshot"]
files_to_skip = ["._.DS_Store", ".DS_Store", ".localized", ".Spotlight-V100", ".Trashes", ".fseventsd", ".local", ".kde"]

# Error logging
errors = []
error_log_json = 'error_log.json'
error_log_txt = 'error_log.txt'
warning_log_txt = 'warning_log.txt'

def get_database_connection():
    """Connect to the database using credentials from config file."""
    try:
        # Load credentials from JSON file
        with open('config/credentials.json') as f:
            credentials = json.load(f)

        # Connect to MySQL database
        cnx = mysql.connector.connect(
            user=credentials['user'],
            password=credentials['password'],
            host=credentials['host'],
            database=credentials['database']
        )
        return cnx
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def is_connection_valid(cnx):
    """Check if database connection is still valid."""
    try:
        return cnx and cnx.is_connected()
    except:
        return False

def md5(fname):
    """Calculate MD5 hash of a file, handling errors gracefully."""
    global errors, error_log_json, error_log_txt
    
    hash_md5 = hashlib.md5()
    try:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except OSError as e:
        # Log error
        errors.append({
            'filename': fname,
            'os_error': str(e),
            'timestamp': time.time()
        })
        with open(error_log_json, 'w') as f:
            json.dump(errors, f)
        with open(error_log_txt, 'a') as f:
            f.write(f'Error occurred at {time.ctime(time.time())} while processing {fname}. Error message: {str(e)}\n')
        print(f"Exception occurred: {str(e)}")
        return ""

def store_md5_xattr(file_path, md5_checksum):
    """Store MD5 checksum as an extended attribute."""
    if not md5_checksum:
        return False
        
    try:
        byte_obj = bytes("user.md5_checksum", 'utf-8')
        os.setxattr(file_path, byte_obj, bytes(md5_checksum, 'utf-8'))
        return True
    except OSError as e:
        with open(error_log_txt, 'a') as f:
            f.write(f'Error storing xattr at {time.ctime(time.time())} for {file_path}. Error: {str(e)}\n')
        print(f"Could not store MD5 checksum in xattr: {str(e)}")
        return False

def check_existing_xattr(file_path):
    """Check if MD5 checksum exists as extended attribute."""
    try:
        md5_checksum = xattr.getxattr(file_path, "user.md5_checksum")
        return md5_checksum.decode('utf-8')
    except:
        return None

def store_md5_database(cnx, file_path, md5_checksum):
    """Store MD5 checksum in the database."""
    if not md5_checksum:
        return False
        
    try:
        # Get file metadata
        file_size = os.path.getsize(file_path)
        modification_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        scan_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        
        # Calculate file path hash for uniqueness
        file_path_hash = hashlib.md5(file_path.encode()).hexdigest()
        
        cursor = cnx.cursor()
        
        # Insert or update the MD5 metadata
        query = """
            INSERT INTO file_metadata
            (file_path, md5_checksum, file_size, modification_date, scan_date, file_path_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            md5_checksum = %s,
            file_size = %s,
            modification_date = %s,
            scan_date = %s
        """
        cursor.execute(query, (
            file_path, md5_checksum, file_size, modification_date, scan_date, file_path_hash,
            md5_checksum, file_size, modification_date, scan_date
        ))
        
        cursor.close()
        return True
    except Exception as e:
        with open(error_log_txt, 'a') as f:
            f.write(f'Database error at {time.ctime(time.time())} for {file_path}. Error: {str(e)}\n')
        print(f"Database error: {str(e)}")
        return False

def check_existing_database(cnx, file_path):
    """Check if metadata already exists in database."""
    cursor = cnx.cursor()
    try:
        # Get file path hash
        file_path_hash = hashlib.md5(file_path.encode()).hexdigest()
        
        # Check if file exists with up-to-date modification time
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        
        # Query by hash (faster)
        query = """
            SELECT md5_checksum 
            FROM file_metadata 
            WHERE file_path_hash = %s AND modification_date = %s
        """
        cursor.execute(query, (file_path_hash, mtime))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        return None
    except Exception as e:
        if very_verbose:
            print(f"Error checking database: {str(e)}")
        return None
    finally:
        cursor.close()

def process_file(cnx, file_path, storage_mode):
    """Process a single file - calculate and store MD5."""
    global file_count
    
    # Check for existing MD5 checksum
    existing_md5 = None
    
    if storage_mode == "database" and cnx:
        existing_md5 = check_existing_database(cnx, file_path)
        if existing_md5:
            if very_verbose:
                print(f"[DB] MD5 already exists for {file_path}: {existing_md5}")
            return "skipped"
    elif storage_mode == "xattr" and XATTR_AVAILABLE:
        existing_md5 = check_existing_xattr(file_path)
        if existing_md5:
            if very_verbose:
                print(f"[XATTR] MD5 already exists for {file_path}: {existing_md5}")
            return "skipped"
    
    # Calculate MD5 if needed
    md5_checksum = md5(file_path)
    if not md5_checksum:
        return "error"
    
    # Store the MD5 checksum
    success = False
    if storage_mode == "database" and cnx:
        success = store_md5_database(cnx, file_path, md5_checksum)
        if success and very_verbose:
            print(f"[DB] Stored MD5 for {file_path}: {md5_checksum}")
    elif storage_mode == "xattr" and XATTR_AVAILABLE:
        success = store_md5_xattr(file_path, md5_checksum)
        if success and very_verbose:
            print(f"[XATTR] Stored MD5 for {file_path}: {md5_checksum}")
    elif storage_mode == "both" and cnx and XATTR_AVAILABLE:
        success_db = store_md5_database(cnx, file_path, md5_checksum)
        success_xattr = store_md5_xattr(file_path, md5_checksum)
        success = success_db or success_xattr
        if very_verbose:
            print(f"[BOTH] Stored MD5 for {file_path}: {md5_checksum} (DB: {success_db}, XATTR: {success_xattr})")
    
    return "success" if success else "error"

def scan_directory(cnx, folder_path, storage_mode):
    """Scan a directory and process all files."""
    global folder_count, file_count, very_verbose
    
    print(f"Scanning directory: {folder_path}")
    print(f"Using storage mode: {storage_mode}")
    
    # Check for storage mode availability
    if storage_mode in ["database", "both"] and not cnx:
        print("WARNING: Database connection failed. Cannot use database storage.")
        if storage_mode == "database":
            if XATTR_AVAILABLE:
                print("Falling back to xattr storage.")
                storage_mode = "xattr"
            else:
                print("ERROR: Cannot proceed without database or xattr support.")
                return
    
    if storage_mode in ["xattr", "both"] and not XATTR_AVAILABLE:
        print("WARNING: xattr not available. Cannot use xattr storage.")
        if storage_mode == "xattr":
            if cnx:
                print("Falling back to database storage.")
                storage_mode = "database"
            else:
                print("ERROR: Cannot proceed without database or xattr support.")
                return
    
    # Find all files to process
    all_files = []
    print("Building file list...")
    
    for root, dirs, files in os.walk(folder_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in folders_to_skip]
        folder_count += len(dirs)
        
        # Process each file
        for filename in files:
            if filename in files_to_skip:
                continue
            file_path = os.path.join(root, filename)
            all_files.append(file_path)
    
    # Process files with progress bar
    print(f"Found {len(all_files)} files to process.")
    
    pbar = tqdm(total=len(all_files), unit="file")
    
    # Initialize counters
    processed = 0
    skipped = 0
    success = 0
    errors = 0
    
    # Process each file
    commit_interval = 100  # How often to commit database changes
    
    for i, file_path in enumerate(all_files):
        file_count += 1
        
        # Process file
        result = process_file(cnx, file_path, storage_mode)
        
        # Update counters
        processed += 1
        if result == "skipped":
            skipped += 1
        elif result == "success":
            success += 1
        else:
            errors += 1
        
        # Commit database changes periodically
        if storage_mode in ["database", "both"] and cnx and i % commit_interval == 0:
            cnx.commit()
        
        # Update progress bar
        pbar.set_description(f"Processed: {processed}, Skipped: {skipped}, Success: {success}, Errors: {errors}")
        pbar.update(1)
    
    # Final commit
    if storage_mode in ["database", "both"] and cnx:
        cnx.commit()
    
    pbar.close()
    
    # Print summary
    print("\nScan Complete:")
    print(f"Total files: {processed}")
    print(f"Skipped (already processed): {skipped}")
    print(f"Successfully processed: {success}")
    print(f"Errors: {errors}")
    print(f"Total folders: {folder_count}")
    print(f"Storage mode used: {storage_mode}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Compute MD5 checksums for files and store in database or as extended attributes.")
    parser.add_argument("folder_path", type=str, help="Path to the folder to scan.")
    parser.add_argument("--storage", choices=["database", "xattr", "both"], default="database",
                      help="Where to store MD5 checksums: database, xattr, or both. Default: database")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()
    
    # Set global variables
    very_verbose = args.verbose
    storage_mode = args.storage
    
    # Sanitize path for log files
    root_path = args.folder_path 
    root_path = root_path.replace(" ", "_")
    root_path = root_path.replace("/", "---")
    root_path = ''.join(e for e in root_path if e.isalnum() or e in ['_', '-'])
    
    # Set up log files
    error_log_json = f'error_log_{root_path}.json'
    error_log_txt = f'error_log_{root_path}.txt'
    warning_log_txt = f'warning_log_{root_path}.txt'
    
    # Clear existing log files
    for log_file in [error_log_json, error_log_txt, warning_log_txt]:
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.truncate(0)
    
    # Initialize database connection if needed
    cnx = None
    if storage_mode in ["database", "both"]:
        if not DB_AVAILABLE:
            print("ERROR: mysql-connector-python is not installed. Cannot use database storage.")
            if storage_mode == "database":
                if XATTR_AVAILABLE:
                    print("Falling back to xattr storage.")
                    storage_mode = "xattr"
                else:
                    print("Cannot continue without database or xattr support.")
                    exit(1)
        else:
            print("Connecting to database...")
            cnx = get_database_connection()
            
            if not is_connection_valid(cnx):
                print("WARNING: Database connection failed.")
                if storage_mode == "database":
                    if XATTR_AVAILABLE:
                        print("Falling back to xattr storage.")
                        storage_mode = "xattr"
                    else:
                        print("Cannot continue without database or xattr support.")
                        exit(1)
    
    # Check xattr availability if needed
    if storage_mode in ["xattr", "both"] and not XATTR_AVAILABLE:
        print("WARNING: xattr module not available. Cannot use xattr storage.")
        if storage_mode == "xattr":
            if DB_AVAILABLE and cnx:
                print("Falling back to database storage.")
                storage_mode = "database"
            else:
                print("Cannot continue without database or xattr support.")
                exit(1)
    
    try:
        # Scan the directory
        if cnx:
            print("Scanning with database storage...")
            log_scan.log_scan(cnx, args.folder_path)
        scan_directory(cnx, args.folder_path, storage_mode)
    finally:
        # Close database connection if open
        if cnx:
            cnx.close()
            print("Database connection closed.")
    
    print(f"Total number of files: {file_count}")
    print(f"Total number of folders: {folder_count}")