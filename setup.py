#!/usr/bin/env python3
"""
File Registry Setup Script
--------------------------
This script helps new users set up the File Registry system by:
1. Creating necessary configuration files
2. Guiding through database setup
3. Verifying the installation
"""

import os
import json
import sys
import getpass
import subprocess
import mysql.connector
from mysql.connector import Error

CONFIG_DIR = "config"
TEMPLATE_FILE = "config_templates.json"
DB_SETUP_FILE = "db_setup.sql"

def print_banner():
    """Display a welcome banner for the setup script."""
    print("\n" + "=" * 60)
    print("  FILE REGISTRY SETUP WIZARD".center(60))
    print("=" * 60)
    print("\nThis script will help you set up the File Registry system.")
    print("You will need to provide database credentials and confirm setup options.\n")

def load_templates():
    """Load configuration templates from the template file."""
    try:
        with open(TEMPLATE_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {TEMPLATE_FILE} not found. Make sure you're running this script from the project root.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {TEMPLATE_FILE} is not valid JSON.")
        sys.exit(1)

def create_config_directory():
    """Create the configuration directory if it doesn't exist."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        print(f"Created configuration directory: {CONFIG_DIR}")
    else:
        print(f"Configuration directory already exists: {CONFIG_DIR}")

def setup_database_connection():
    """Guide the user through setting up database credentials."""
    print("\n" + "-" * 60)
    print("DATABASE CONFIGURATION".center(60))
    print("-" * 60)
    
    print("\nYou'll need to provide MySQL/MariaDB database credentials.")
    print("These will be saved in config/credentials.json")
    
    credentials = {
        "user": input("\nDatabase username [root]: ") or "root",
        "password": getpass.getpass("Database password: "),
        "host": input("Database host [127.0.0.1]: ") or "127.0.0.1",
        "database": input("Database name [file_registry]: ") or "file_registry"
    }
    
    # Test the database connection
    try:
        print("\nTesting database connection...")
        conn = mysql.connector.connect(
            host=credentials["host"],
            user=credentials["user"],
            password=credentials["password"]
        )
        if conn.is_connected():
            print("✓ Database connection successful!")
            conn.close()
            
            # Save the credentials
            credentials_path = os.path.join(CONFIG_DIR, "credentials.json")
            with open(credentials_path, 'w') as file:
                json.dump(credentials, file, indent=4)
            print(f"✓ Credentials saved to {credentials_path}")
            
            return credentials
    except Error as e:
        print(f"✗ Database connection failed: {e}")
        retry = input("\nWould you like to try again? (y/n): ").lower()
        if retry == 'y':
            return setup_database_connection()
        else:
            print("\nYou can edit the credentials manually later in config/credentials.json")
            credentials_path = os.path.join(CONFIG_DIR, "credentials.json")
            with open(credentials_path, 'w') as file:
                json.dump(credentials, file, indent=4)
            print(f"✓ Default credentials saved to {credentials_path}")
            return credentials

def create_database(credentials):
    """Create the database if it doesn't exist and set up all required tables."""
    try:
        # Connect without database selected
        conn = mysql.connector.connect(
            host=credentials["host"],
            user=credentials["user"],
            password=credentials["password"]
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {credentials['database']}")
            print(f"✓ Database '{credentials['database']}' created or already exists.")
            
            # Switch to the database
            cursor.execute(f"USE {credentials['database']}")
            
            # Read and execute the SQL setup script
            print("\nSetting up database tables:")
            with open(DB_SETUP_FILE, 'r') as file:
                sql_script = file.read()
                
            # Split the script into individual statements
            statements = sql_script.split(';')
            
            # Execute each statement
            for statement in statements:
                statement = statement.strip()
                if statement:
                    # Extract table name from CREATE TABLE statement for feedback
                    table_match = None
                    if "CREATE TABLE" in statement.upper():
                        # Find the table name using regular expressions
                        import re
                        table_match = re.search(r'CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+([^\s(]+)', statement, re.IGNORECASE)
                    
                    try:
                        cursor.execute(statement)
                        
                        # Provide feedback about which table was created
                        if table_match:
                            table_name = table_match.group(1)
                            print(f"  - Created table: {table_name}")
                    except mysql.connector.Error as e:
                        print(f"  ! Error executing: {statement[:50]}... - {e}")
            
            conn.commit()
            print("\n✓ Database tables created successfully!")
            
            # Verify tables exist
            print("\nVerifying database tables:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                print(f"  - Found table: {table[0]}")
            
            cursor.close()
            conn.close()
            
            return True
    except mysql.connector.Error as e:
        print(f"✗ Database setup failed: {e}")
        print("\nYou can set up the database manually using the SQL commands in db_setup.sql")
        return False

def setup_excluded_files(templates):
    """Set up the excluded files configuration."""
    excluded_files = templates["excluded_files.json"]
    excluded_files_path = os.path.join(CONFIG_DIR, "excluded_files.json")
    
    with open(excluded_files_path, 'w') as file:
        json.dump(excluded_files, file, indent=4)
    
    print(f"✓ Excluded files configuration saved to {excluded_files_path}")

def setup_excluded_dirs(templates):
    """Set up the excluded directories configuration."""
    excluded_dirs = templates["excluded_dirs.json"]
    excluded_dirs_path = os.path.join(CONFIG_DIR, "excluded_dirs.json")
    
    with open(excluded_dirs_path, 'w') as file:
        json.dump(excluded_dirs, file, indent=4)
    
    print(f"✓ Excluded directories configuration saved to {excluded_dirs_path}")

def verify_setup():
    """Verify that all required files exist."""
    required_files = [
        os.path.join(CONFIG_DIR, "credentials.json"),
        os.path.join(CONFIG_DIR, "excluded_files.json"),
        os.path.join(CONFIG_DIR, "excluded_dirs.json"),
        DB_SETUP_FILE
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"✗ Missing file: {file_path}")
            all_files_exist = False
    
    if all_files_exist:
        print("\n✓ All required files have been created!")
    else:
        print("\n✗ Some required files are missing. Setup may not be complete.")

def main():
    """Main setup function that orchestrates the setup process."""
    print_banner()
    
    # Load templates
    templates = load_templates()
    
    # Create config directory
    create_config_directory()
    
    # Setup database connection
    credentials = setup_database_connection()
    
    # Ask if the user wants to set up the database now
    setup_db = input("\nWould you like to set up the database tables now? (y/n): ").lower()
    if setup_db == 'y':
        create_database(credentials)
    else:
        print("\nYou can set up the database manually later using the SQL commands in db_setup.sql")
    
    # Setup excluded files and directories
    print("\n" + "-" * 60)
    print("CONFIGURATION FILES".center(60))
    print("-" * 60)
    
    setup_excluded_files(templates)
    setup_excluded_dirs(templates)
    
    # Verify setup
    print("\n" + "-" * 60)
    print("SETUP VERIFICATION".center(60))
    print("-" * 60)
    
    verify_setup()
    
    print("\n" + "=" * 60)
    print("  SETUP COMPLETE".center(60))
    print("=" * 60)
    print("\nYour File Registry system is now configured!")
    print("You can start using it by running:")
    print("\n  python file_registry_scan.py /path/to/scan")
    print("  python file_registry_search.py \"search_term\"")
    print("  python file_registry_log.py\n")

if __name__ == "__main__":
    main()
