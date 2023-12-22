import argparse
import hashlib
import os
import xattr

file_count = 0
folder_count = 0
very_verbose = True

# List of folder names to skip
folders_to_skip = [".git", ".snapshots", ".snapshot", "SNAPSHOTS", "snapshot"]
files_to_skip=["._.DS_Store", ".DS_Store"]

import json
import os
import hashlib
import time

errors = []
error_log_json = 'error_log.json'
error_log_txt = 'error_log.txt'
warning_log_txt = 'warning_log.txt'

def md5(fname):
    global errors
    global error_log_json
    global error_log_txt
    hash_md5 = hashlib.md5()
    try:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except OSError as e:
        errors.append({
            'filename': fname,
            'os_error': str(e),
            'timestamp': time.time()
          #  'is_defunct_link': os.path.islink(fname) and not os.path.exists(fname)
        })
        with open(error_log_json, 'w') as f:
            json.dump(errors, f)
        with open(error_log_txt, 'a') as f:
            f.write(f'Error occurred at {time.ctime(time.time())} while processing {fname}. Error message: {str(e)}\n')
        print("Exception occured", str(e))
        return "";
        #exit(0)
    return hash_md5.hexdigest()

def md5_exit_on_error(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def store_md5_metadata(file_path):

    try:
        existing_md5_checksum = xattr.getxattr(file_path, "user.md5_checksum")
        #if existing_md5_checksum == md5_checksum:
        try:
            print(f"MD5 checksum already exists for {file_count} : {file_path} {existing_md5_checksum}")
        except:
            print(f"MD5 checksum already exists for {file_count} : NON UTF8 NAME {existing_md5_checksum}")
        return
    except OSError:
        pass
    md5_checksum = md5(file_path)
    try:
        byte_obj = bytes("user.md5_checksum", 'utf-8')
        os.setxattr(file_path, byte_obj, bytes(md5_checksum, 'utf-8'))
        file_path_print = str(file_path).encode('ascii', 'ignore')
        print(f"MD5 checksum stored in metadata for {file_count} {file_path_print}")
    except OSError as e:
        with open(error_log_txt, 'a') as f:
            f.write(f'Error occurred at {time.ctime(time.time())} while processing {file_count}; {file_path}. Error message: {str(e)}\n')
        print(f"MD5 checksum NOT stored in metadata for {file_count} : {file_path} {md5_checksum} {str(e)}")

def md5_folder(folder_path):
    global very_verbose
    for root, dirs, files in os.walk(folder_path):
        # Remove folders to skip from the list of directories
        dirs[:] = [d for d in dirs if d not in folders_to_skip]
        global folder_count
        folder_count += len(dirs)

        for file in files:
            if file in files_to_skip:
                print("skipping ", file)
                continue
            file_path = os.path.join(root, file)
            global file_count
            file_count += 1

            if very_verbose:
                file_path_print = str(file_path).encode('ascii', 'ignore')
                print(f"File: {file_path_print}")
            store_md5_metadata(file_path)

if __name__ == "__main__":
    #global error_log_json
    #global error_log_txt

    parser = argparse.ArgumentParser(description="Compute MD5 values for all files in a folder.")
    parser.add_argument("folder_path", type=str, help="Path to the folder to scan.")
    args = parser.parse_args()
    root_path = args.folder_path 
    root_path = root_path.replace(" ", "_")
    root_path = root_path.replace("/", "---")
    root_path = ''.join(e for e in root_path if e.isalnum() or e in ['_', '-'])

    error_log_json = f'error_log_{root_path}.json'
    error_log_txt = f'error_log_{root_path}.txt'
    warning_log_txt = f'warning_log_{root_path}.txt'

    if os.path.exists(error_log_json):
        with open(error_log_json, 'r+') as f:
            f.truncate(0)

    if os.path.exists(error_log_txt):
        with open(error_log_txt, 'r+') as f:
            f.truncate(0)

    if os.path.exists(warning_log_txt):
        with open(warning_log_txt, 'r+') as f:
            f.truncate(0)


    md5_folder(args.folder_path)
    print(f"Total number of files: {file_count}")
    print(f"Total number of folders: {folder_count}")

