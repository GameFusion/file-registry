

import mysql.connector
import json

def get_database_connection():
    # Load the credentials from the JSON file
    with open('config/credentials.json') as f:
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
