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


def search_file_path_substring_in_database(cnx, search_substring):
    cursor = cnx.cursor()
    try:
        query = "SELECT EXISTS(SELECT 1 FROM files WHERE file_path LIKE %s)"
        search_pattern = "%" + search_substring + "%"
        cursor.execute(query, (search_pattern,))
        result = cursor.fetchone()
        return result[0] == 1
    except mysql.connector.Error as err:
        print(f"Error searching for file path substring: {err}")
        return False
    finally:
        cursor.close()

def find_file_paths_by_substring(cnx, search_substring):
    cursor = cnx.cursor()
    try:
        query = "SELECT file_path FROM files WHERE file_path LIKE %s"
        search_pattern = "%" + search_substring + "%"
        cursor.execute(query, (search_pattern,))
        results = cursor.fetchall()
        return [result[0] for result in results] if results else []
    except mysql.connector.Error as err:
        print(f"Error searching for file path substring: {err}")
        return []
    finally:
        cursor.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan a directory and add its files to a MySQL database. Optionally, search for a file path substring.')
    parser.add_argument('search', type=str, help='substring to search in file paths')
    args = parser.parse_args()

    cnx = get_database_connection()
    if cnx and is_connection_valid(cnx):
        if args.search:
            # Perform the search operation
            matching_file_paths = find_file_paths_by_substring(cnx, args.search)
            if matching_file_paths:
                print(f"Found file paths containing '{args.search}':")
                for path in matching_file_paths:
                    print(path)
                print("Found matching file_path count :",len(matching_file_paths))
            else:
                print(f"No file paths containing '{args.search}' found in the database.")

        cnx.close()
    else:
        print("Database connection failed or timed out.")



